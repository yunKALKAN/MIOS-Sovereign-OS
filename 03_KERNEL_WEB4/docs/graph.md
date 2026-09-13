# Graph Engine

## Overview

The Graph Engine manages wallet relationship graphs with typed nodes and weighted edges.

## Node Types

| Type | Role | Description |
|------|------|-------------|
| AJAN | execution | Operational wallet |
| MZC | asset | Token holdings |
| MYK | treasury | Reserve management |

## API

```
GET /api/v1/graph
```

Returns all nodes and edges in the wallet cluster graph.

## Future (v2)

- Dynamic graph construction from on-chain data
- Path query endpoints
- Cluster detection algorithms
