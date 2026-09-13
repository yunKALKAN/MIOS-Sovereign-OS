# RFC: Wallet Clustering

## Summary

Define the algorithm and data model for grouping wallets into clusters based on transaction patterns.

## Motivation

Identifying related wallets enables:
- Smart money tracking
- Risk assessment
- Fund flow analysis

## Proposed Approach

1. Build transaction graph from on-chain data
2. Apply community detection algorithms
3. Classify clusters by behavior (execution, asset, treasury)
4. Assign confidence scores

## Open Questions

- Which clustering algorithm? (Louvain, Label Propagation, etc.)
- How to handle cross-chain wallets?
- Update frequency?

## Status

Draft
