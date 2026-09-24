# Clean Architecture

TrafficMaster applies Clean Architecture to keep business rules independent of delivery and persistence technologies.

## Dependency Rule

Dependencies point inward:

```text
Presentation ──┐
               ├──▶ Application ──▶ Domain
Infrastructure ┘

Setup composes all layers at the application boundary.
```

The domain does not import FastAPI, SQLAlchemy, Redis, Dishka, or configuration code. The application depends on infrastructure behavior only through protocols defined under `application/common/ports/`.

## Domain Layer

The domain owns:

- entity state and transitions;
- value validation and invariants;
- domain services and domain errors;
- strongly typed identifiers;
- small ports required by pure domain behavior.

A domain object never knows how it is stored or exposed over HTTP.

## Application Layer

The application owns:

- command and query handlers;
- authorization and existence checks;
- transaction boundaries;
- gateway protocols;
- immutable views returned to outer layers.

Commands and query input dataclasses are frozen, slotted, and keyword-only. Every successful persistent mutation finishes with `TransactionManager.commit()`.

## Outer Layers

Infrastructure implements ports. Presentation adapts HTTP. Neither layer should move framework-specific objects into the application or domain.

For example, a route receives standard UUIDs and strings through a Pydantic schema, creates an application command, and converts the returned view into a response schema.

## Commands and Queries

TrafficMaster uses a CQRS-like separation without separate databases:

```text
Command → handler → domain operation → gateway → commit
Query   → handler → gateway → immutable view
```

The separation keeps mutation rules and read concerns explicit while avoiding unnecessary infrastructure.
