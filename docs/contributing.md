# Contributing

Contributions should preserve the existing dependency direction and the conventions of the surrounding feature slice.

## Development Workflow

1. Create a branch from the latest `main`.
2. Install dependencies with `uv sync --group dev`.
3. Make a focused change using a neighboring implementation as the template.
4. Add or update tests for the changed behavior.
5. Run the relevant test module and static checks.
6. Update documentation when configuration, API behavior, or architecture changes.
7. Open a pull request with a concise explanation of the behavior and verification performed.

## Architecture Rules

- Domain code must not depend on FastAPI, SQLAlchemy, Redis, or setup code.
- Application code accesses infrastructure through protocols.
- Persistent mutations must commit through `TransactionManager`.
- Domain entities remain independent of ORM mappings.
- Cache failures fall back to the wrapped gateway.
- Secrets and local `.env` files must never be committed.

## Before Opening a Pull Request

```bash
uv run pytest tests/unit -q
uv run ruff check --no-fix .
uv run ruff format --check .
uv run mypy --config-file pyproject.toml
uv run --group docs mkdocs build --strict
```

Run integration tests when changing routes, middleware, authentication, dependency wiring, persistence, Redis behavior, or transaction boundaries.
