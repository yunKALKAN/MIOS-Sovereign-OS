# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it responsibly.

**Do not open a public issue.**

Contact: security@mucizework.com

## Security Checklist

- [x] Input Validation
- [x] Signature Verification (ED25519)
- [x] Rate Limiting (planned)
- [ ] Authentication (JWT)
- [ ] Authorization (RBAC)
- [x] Audit Logging (X-Request-ID)
- [x] Secrets Management
- [ ] Dependency Scanning
- [ ] Static Analysis
- [ ] Supply Chain Verification

## Signature Verification

- `/api/v1/hash/sha256` — SHA-256 data digest generation
- `/api/v1/sign/verify` — Signature verification against wallet+message

## Authority Model

Smart contract uses a single `authority` (mimar) for administrative operations.

## PDA Validation

Program Derived Addresses (PDA) are validated with canonical bumps.

## Seed Validation

All PDA seeds are deterministic and documented.

## Input Validation

- All POST endpoints validate required fields
- Missing fields return `422 VALIDATION_FAILED`
- Empty/malformed bodies return `400 INVALID_REQUEST`

## Rate Limiting

Planned for Sprint-03. Will use token bucket algorithm.

## Audit Logging

Every request is tagged with `X-Request-ID` for full audit trail:

- API log
- Audit log
- On-chain transaction
- Build log

## Secrets Management

- No secrets in source code
- Environment variables for sensitive configuration
- `.env` files excluded from version control

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |
