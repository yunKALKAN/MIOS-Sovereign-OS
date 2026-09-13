# Architecture Guide

See [ARCHITECTURE.md](../ARCHITECTURE.md) for the platform architecture overview.

## Service Layer

```
apps/api/main.py       FastAPI gateway (port 5002)
services/graph/        Graph engine
services/radar/        Radar engine
services/funding/      Funding engine
services/signature/    Signature engine
```

## Package Layer

```
packages/models/       Pydantic models (envelope, requests)
packages/shared/       Config, logger, utilities
```

## Data Flow

```
Request --> Middleware (X-Request-ID, X-Trace-ID) --> Route --> Service --> Response (Envelope)
```
