# @mucizework/normalizer

MUCIZECHAİN blockchain adres normalizasyonu paketi.

## Overview

Bu paket farklı blockchain'ler için adres normalizasyonu ve canonical ID üretimi sağlar.

## Features

- **Blockchain Enum**: Desteklenen blockchain tipleri
- **CanonicalID**: Standart adres formatı

## Installation

```bash
npm install @mucizework/normalizer
```

## Usage

```typescript
import { Blockchain, CanonicalID } from '@mucizework/normalizer';

const canonicalId: CanonicalID = {
  blockchain: Blockchain.ETHEREUM,
  address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
  network: 'mainnet'
};
```

## API Documentation

### Blockchain

Desteklenen blockchain tipleri:

- `ETHEREUM`
- `SOLANA`
- `BNB_CHAIN`
- `POLYGON`
- `ARBITRUM`
- `OPTIMISM`
- `AVALANCHE`
- `BASE`
- `UNKNOWN`

### CanonicalID

Standart adres formatı interface'i.

### Properties

- `blockchain`: Blockchain tipi
- `address`: Normalize edilmiş adres
- `network`: Network adı

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