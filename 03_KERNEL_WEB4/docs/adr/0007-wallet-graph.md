# ADR-0007: Wallet Graph Model

## Status

Accepted

## Context

Wallet relationships need to be modeled for cluster analysis.

## Decision

Use a directed graph model with typed nodes (AJAN/MZC/MYK) and weighted edges.

## Node Types

- **AJAN** — Execution wallet (operations)
- **MZC** — Asset wallet (token holdings)
- **MYK** — Treasury wallet (reserves)

## Reasons

- Natural representation of fund flows
- Supports cluster detection algorithms
- Extensible to new wallet types
- Queryable for path analysis

## Consequences

- Graph storage needs optimization at scale
- Edge weights must be kept current
- Requires periodic recomputation for large datasets
