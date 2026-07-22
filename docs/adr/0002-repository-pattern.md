# ADR 0002: Repository Pattern

## Status
Accepted

## Context
Directly embedding SQLAlchemy ORM queries inside business logic or REST routers makes unit testing difficult and ties the application strictly to PostgreSQL semantics.

## Decision
We implemented a Repository Pattern (`src.db.repositories`). The business layer communicates via Python objects and domain interfaces, rather than querying `db.session` natively.

## Consequences
- **Positive**: We can swap SQL engines or mock database queries in `pytest` natively without spinning up ephemeral SQL containers for every unit test.
- **Negative**: Adds a layer of indirection. Developers must map domain objects to ORM models iteratively.
