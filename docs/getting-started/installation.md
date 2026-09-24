# Installation

This guide explains how to run TrafficMaster locally for development.

## Prerequisites

- Python 3.12 or newer
- uv 0.9.26
- Docker with Docker Compose
- just command runner
- Git

Check the installed tools:

```bash
python3 --version
uv --version
docker compose version
just --version
```

!!! note
    You do not need to activate `.venv` before running `uv`. The project pins uv to version `0.9.26` in `pyproject.toml`.

## Clone the Repository

```bash
git clone git@github.com:TrafficMaster-Team/trafficmaster-backend.git
cd trafficmaster-backend
```

## Install Dependencies

Create the local configuration and synchronize the development environment:

```bash
cp .env.dist .env
uv sync --group dev
```

Replace the development values of `JWT_SECRET` and `PEPPER` in `.env`. Never commit this file.

## Start Infrastructure

Start PostgreSQL and Redis:

```bash
just up
```

Apply database migrations:

```bash
uv run alembic upgrade head
```

## Run the API

```bash
just uvicorn
```

The API is available at `http://localhost:8080`. Interactive API documentation is available at `http://localhost:8080/docs`.

Verify the service:

```bash
curl http://localhost:8080/healthcheck/live
curl http://localhost:8080/healthcheck/ready
```

## Run the Documentation

```bash
uv sync --group docs
uv run --group docs mkdocs serve
```

Open `http://127.0.0.1:8000` in a browser. MkDocs rebuilds the site whenever a Markdown file changes.
