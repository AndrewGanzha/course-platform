import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DockerRunResult:
    stdout: str
    stderr: str
    exit_code: int | None
    logs: str = ""


class DockerRunner:
    def __init__(self, container_workdir: str = "/workspace") -> None:
        self.container_workdir = container_workdir

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
            "--memory",
            f"{memory_limit_mb}m",
            "--cpus",
            "1",
            "-v",
            f"{bundle_dir}:{self.container_workdir}:ro",
            "-w",
            self.container_workdir,
            image,
            *command,
        ]

        process = await asyncio.create_subprocess_exec(
            *docker_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

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
