# Smart Contract

## Overview

The on-chain program (Anchor/Solana) handles:
- Authority management
- Treasury operations
- State validation
- Verifiable records

## Program Structure

```
programs/mzc_web4/
+-- lib.rs
+-- instructions/
+-- state/
+-- events.rs
+-- errors.rs
+-- constants.rs
+-- security.rs
+-- utils.rs
```

## Instructions (Planned)

- initialize()
- update_config()
- create_treasury()
- deposit()
- withdraw()
- pause()
- resume()
- transfer_authority()

## Security

- Signer validation
- Authority validation
- PDA validation
- Overflow checks
- Pause state checks
