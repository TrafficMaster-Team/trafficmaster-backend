# Endpoints

TrafficMaster publishes an OpenAPI contract directly from its FastAPI routes.

During local development:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`
- OpenAPI schema: `http://localhost:8080/openapi.json`

These endpoints can be disabled in production with `EXPOSE_API_DOCS=false`.

## Service Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Service information |
| `GET` | `/healthcheck/live` | Process liveness |
| `GET` | `/healthcheck/ready` | PostgreSQL readiness and Redis status |

## API Groups

Application routes use the `/v1` prefix.

| Prefix | Operations |
| --- | --- |
| `/v1/auth` | Sign up, log in, log out, current user |
| `/v1/user` | User management, roles, profile changes, aggregate statistics |
| `/v1/deck` | Deck CRUD, public decks, user decks, copying, configuration assignment |
| `/v1/card` | Card CRUD, question, answer, deck, image, and tag changes |
| `/v1/deck-config` | Scheduling configuration and daily limits |
| `/v1/review` | Queue, review actions, progress, logs, interval previews, deck statistics |

## Authentication

Authentication is cookie-backed. A successful login creates a server-side session and returns an HttpOnly `access_token` cookie containing a signed JWT with the session identifier.

```bash
curl -i \
  -c cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"your-password"}' \
  http://localhost:8080/v1/auth/login

curl -b cookies.txt http://localhost:8080/v1/auth/me
```

## Errors

Domain and application errors are mapped to HTTP responses by a centralized exception handler. Common statuses include `400`, `401`, `403`, `404`, `409`, `422`, and `503`.

!!! note
    Swagger UI is the authoritative endpoint reference because paths, schemas, validation constraints, and documented error responses are generated from the current application code.
