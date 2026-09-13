# ADR-0004: API Versioning Strategy

## Status

Accepted

## Context

API evolution must not break existing clients.

## Decision

Use **URL path versioning** (`/api/v1/`) plus **header versioning** (`X-API-Version: 1.0`).

## Reasons

- Path versioning is explicit and cacheable
- Header provides additional compatibility signal
- Simple routing at gateway level

## Consequences

- New major versions require new path prefix
- Old versions must be maintained until deprecation
