# FastAPI Education

Backend онлайн-школы на FastAPI с чистой архитектурой и DI через [dishka](https://dishka.readthedocs.io/).

## Требования

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/) — менеджер зависимостей
- Redis — для очереди отправки кода
- Docker — для запуска кода студентов (нужен только для воркера проверки решений)

## Установка

Все команды выполняются из каталога `backend/`.

```bash
cd backend
uv sync
```

## Настройка окружения

Скопируйте пример конфигурации и при необходимости отредактируйте значения:

```bash
cp .env.example .env
```

Основные переменные (см. `app/infrastructure/config/settings.py`):

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `APP_ENV` | `development` | Окружение |
| `APP_TITLE` | `FastAPI Education` | Название приложения |
| `APP_DEBUG` | `true` | Режим отладки |
| `API_PREFIX` | `/api` | Префикс всех HTTP-маршрутов |
| `DATABASE_URL` | `sqlite+aiosqlite:///./fastapi_education.db` | Подключение к БД |
| `DATABASE_ECHO` | `false` | Логирование SQL |
| `JWT_SECRET_KEY` | — | Секрет для подписи JWT (обязательно поменяйте) |
| `JWT_ALGORITHM` | `HS256` | Алгоритм подписи JWT |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни access-токена |
| `REDIS_URL` | `redis://localhost:6379/0` | Подключение к Redis |
| `SUBMISSION_QUEUE_NAME` | `code-submissions` | Имя очереди отправок кода |
| `MEDIA_ROOT` | `./media` | Каталог локального хранения загруженных файлов |
| `MEDIA_URL_PREFIX` | `/media` | HTTP-префикс для отдачи загруженных файлов |
| `MAX_COVER_IMAGE_BYTES` | `5242880` | Максимальный размер обложки курса в байтах |

## Миграции базы данных

```bash
cd backend
uv run alembic upgrade head
```

Создание новой миграции:

```bash
uv run alembic revision --autogenerate -m "description"
```

## Запуск API

```bash
cd backend
uv run uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Redis и воркер проверки кода

Проверка решений студентов идёт асинхронно через Redis-очередь, поэтому для этой функциональности нужны Redis и Docker.

Запуск Redis (если не запущен локально):

```bash
docker run -d --name redis -p 6379:6379 redis:7
```

Запуск воркера (в отдельном терминале):

```bash
cd backend
uv run python -m app.run_code_submission_worker
```

Воркер использует Docker-образы `python:3.12-alpine` и `eclipse-temurin:21-jdk-jammy`; они подтянутся автоматически при первом запуске. Убедитесь, что Docker daemon запущен.

## Тесты

```bash
cd backend
uv run pytest
```

Отдельные группы:

```bash
uv run pytest tests/unit
uv run pytest tests/integration/api
uv run pytest tests/integration/e2e
```

> Интеграционные тесты используют SQLite во временном каталоге. Тестам, связанным с очередью и воркером, нужен запущенный Redis (и Docker для сценариев выполнения кода).

## Линтинг и форматирование

```bash
cd backend
uv run ruff check .
uv run ruff format .
```

Либо через pre-commit из корня репозитория:

```bash
pre-commit install
pre-commit run --all-files
```
