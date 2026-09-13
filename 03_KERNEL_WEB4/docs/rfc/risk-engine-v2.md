# RFC: Risk Engine v2

## Summary

Design a composable risk scoring engine that aggregates signals from multiple sources.

## Motivation

Risk assessment requires combining:
- Graph topology (cluster proximity to known risky wallets)
- Funding sources (CEX, bridge, mixer)
- Radar signals (unusual flow patterns)
- On-chain behavior (transaction frequency, amounts)

## Proposed Approach

1. Define risk factors as independent scorers
2. Each factor produces a normalized score (0.0 - 1.0)
3. Weighted aggregation into composite risk score
4. Configurable factor weights per use case

## Risk Factors

- Source risk (funding origin)
- Behavioral risk (transaction patterns)
- Network risk (graph proximity)
- Temporal risk (activity timing)

## Open Questions

- Factor weight optimization?
- Score update frequency?
- Threshold for alerts?

## Status

Draft
