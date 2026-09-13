# @mucizework/common

MUCIZECHAİN ortak util'leri paketi.

## Overview

Bu paket MIGE OS ekosisteminde kullanılan temel utility class'larını ve interface'lerini içerir.

## Features

- **Result Pattern**: Hata yönetimi için tip-safe result pattern
- **Hash Service**: Canonical hash üretimi (SHA256)
- **UUID**: UUID v4/v5 generator
- **Clock**: System ve Test clock implementasyonları
- **Retry Policy**: Otomatik retry mekanizması
- **Error Hierarchy**: Standart app error hiyerarşisi

## Installation

```bash
npm install @mucizework/common
```

## Usage

### Result Pattern

```typescript
import { ResultType, CompileResult } from '@mucizework/common';

const result = ResultType.success({ data: 'value' });
if (ResultType.isSuccess(result)) {
  console.log(result.value);
}
```

### Hash Service

```typescript
import { canonicalHashService } from '@mucizework/common';

const hash = canonicalHashService.sha256('data');
const evidenceId = canonicalHashService.generateEvidenceId({
  blockchain: 'ETHEREUM',
  address: '0x...',
  timestamp: Date.now()
});
```

### UUID

```typescript
import { UUID } from '@mucizework/common';

const id = UUID.v4();
const deterministicId = UUID.v5('namespace', 'name');
```

### Clock

```typescript
import { systemClock } from '@mucizework/common';

const now = systemClock.now();
await systemClock.sleep(1000);
```

### Retry Policy

```typescript
import { withRetry, DefaultRetryPolicy } from '@mucizework/common';

const policy = new DefaultRetryPolicy({ maxAttempts: 3 });
const result = await withRetry(() => fetchData(), policy);
```

### Error Handling

```typescript
import { AppErrorFactory, isAppError } from '@mucizework/common';

const error = AppErrorFactory.validation('Invalid input');
if (isAppError(error)) {
  console.log(error.type, error.message);
}
```

## API Documentation

### Result<T, E>

Tip-safe result pattern implementasyonu.

### HashService

Canonical hash üretimi için interface.

### Clock

Time abstraction için interface.

### RetryPolicy

Retry stratejileri için interface.

### AppError

Standart app error interface'i.

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