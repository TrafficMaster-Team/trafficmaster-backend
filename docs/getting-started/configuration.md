# Configuration

TrafficMaster is configured through environment variables. Copy `.env.dist` to `.env` for local development:

```bash
cp .env.dist .env
```

!!! warning
    `.env.dist` contains development placeholders. Do not use them in production and never commit `.env`.

## Application

| Variable | Description | Development value |
| --- | --- | --- |
| `APP_ENV` | Application environment | `development` |
| `UVICORN_HOST` | Server bind address | `0.0.0.0` |
| `UVICORN_PORT` | HTTP port | `8080` |
| `FASTAPI_DEBUG` | FastAPI debug mode | `True` |
| `EXPOSE_API_DOCS` | Expose Swagger, ReDoc, and OpenAPI | `True` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins | `http://localhost:3000` |
| `TRUSTED_HOSTS` | Comma-separated Host allowlist | `localhost,127.0.0.1` |
| `HEALTHCHECK_TIMEOUT_SECONDS` | Dependency check timeout | `2` |

## PostgreSQL

The connection is assembled from `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, and `POSTGRES_DRIVER`.

SQLAlchemy pool behavior is controlled with:

- `DB_POOL_SIZE`
- `DB_POOL_MAX_OVERFLOW`
- `DB_POOL_RECYCLE`
- `DB_POOL_PRE_PING`
- `DB_ECHO`
- `DB_AUTO_FLUSH`
- `DB_EXPIRE_ON_COMMIT`

## Redis

Redis uses `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_CACHE_DB`, and `REDIS_MAX_CONNECTIONS`.

Redis is an optional cache. Cache failures fall back to PostgreSQL, while the readiness response reports the degraded state.

## Authentication

| Variable | Description |
| --- | --- |
| `JWT_SECRET` | JWT signing secret |
| `JWT_ALGORITHM` | Signing algorithm |
| `PEPPER` | Server-side password pepper |
| `SESSION_TTL_MIN` | Session lifetime in minutes |
| `SESSION_REFRESH_THRESHOLD` | Fraction of TTL used to refresh a session |
| `SECURE` | Restrict the auth cookie to HTTPS |
| `COOKIE_SAME_SITE` | Cookie SameSite policy |

## Production Validation

When `APP_ENV=production`, the application rejects unsafe settings. Production requires HTTPS origins, explicit trusted hosts, secure cookies, disabled debug mode, and non-placeholder secrets of at least 32 characters.

See the [Production](../production.md) runbook for deployment guidance.
