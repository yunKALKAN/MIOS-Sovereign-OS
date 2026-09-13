# API Reference

## Base URL

```
http://127.0.0.1:5002/api/v1
```

## Endpoints

### GET /api/v1/health

System health with subsystem status.

**Response:**

```json
{
  "status": "online",
  "engine": "WEB4_BLACK_MUCIZEWORK",
  "version": "1.0",
  "subsystems": {
    "graph_engine": { "status": "ok", "nodes": 3 },
    "radar_engine": { "status": "ok" },
    "funding_engine": { "status": "ok" },
    "signature_engine": { "status": "ok" },
    "database": { "status": "ok" }
  },
  "timestamp": 1719000000.0
}
```

### GET /api/v1/graph

Wallet cluster graph (nodes + edges).

**Response:**

```json
{
  "nodes": {
    "AJAN": { "role": "execution", "balance": 0 },
    "MZC": { "role": "asset", "balance": 162.99 },
    "MYK": { "role": "treasury", "balance": 12025.88 }
  },
  "edges": [
    { "from": "external", "to": "MZC", "amount": 162.99 },
    { "from": "MZC", "to": "MYK", "amount": 162.99 }
  ]
}
```

### GET /api/v1/radar

Smart money signal scan.

**Response:**

```json
{
  "smart_money_inflow": 1245000,
  "outflow": 532000,
  "net": 713000,
  "signal": "ACCUMULATION",
  "timestamp": 1719000000.0
}
```

### GET /api/v1/funding/{wallet}

Per-wallet funding trace analysis.

**Parameters:**

| Name   | In   | Required | Type   |
|--------|------|----------|--------|
| wallet | path | yes      | string |

**Response:**

```json
{
  "wallet": "MZC",
  "sources": ["external", "CEX", "bridge"],
  "flows": [
    { "from": "external", "to": "MZC", "amount": 162.99 }
  ],
  "confidence": 0.87,
  "timestamp": 1719000000.0
}
```

### POST /api/v1/flow

Record a fund flow.

**Request Body:**

```json
{
  "from": "wallet_a",
  "to": "wallet_b",
  "amount": 100.0
}
```

**Response (200):**

```json
{
  "status": "flow_added",
  "data": { "from": "wallet_a", "to": "wallet_b", "amount": 100.0 },
  "request_id": "abc123"
}
```

**Error (422):**

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "status": 422,
    "message": "Eksik alanlar: to, amount",
    "request_id": "abc123"
  }
}
```

### POST /api/v1/hash/sha256

Generate SHA-256 digest.

**Request Body:**

```json
{
  "input": "hello world"
}
```

**Response:**

```json
{
  "hash": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
  "algorithm": "sha256",
  "input_length": 11
}
```

### POST /api/v1/sign/verify

Verify a signature.

**Request Body:**

```json
{
  "wallet": "AJAN",
  "message": "test message",
  "signature": "sig_value"
}
```

**Response:**

```json
{
  "valid": false,
  "hash": "a1b2c3d4e5",
  "wallet": "AJAN"
}
```

## Headers

All responses include:

| Header         | Value                          |
|----------------|--------------------------------|
| X-Request-ID   | Echoed from request or auto-generated UUID |
| X-API-Version  | 1.0                            |

## Error Codes

| HTTP | Code              | Description          |
|------|-------------------|----------------------|
| 400  | INVALID_REQUEST   | Malformed request    |
| 401  | UNAUTHORIZED      | Auth failed          |
| 403  | FORBIDDEN         | No permission        |
| 404  | NOT_FOUND         | Resource not found   |
| 409  | CONFLICT          | State conflict       |
| 422  | VALIDATION_FAILED | Business rule error  |
| 429  | RATE_LIMITED       | Rate limit exceeded  |
| 500  | INTERNAL_ERROR    | Server error         |

## OpenAPI Spec

Full OpenAPI 3.0.3 specification: [`api/openapi.yaml`](api/openapi.yaml)
