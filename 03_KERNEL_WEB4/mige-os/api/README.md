# MIGE OS API

MIGE OS Evidence Compilation API - Production Grade

## Installation

```bash
pip install -r requirements.txt
```

## Development Dependencies

```bash
pip install -r requirements-dev.txt
```

## Running

```bash
# Development
python api.py

# Production with uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Endpoints

### Health & Monitoring
- `GET /` — Root endpoint
- `GET /health` — Detailed health check (git commit, build time, uptime, schema version)
- `GET /ready` — Readiness check
- `GET /live` — Liveness check
- `GET /version` — Version information (commit, tag)
- `GET /metrics` — Prometheus metrics

### Evidence Compilation
- `POST /api/v1/evidence/compile` — Compile raw data into evidence

### Registry
- `GET /api/v1/registry/handlers` — List available handlers
- `GET /api/v1/registry/blockchains` — List supported blockchains

## Features

- ✅ Correlation ID middleware for distributed tracing
- ✅ Structured JSON logging with structlog
- ✅ CORS configuration
- ✅ GZip compression
- ✅ Pydantic v2 with Field validation
- ✅ Type-safe request/response models
- ✅ Standard error response model
- ✅ OpenAPI v1 specification

## Docker

```bash
# Build
docker build -t mige-os-api .

# Run
docker-compose up

# Run standalone
docker run -p 8000:8000 mige-os-api
```

## Testing

```bash
# Run tests
pytest test_api.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Linting

```bash
# Ruff
ruff check .

# Black
black .

# MyPy
mypy api.py --ignore-missing-imports
```

## CI/CD

GitHub Actions automatically runs:
- Ruff linting
- Black formatting check
- MyPy type checking
- Pytest tests
- Smoke tests (health, ready, liveness)

## Example Usage

```bash
# Health check
curl http://localhost:8000/health

# Version
curl http://localhost:8000/version

# Compile evidence
curl -X POST http://localhost:8000/api/v1/evidence/compile \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test-123" \
  -d '{
    "raw_data": {"tx": "abc123"},
    "handler_type": "SOLANA",
    "blockchain": "SOLANA",
    "source": "rpc"
  }'
```