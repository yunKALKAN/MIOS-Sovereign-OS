# @mucizework/core-contracts

MUCIZECHAİN temel sözleşmeleri paketi.

## Overview

Bu paket MIGE OS ekosisteminde kullanılan temel data contract'larını içerir.

## Features

- **Provenance**: Delil köken bilgisi için contract

## Installation

```bash
npm install @mucizework/core-contracts
```

## Usage

```typescript
import { Provenance } from '@mucizework/core-contracts';

const provenance: Provenance = {
  blockchain: 'ETHEREUM',
  source: 'rpc',
  collectedAt: Date.now(),
  adapterVersion: '1.0.0',
  rawHash: 'abc123',
  schemaVersion: '1.0.0'
};
```

## API Documentation

### Provenance

Delil köken bilgisi interface'i.

### Properties

- `blockchain`: Blockchain tipi
- `source`: Veri kaynağı
- `collectedAt`: Toplama zamanı (timestamp)
- `adapterVersion`: Adapter versiyonu
- `rawHash`: Ham veri hash'i
- `schemaVersion`: Schema versiyonu

## Development

```bash
# Build
npm run build

# Test
npm test
npm run test:coverage

# Lint
npm run lint
npm run lint:fix

# Type check
npm run typecheck
```

## License

MIT