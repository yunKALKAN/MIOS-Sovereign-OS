# Architecture

## Platform Layers

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

## Layer Definitions

### 1. Blockchain Layer (Anchor/Solana)

Smart contracts, on-chain state, PDA accounts, signature verification.

### 2. Core Intelligence Layer

| Engine  | Responsibility                              |
|---------|---------------------------------------------|
| Graph   | Wallet relationship graphs, cluster analysis |
| Radar   | Smart money detection, signal generation     |
| Funding | Fund source analysis, confidence scoring     |
| Risk    | Wallet risk scoring, anomaly detection        |

### 3. Service Layer

- REST API Gateway (Flask, port 5002)
- SDK (TypeScript, Python, Rust, Go)
- CLI (`web4` commands)

### 4. Platform Layer

- CI/CD (GitHub Actions)
- Monitoring (Prometheus, Grafana)
- Logging (structured JSON)
- Tracing (OpenTelemetry)
- Docker / Kubernetes

### 5. Developer Experience Layer

- Documentation (OpenAPI, ADR, RFC)
- Examples and Tutorials
- Plugin System

## Module Communication

Modules communicate through **interfaces**, not direct imports.

```
Engine Registry
      |
      +-- IGraphEngine
      +-- IRadarEngine
      +-- IFundingEngine
      +-- IRiskEngine
      +-- ISignatureEngine
```

## Event-Driven Architecture

```
WalletDetected --> FundingCompleted --> RiskCalculated
                                            |
                                     RadarSignalCreated
                                            |
                                     NotificationSent
```

## Plugin System

```
plugins/
+-- solscan/
+-- helius/
+-- birdeye/
+-- debank/
+-- chainbase/
+-- dexscreener/
```

New data providers are added as plugins without modifying core engines.

## Design Principles

- **Modularity over monoliths**
- **Interfaces over coupling**
- **Documentation over assumptions**
- **Testing over guessing**
- **Observability over opacity**
- **Security by design**
- **Open standards over vendor lock-in**
