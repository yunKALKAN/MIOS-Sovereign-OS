# ADR-0001: Use Anchor Framework

## Status

Accepted

## Context

We need a framework for developing Solana smart contracts. Options include raw Solana SDK, Anchor, or Seahorse.

## Decision

Use **Anchor** as the primary smart contract framework.

## Reasons

- IDL auto-generation for client SDK
- Built-in account validation and PDA management
- Strong ecosystem and community support
- TypeScript test integration
- Standardized program structure

## Consequences

- Dependency on Anchor CLI toolchain
- Slightly larger program binary size
- Team needs Anchor-specific knowledge
