# ADR 0001: Clean Architecture

## Status
Accepted

## Context
The Fintech Analytics Platform requires a scalable structure capable of accommodating Machine Learning, robust Data Engineering, and REST API layers simultaneously without entangling them. Business logic is notoriously prone to leaking into Web Frameworks (like FastAPI or Django).

## Decision
We enforce a strict Clean Architecture. The project is split structurally by domain rather than technology:
- `src.core` (Enterprise constraints)
- `src.db` (Infrastructure/Persistence)
- `src.analytics` & `src.ml` & `src.features` (Core Domain Services)
- `src.api` (Delivery/Gateway mechanism)

## Consequences
- **Positive**: Complete decoupling allows the API to be torn out or replaced by a CLI/gRPC interface without altering the ML pipeline.
- **Negative**: There is more boilerplate passing data objects between boundaries, compared to traditional tight-coupled MVC patterns.
