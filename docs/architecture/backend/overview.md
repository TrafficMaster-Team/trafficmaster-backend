# Architecture Overview

TrafficMaster uses a layered architecture with dependencies directed toward the domain. Frameworks and storage technologies are implementation details around the application core.

## Project Structure

```text
src/trafficmaster/
├── domain/          # Entities, value objects, services, domain errors
├── application/     # Commands, queries, handlers, ports, views
├── infrastructure/  # PostgreSQL, Redis, JWT, hashing, transactions
├── presentation/    # FastAPI routes, schemas, middleware
└── setup/           # Configuration and dependency composition
```

## Request Flow

A typical write request passes through the following components:

```text
HTTP request
    ↓
FastAPI route and Pydantic schema
    ↓
Application command handler
    ↓
Domain entity or service
    ↓
Gateway and transaction ports
    ↓
SQLAlchemy adapters and PostgreSQL
```

Queries follow a shorter path and return immutable application view dataclasses rather than ORM or Pydantic objects.

## Core Components

### Domain

The domain contains users, decks, deck configurations, cards, card progress, and review logs. Value objects validate individual values, while entities and domain services protect state transitions and business invariants.

### Application

The application layer coordinates use cases. Commands mutate state and commit through `TransactionManager`; queries read data through gateway protocols. Authorization, existence checks, and sequencing belong here.

### Infrastructure

Infrastructure implements the application ports with SQLAlchemy, PostgreSQL, Redis, JWT, bcrypt, UUID generators, and UTC clocks.

### Presentation

Presentation translates HTTP requests into application data structures and converts application views into response schemas. It also owns middleware and exception-to-status mappings.

### Setup

The setup package is the composition root. It registers routes, exception handlers, middleware, ORM mappings, configuration, and Dishka providers.

## Data Flow

PostgreSQL is the source of truth. Redis is an optional cache-aside layer: read failures fall back to PostgreSQL, and mutations invalidate cached representations that may become stale.
