# Security Guide

See [SECURITY.md](../SECURITY.md) for the security policy.

## On-Chain Security

- Authority model (single mimar)
- PDA validation with canonical bumps
- Deterministic seed patterns
- Overflow protection

## Off-Chain Security

- Input validation on all endpoints
- X-Request-ID for audit trails
- Secrets via environment variables
- Dependency scanning (Bandit, Snyk)

## Authentication Flow

```
Challenge --> Sign --> Verify --> JWT --> Session
```

## Reporting

For vulnerabilities, contact: security@mucizework.com
