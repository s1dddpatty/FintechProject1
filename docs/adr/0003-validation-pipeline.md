# ADR 0003: Validation Pipeline

## Status
Accepted

## Context
Data traversing the ingestion layer is highly unstructured and volatile. Validating this manually across business endpoints causes duplicated validation logic.

## Decision
We enforce a decoupled Validation Engine inside `src.pipelines.validation`. It is exclusively responsible for Data Schema assertions and strict logical Business Rules before the data is allowed into the Persistence or Feature Engine layers.

## Consequences
- **Positive**: Assures 100% predictable inputs downstream (for training and database ORM mapping).
- **Negative**: Rejected records are currently dropped completely. Future iterations must handle partial pipeline progression.
