# SDK

Client SDKs for the WEB4 Engine API.

## Planned SDKs

- `typescript-sdk/` — TypeScript/JavaScript
- `python-sdk/` — Python
- `rust-sdk/` — Rust
- `go-sdk/` — Go

## Usage (Planned)

```typescript
import { Web4Client } from '@mucizework/web4-sdk';

const client = new Web4Client('http://localhost:5002');
const health = await client.health();
const graph = await client.graph();
```
