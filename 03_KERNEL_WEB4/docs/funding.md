# Funding Engine

## Overview

The Funding Engine analyzes wallet funding sources and traces fund flows.

## API

```
GET /api/v1/funding/{wallet}
GET /api/v1/funding
POST /api/v1/flow
```

## Sources

Currently tracked sources:
- external (direct transfers)
- CEX (centralized exchanges)
- bridge (cross-chain bridges)

## Confidence Score

Each trace includes a confidence score (0.0 - 1.0) indicating analysis reliability.
