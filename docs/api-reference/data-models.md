# Data Models

TrafficMaster separates domain entities, application views, HTTP schemas, and persistence mappings. They represent related data but serve different boundaries.

## User

A user has a strongly typed identifier, email, name, hashed password, activation state, and role. Users own decks and deck configurations.

## Deck

A deck groups cards and references a scheduling configuration. It has a title, optional description, owner, and public/private state. Public decks can be discovered and copied by other users.

## Deck Configuration

A deck configuration defines learning behavior:

- daily limits;
- new-card settings;
- lapse behavior;
- advanced scheduling settings.

Configurations belong to users and can be assigned to their decks.

## Card

A card belongs to a deck and contains a question, answer, optional image path, and tags.

## Card Progress

Progress is stored per user and card. The main states are:

- `new`
- `learning`
- `review`
- `relearning`

A review rating moves the progress through its state machine and determines the next due time and interval.

## Review Log

Each completed review creates an immutable history record. Logs support per-card and per-user history queries and make scheduling changes auditable.

## Relationships

```text
User 1 ── * Deck 1 ── * Card
  │           │
  │           └── 1 DeckConfig
  │
  └── * CardProgress * ── 1 Card
             │
             └── * ReviewLog
```

Exact request and response representations are available in the generated [API documentation](endpoints.md).
