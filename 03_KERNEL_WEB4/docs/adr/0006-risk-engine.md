# ADR-0006: Risk Engine as Independent Module

## Status

Proposed

## Context

Wallet risk scoring needs to combine signals from graph, radar, and funding engines.

## Decision

Implement Risk Engine as an independent module that consumes events from other engines.

## Reasons

- Decoupled from data source engines
- Can evolve independently
- Event-driven updates
- Composable risk factors

## Consequences

- Requires event bus infrastructure
- Eventually consistent risk scores
- Additional operational complexity
