# ADR-0002: Use Program Derived Addresses (PDA)

## Status

Accepted

## Context

On-chain accounts need deterministic addressing for treasury, config, and vault accounts.

## Decision

Use **PDA** with canonical bumps for all program-owned accounts.

## Reasons

- Deterministic address derivation
- No private key required for program accounts
- Standardized seed patterns
- Enables cross-program invocation

## Consequences

- Seeds must be carefully managed
- Bump validation required in every instruction
- PDA collisions must be prevented through unique seeds
