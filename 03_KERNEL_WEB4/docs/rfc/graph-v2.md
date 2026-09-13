# RFC: Graph Engine v2

## Summary

Upgrade the graph engine to support dynamic graph construction from on-chain data.

## Motivation

Current graph is static (hardcoded AJAN/MZC/MYK). v2 should:
- Build graphs from real transaction data
- Support node/edge CRUD via API
- Enable path queries and cluster detection

## Proposed Approach

1. Transaction ingestion pipeline
2. Graph database (Neo4j or in-memory)
3. Path query API endpoints
4. Periodic graph recomputation

## Open Questions

- In-memory vs external graph database?
- Maximum graph size?
- Historical graph snapshots?

## Status

Draft
