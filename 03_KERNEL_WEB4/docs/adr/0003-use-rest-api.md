# ADR-0003: Use REST API for Off-Chain Services

## Status

Accepted

## Context

Off-chain intelligence services (graph, radar, funding, risk) need an interface for clients.

## Decision

Use **REST API** with JSON responses as the primary interface. API Contract v1 is frozen.

## Reasons

- Universal client compatibility
- Simple to test and document (OpenAPI)
- Stateless request model
- Easy caching and load balancing

## Alternatives Considered

- gRPC: Higher performance but less universal
- GraphQL: More flexible but higher complexity

## Consequences

- HTTP overhead for high-frequency calls
- Need versioning strategy (solved with /api/v1/ prefix)
