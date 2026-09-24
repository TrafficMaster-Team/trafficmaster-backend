# Production runbook

This runbook covers a safe API release. To publish the documentation site itself, use `uv run --group docs mkdocs gh-deploy`.

## Required configuration

Store production values in the platform secret/configuration service. Do not copy `.env.dist` into production.

The application refuses to start with an unsafe production configuration when `APP_ENV=production`. At minimum set:

```dotenv
APP_ENV=production
FASTAPI_DEBUG=false
SECURE=true
COOKIE_SAME_SITE=strict
JWT_SECRET=<at-least-32-random-characters>
PEPPER=<at-least-32-random-characters>
CORS_ALLOWED_ORIGINS=https://app.example.com
TRUSTED_HOSTS=api.example.com
EXPOSE_API_DOCS=false
```

Also provide PostgreSQL and Redis connection settings from `.env.dist`. Size `DB_POOL_SIZE` and `DB_POOL_MAX_OVERFLOW` against the database connection limit across every worker and replica. Redis is treated as optional cache infrastructure: its failure degrades readiness metadata but does not make the application unready.

TLS termination, HSTS and request-size limits belong at the trusted ingress. Configure proxy-header trust only for known proxy addresses. Rate-limit login and signup at the ingress until distributed application-level limits are implemented.

## Release sequence

1. Verify CI on the exact commit and publish an immutable image digest.
2. Confirm a recent PostgreSQL backup and a tested restore path.
3. Run `alembic upgrade head` as a one-off job using the release image.
4. Roll out one canary instance.
5. Verify `/healthcheck/live`, `/healthcheck/ready`, login, and one representative read/write flow.
6. Roll out the remaining instances while monitoring 5xx rate, latency, database connections, and readiness.
7. Record the image digest and migration revision in the release log.

## Rollback

Roll back the application image first. Do not automatically downgrade the database. Alembic downgrade is allowed only after confirming that the downgrade is data-safe and that no newer application instance remains active.

If PostgreSQL is unavailable, remove instances from service and restore/fail over according to the database provider runbook. If Redis is unavailable, keep serving from PostgreSQL, investigate the cache separately, and monitor database load.

## Operational checks

- Alert on sustained readiness failures, 5xx responses, latency, pool exhaustion, and database saturation.
- Centralize application and ingress logs; unknown 5xx responses include method and path with a traceback server-side.
- Exercise backup restoration and rollback in staging before the first production release.
- Decide and document retention, point-in-time recovery, SLOs, on-call ownership, and incident escalation outside this repository.
