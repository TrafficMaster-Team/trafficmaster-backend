# Backend Development

TrafficMaster is organized as repetitive vertical slices across users, decks, deck configurations, cards, and card progress. When adding behavior, use an adjacent slice as the template.

## Running the Application

```bash
cp .env.dist .env
uv sync --group dev
just up
uv run alembic upgrade head
just uvicorn
```

The application factory is `trafficmaster.web:create_fastapi_app`. The `just uvicorn` command sets `PYTHONPATH=src` and starts it through Uvicorn.

## Adding a Use Case

1. Add invariants to domain entities or value objects.
2. Create an application command or query and its handler.
3. Extend an application port when infrastructure behavior is required.
4. Update every adapter, decorator, fixture, and test double implementing that port.
5. Add the FastAPI route and Pydantic schemas.
6. Register the handler in `setup/ioc.py` and the router in its route package.
7. Add exception-to-status mappings where required.
8. Cover success and failure behavior with tests.

## Database Migrations

SQLAlchemy uses classical mappings, so domain entities remain free of ORM declarations. When the schema changes, update the mapping and create a new Alembic revision:

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

Do not rewrite an existing migration that may already have been applied.

## Cache Behavior

Redis decorators implement cache-aside behavior. Reads must fall back to the wrapped PostgreSQL gateway when Redis fails. Mutations must invalidate all affected by-ID, list, count, existence, owner, and public-list keys.

## Documentation

Markdown source files live in `docs/`, and `mkdocs.yml` defines the theme and navigation.

```bash
uv run --group docs mkdocs serve
uv run --group docs mkdocs build --strict
```
