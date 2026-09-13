# ADR-0005: Separate Hash and Signature Verification

## Status

Accepted

## Context

The API needs both data hashing and signature verification capabilities.

## Decision

Separate into two independent endpoints:

- `/api/v1/hash/sha256` — pure data digest
- `/api/v1/sign/verify` — signature verification

## Reasons

- Single responsibility per endpoint
- Hash can be used independently of signatures
- Clearer API semantics
- Easier testing and documentation

## Consequences

- Two endpoints instead of one
- Clients must call the correct endpoint for their use case
