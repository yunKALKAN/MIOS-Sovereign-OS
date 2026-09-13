# Radar Engine

## Overview

The Radar Engine detects smart money signals from fund flow analysis.

## Signals

| Signal | Description |
|--------|-------------|
| ACCUMULATION | Net inflow exceeds threshold |
| DISTRIBUTION | Net outflow exceeds threshold |
| NEUTRAL | Balanced flow |

## API

```
GET /api/v1/radar
```

## Metrics

- smart_money_inflow
- outflow
- net (inflow - outflow)
- signal
- timestamp
