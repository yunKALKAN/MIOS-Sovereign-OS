# WEB4 Engine

> Next-generation Web4 Blockchain Intelligence Engine for the MucizeWork ecosystem.

![Status](https://img.shields.io/badge/status-active-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Solana](https://img.shields.io/badge/Solana-Anchor-9945FF)
![API](https://img.shields.io/badge/API-v1-orange)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)
![Rust](https://img.shields.io/badge/Rust-stable-orange)

---

## Overview

WEB4 Engine is a modular blockchain intelligence platform designed to provide analytics, graph exploration, funding analysis, monitoring, and cryptographic verification services.

The project is designed with a service-oriented architecture to integrate smart contracts, blockchain data, and intelligent analysis engines.

---

## Platform Architecture

```
                          WEB4 ENGINE

                  +---------------------+
                  |   Developer Portal  |
                  +----------+----------+
                             |
        +--------------------+--------------------+
        |                    |                    |
     REST API             SDK Layer           CLI Layer
        |                    |                    |
        +--------------------+--------------------+
                             |
                   Intelligence Platform
                             |
      +---------------+---------------+---------------+
      |               |               |               |
  Graph Engine    Radar Engine   Funding Engine  Risk Engine
      |               |               |               |
      +---------------+-------+-------+---------------+
                              |
                    Blockchain Abstraction
                              |
      +-----------------------+------------------------+
      |                       |                        |
   Solana                 Ethereum               Future Chains
                              |
                       Smart Contracts
```

---

## API Contract v1 (Frozen)

```
GET    /api/v1/health            System health + subsystem status
GET    /api/v1/graph             Wallet cluster graph
GET    /api/v1/radar             Smart money signals
GET    /api/v1/funding/{wallet}  Per-wallet funding trace

POST   /api/v1/flow              Record fund flow
POST   /api/v1/hash/sha256       SHA-256 digest
POST   /api/v1/sign/verify       Signature verification
```

**Enterprise Standards:**

- `X-Request-ID` — Request correlation
- `X-Trace-ID` — Distributed tracing
- `X-API-Version` — Version header (1.0)
- Standardized error envelope
- Response envelope: `{ success, request_id, trace_id, timestamp, data }`

**Auto-generated docs:** `/docs` (Swagger) | `/redoc` (ReDoc)

---

## Project Structure

```
web4-engine/
+-- apps/api/              FastAPI gateway (port 5002)
+-- services/              Engine implementations
|   +-- graph/             Wallet graph engine
|   +-- radar/             Smart money radar
|   +-- funding/           Funding trace engine
|   +-- signature/         Hash + signature verification
+-- packages/              Shared libraries
|   +-- models/            Pydantic models, envelope
|   +-- shared/            Config, logger, utilities
+-- programs/              Solana Anchor programs
+-- legacy/                Flask legacy code (reference)
+-- tests/                 Integration tests
+-- docs/                  Documentation
|   +-- adr/               Architecture Decision Records
|   +-- rfc/               Request for Comments
|   +-- diagrams/          Architecture diagrams
+-- docker/                Container configuration
+-- configs/               Environment configs (YAML)
+-- plugins/               Data provider plugins
+-- sdk/                   Client SDKs
+-- cli/                   Command-line interface
+-- infra/                 Infrastructure (k8s, helm, terraform)
+-- .github/               CI/CD, templates, labels
```

---

## Quick Start

```bash
git clone https://github.com/yunKALKAN/web4-engine.git
cd web4-engine
pip install -r requirements.txt
uvicorn apps.api.main:app --port 5002
```

Visit http://127.0.0.1:5002/docs for Swagger UI.

---

## Development

```bash
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Lint
ruff check .
black --check .

# Security scan
bandit -r apps/ services/ packages/ -ll
```

---

## Docker

```bash
docker build -f docker/Dockerfile -t web4-engine .
docker run -p 5002:5002 web4-engine
```

---

## Development Roadmap

### Sprint-01 — Smart Contract
- [x] Anchor Build, IDL, Tests

### Sprint-02 — REST API + Platform
- [x] API Contract v1 (Frozen)
- [x] FastAPI migration
- [x] Enterprise standards (X-Request-ID, X-Trace-ID, envelope)
- [x] Docker + CI/CD
- [x] 23 integration tests
- [x] Documentation suite

### Sprint-03 — Intelligence Engine
- [ ] Graph Engine v2
- [ ] Radar Engine v2
- [ ] Funding Engine v2
- [ ] Risk Engine

### Sprint-04 — Dashboard
- [ ] React Admin Panel

### Sprint-05 — Production
- [ ] Kubernetes, monitoring, v1.0.0

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Platform architecture |
| [API.md](API.md) | API reference |
| [ENGINEERING_CONSTITUTION.md](ENGINEERING_CONSTITUTION.md) | Engineering principles |
| [ROADMAP.md](ROADMAP.md) | Development roadmap |
| [SECURITY.md](SECURITY.md) | Security policy |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [docs/adr/](docs/adr/) | Architecture Decision Records |
| [docs/rfc/](docs/rfc/) | Request for Comments |
| [ORGANIZATION.md](ORGANIZATION.md) | Platform organizational structure |

---

## Technology Stack

- **Backend:** Python, FastAPI, Pydantic v2, Uvicorn
- **Blockchain:** Rust, Anchor, Solana
- **Frontend:** TypeScript, Node.js, React (planned)
- **Infrastructure:** Docker, GitHub Actions, Kubernetes (planned)
- **Security:** SHA-256, Ed25519, JWT
- **Observability:** Structured JSON logging, request tracing

---

## Engineering Principles

> See [ENGINEERING_CONSTITUTION.md](ENGINEERING_CONSTITUTION.md) for the full engineering constitution.

- Modularity over monoliths
- Documentation over assumptions
- Interfaces over coupling
- Testing over guessing
- Observability over opacity
- Security by design
- Open standards over vendor lock-in

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT License — See [LICENSE](LICENSE).

---

## Authors

**MucizeWork**

Web4 Blockchain Intelligence Platform

```
Build Secure.
Analyze Smart.
Scale Together.
```
