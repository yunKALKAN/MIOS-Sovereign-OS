# Deployment Guide

## Environments

```
Development
    |
  Devnet
    |
  Testnet
    |
  Mainnet
```

## Local Development

### Prerequisites

- Python 3.10+
- pip
- Rust (for Anchor/Solana)
- Node.js 18+

### Setup

```bash
git clone https://github.com/yunKALKAN/web4-engine.git
cd web4-engine
pip install -r requirements.txt
```

### Run API

```bash
python api/api.py
# API available at http://127.0.0.1:5002/api/v1/health
```

### Run WEB4 Auth

```bash
pip install flask pyjwt pynacl base58
python web4_full/engine/app.py
# Auth available at http://127.0.0.1:5080/status
```

### Run Tests

```bash
python tests/test_api_v1.py
```

## Docker (Planned)

```bash
docker-compose up -d
```

```yaml
# docker/docker-compose.yml
services:
  api-gateway:
    build: docker/Dockerfile.api
    ports: ["5002:5002"]
  graph-service:
    build: docker/Dockerfile.graph
  radar-service:
    build: docker/Dockerfile.radar
```

## Kubernetes (Planned)

```bash
helm install web4-engine infra/helm/web4-engine
```

## Infrastructure

```
Internet
    |
  NGINX
    |
  API Gateway
    |
  Redis (cache)
    |
  PostgreSQL (planned)
    |
  Solana RPC
    |
  Anchor Program
```

## Monitoring (Planned)

| Tool       | Purpose         |
|------------|-----------------|
| Prometheus | Metrics         |
| Grafana    | Dashboards      |
| Loki       | Log aggregation |
| Tempo      | Distributed tracing |
| Jaeger     | Trace visualization |

## Release Process

```
feature/*
    |
  develop
    |
  release/*
    |
  main
    |
  GitHub Release
    |
  Docker Image
    |
  Deploy
```
