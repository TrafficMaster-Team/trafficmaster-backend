# Testing

TrafficMaster uses Pytest for domain, application, infrastructure, presentation, and integration tests.

## Unit Tests

Run the narrowest relevant test module first:

```bash
uv run pytest tests/unit/domain/card -q
uv run pytest tests/unit/application/commands/card -q
```

Run the complete unit suite:

```bash
uv run pytest tests/unit -q
```

Tests reuse valid entities and value objects from `tests/unit/factories/`. Application tests use shared mocks from `tests/unit/application/conftest.py`.

## Integration Tests

Integration tests exercise the assembled ASGI application and use Testcontainers for PostgreSQL and Redis:

```bash
uv run pytest tests/integration -q
```

A working Docker daemon is required.

## Static Checks

```bash
uv run ruff check --no-fix .
uv run ruff format --check .
uv run mypy --config-file pyproject.toml
```

`just lint` changes files because Ruff fix mode is enabled. Use the commands above when you only want to check the working tree.

## Coverage Expectations

Handler tests should protect successful interactions, missing dependencies, permission denial, and commit/non-commit behavior. Domain tests should cover invariant boundaries and state transitions. Scheduling changes require state/rating matrix coverage with explicit time and interval assertions.

## Continuous Integration

The GitHub Actions workflow verifies formatting, linting, typing, tests, Python package creation, and the production container build on pull requests and pushes to `main`.
