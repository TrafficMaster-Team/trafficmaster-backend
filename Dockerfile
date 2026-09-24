FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable

COPY alembic.ini ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable


FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN groupadd --system --gid 10001 trafficmaster \
    && useradd --system --uid 10001 --gid trafficmaster --home-dir /nonexistent --shell /usr/sbin/nologin trafficmaster

WORKDIR /app
COPY --from=builder --chown=trafficmaster:trafficmaster /app /app

USER trafficmaster
EXPOSE 8080

CMD ["uvicorn", "trafficmaster.web:create_fastapi_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
