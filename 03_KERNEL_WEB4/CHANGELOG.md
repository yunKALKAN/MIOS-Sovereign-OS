# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] - 2025-06-21

### Added

- API Contract v1 (Frozen) with `/api/v1/` prefix
- X-Request-ID middleware
- X-API-Version: 1.0 header
- Standardized error responses (400/401/403/404/409/422/429/500)
- Enhanced `/health` with subsystem status reporting
- `/api/v1/hash/sha256` endpoint (SHA-256 digest)
- `/api/v1/sign/verify` endpoint (signature verification)
- `/api/v1/funding/{wallet}` with path parameter filtering
- OpenAPI 3.0.3 specification
- 19 integration tests
- Professional README.md
- Project documentation (ROADMAP, ARCHITECTURE, API, SECURITY, etc.)

## [0.1.0] - 2025-06-20

### Added

- Initial project structure
- Core orchestrator API (Flask, port 5002)
- WEB4 Auth (Solana ED25519, port 5080)
- WalletCluster (AJAN/MZC/MYK)
- Smart Money Radar
- Funding Trace Engine
- Signature Engine (SHA-256)
- Core config (BLACK mode)
- Storage layer (JSON-based)

## [Unreleased]

### Planned

- Graph Engine v2
- Radar Engine v2
- Funding Engine v2
- Plugin system
- Event bus
- Dashboard
- Docker deployment
- v1.0.0 release
