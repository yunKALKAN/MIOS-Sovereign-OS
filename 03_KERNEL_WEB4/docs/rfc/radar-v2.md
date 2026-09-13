# RFC: Radar Engine v2

## Summary

Enhance the radar engine with real-time signal detection and multi-source data aggregation.

## Motivation

Current radar returns static signals. v2 should:
- Ingest live blockchain data
- Detect accumulation/distribution patterns in real-time
- Support configurable thresholds

## Proposed Approach

1. Stream transaction data from RPC
2. Apply sliding window analysis
3. Generate typed signals (ACCUMULATION, DISTRIBUTION, NEUTRAL)
4. Publish events for downstream consumers

## Open Questions

- WebSocket vs polling for data ingestion?
- Signal persistence and TTL?
- Alert notification channels?

## Status

Draft
