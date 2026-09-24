# Dependency Injection

TrafficMaster uses [Dishka](https://dishka.readthedocs.io/) to connect application protocols to infrastructure implementations.

## Composition Root

Dependency wiring lives in `src/trafficmaster/setup/`. The `create_fastapi_app()` factory:

1. loads and validates configuration;
2. registers imperative SQLAlchemy mappings;
3. creates the Dishka container;
4. registers exception handlers, routes, and middleware;
5. connects the container to FastAPI.

```python
container = make_async_container(*setup_providers(), context=context)
setup_dishka(container, app)
```

Configuration values are placed in the container context. Providers create database sessions, gateways, cache decorators, authentication services, and application handlers.

## Handler Injection

HTTP handlers request an application interactor with `FromDishka`:

```python
async def create_deck(
    request: CreateDeckRequestSchema,
    interactor: FromDishka[CreateDeckCommandHandler],
) -> CreateDeckResponseSchema:
    ...
```

The route depends on the use-case handler, not on SQLAlchemy sessions or Redis clients.

## Provider Boundaries

Providers are grouped by responsibility:

- persistence and transaction management;
- caching;
- authentication and security;
- application commands and queries;
- shared utilities such as clocks and ID generators.

When a new handler or adapter is introduced, register it in `src/trafficmaster/setup/ioc.py`. Keep service construction out of routes and domain objects.

## Resource Lifetime

Dishka controls component scopes. The FastAPI lifespan closes the asynchronous container when the application stops, releasing pools and other managed resources.
