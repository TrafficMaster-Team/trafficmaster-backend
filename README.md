# TrafficMaster

TrafficMaster is an asynchronous FastAPI backend for learning traffic rules with an Anki-style spaced-repetition system. It uses PostgreSQL as the source of truth, Redis as an optional cache, SQLAlchemy, Alembic, and cookie-backed authentication sessions.

## Local development

Requirements: Python 3.12+, uv 0.9.26, Docker, and Docker Compose.

```bash
cp .env.dist .env
uv sync --group dev
just up
.venv/bin/alembic upgrade head
just uvicorn
```

The API is available on `http://localhost:8080`. Health endpoints:

- `GET /healthcheck/live` — process liveness;
- `GET /healthcheck/ready` — PostgreSQL readiness and Redis degradation state.

## Verification

```bash
.venv/bin/pytest tests/unit -q
.venv/bin/pytest tests/integration -q
.venv/bin/ruff check --no-fix .
.venv/bin/ruff format --check .
.venv/bin/mypy --config-file pyproject.toml
```

Integration tests use testcontainers and require access to a Docker daemon.

## Production

Build the image with `docker build -t trafficmaster .`. Apply migrations as a separate release step before rolling out the application:

```bash
docker run --rm --env-file /secure/path/trafficmaster.env trafficmaster \
  alembic upgrade head
```

See [docs/production.md](docs/production.md) for required configuration and the rollout/rollback checklist. Never use `.env.dist` as production configuration.
