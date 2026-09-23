import asyncio
from dataclasses import dataclass
from pathlib import Path

from app.application.exceptions import RetryableExecutionError


@dataclass(slots=True)
class DockerRunResult:
    stdout: str
    stderr: str
    exit_code: int | None
    logs: str = ""


@dataclass(slots=True)
class DockerRunConfig:
    container_workdir: str = "/workspace"
    cpus: str = "1"
    tmpfs_size_mb: int = 64
    pids_limit: int = 64


class DockerRunner:
    def __init__(self, config: DockerRunConfig) -> None:
        self.config = config

    async def run(
        self,
        image: str,
        bundle_dir: Path,
        command: list[str],
        time_limit_seconds: int,
        memory_limit_mb: int,
    ) -> DockerRunResult:
        docker_command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--tmpfs",
            f"/tmp:size={self.config.tmpfs_size_mb}m",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(self.config.pids_limit),
            "--memory",
            f"{memory_limit_mb}m",
            "--cpus",
            self.config.cpus,
            "-v",
            f"{bundle_dir}:{self.config.container_workdir}:ro",
            "-w",
            self.config.container_workdir,
            image,
            *command,
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *docker_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise RetryableExecutionError("Docker executable not found.") from exc
        except OSError as exc:
            raise RetryableExecutionError(
                "Docker process could not be started."
            ) from exc

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=time_limit_seconds,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            return DockerRunResult(
                stdout="",
                stderr="Execution timed out.",
                exit_code=None,
                logs="Docker process killed by timeout.",
            )

        return DockerRunResult(
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
            exit_code=process.returncode,
            logs="",
        )
