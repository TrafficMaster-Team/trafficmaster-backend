# Testing

TrafficMaster uses Pytest for domain, application, infrastructure, presentation, and integration tests.

## Unit Tests

Run the narrowest relevant test module first:

```bash
uv run pytest tests/unit/domain/card -q --no-cov
uv run pytest tests/unit/application/commands/card -q --no-cov
```

Run the complete unit suite:

```bash
uv run pytest tests/unit -q --no-cov
```

Tests reuse valid entities and value objects from `tests/unit/factories/`. Application tests use shared mocks from `tests/unit/application/conftest.py`.

## Integration Tests

Integration tests exercise the assembled ASGI application and use Testcontainers for PostgreSQL and Redis:

```bash
uv run pytest tests/integration -q --no-cov
```

A working Docker daemon is required.

The application currently has no outgoing HTTP integrations with external services. PostgreSQL and Redis use their native protocols and are tested with real containers. `ASGITransport` sends requests to the application under test; it does not stub an external service. Consequently, external HTTP request stubs are not applicable to the current implementation. If an outgoing HTTP integration is added, its integration tests must stub the HTTP transport and cover successful responses, errors, and timeouts.

## Static Checks

```bash
uv run ruff check --no-fix .
uv run ruff format --check .
uv run mypy --config-file pyproject.toml
```

`just lint` changes files because Ruff fix mode is enabled. Use the commands above when you only want to check the working tree.

## Coverage Expectations

Run the complete suite with coverage:

```bash
uv run pytest tests/ -q
```

Pytest-cov measures application code, including branches, and fails the run below 70%. Configuration modules and Alembic migrations are excluded in `pyproject.toml`; no separate generated application code is present. Test factories are outside the measured source directory. Focused test commands use `--no-cov` because the threshold applies to the complete suite.

To export reports for submission:

```bash
uv run pytest tests/ -q --cov-report=term-missing --cov-report=html --cov-report=xml
```

See the [laboratory 2 verification report](../lab2-verification.md) for the requirement mapping and measured results.

Handler tests should protect successful interactions, missing dependencies, permission denial, and commit/non-commit behavior. Domain tests should cover invariant boundaries and state transitions. Scheduling changes require state/rating matrix coverage with explicit time and interval assertions.

## Continuous Integration

The GitHub Actions workflow verifies formatting, linting, typing, tests, Python package creation, and the production container build on pull requests and pushes to `main`.
