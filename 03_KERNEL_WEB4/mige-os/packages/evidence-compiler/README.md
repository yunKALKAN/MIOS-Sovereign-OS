# @mucizework/evidence-compiler

MUCIZECHAİN Delil Derleyicisi paketi.

## Overview

Bu paket blockchain delillerini toplamak, derlemek ve doğrulamak için altyapı sağlar.

## Features

- **Evidence**: Delil contract'ları
- **Compiler**: Delil derleme motoru
- **Handler**: İşleyici soyutlaması
- **Validator**: Doğrulama katmanı
- **Event Bus**: Olay tabanlı mimari
- **Test Suite**: Deterministik, replay ve cross-platform testler

## Installation

```bash
npm install @mucizework/evidence-compiler
```

## Usage

```typescript
import { Evidence, EvidenceType } from '@mucizework/evidence-compiler';
```

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