# MIGE-OS Sprint CI Validation Policy v1.0

## Principle

```text
Implementation ≠ Validation

A code change is not considered complete until GitHub Actions validates it successfully.
```

---

## CI Validation Workflow

For every push:

1. Wait until all GitHub Actions workflows finish.
2. Do not assume success.
3. Report only completed workflow results.

---

## Workflow Report

For every workflow report:

```text
Workflow:
Commit SHA:
Started:
Finished:
Duration:

Status:
PASS
FAIL
SKIPPED

Runner:
Operating System:
Runtime Version:
```

---

## Failure Report

If a workflow fails:

```text
Root Cause

Workflow:
File:
Line:
Exception:
Error Message:

Classification

Configuration
Dependency
Build
Type Error
Runtime
Test Failure
Infrastructure

Resolution

Fix Applied:
Commit:
Verification Pending:
```

---

## Evidence

Every reported result must have evidence.

| Evidence        | Source         |
| --------------- | -------------- |
| Workflow Status | GitHub Actions |
| Commit SHA      | Git            |
| Logs            | GitHub Actions |
| Duration        | GitHub Actions |
| Runner          | GitHub Actions |

If evidence is unavailable:

```text
Evidence unavailable.
Verification pending.
```

---

## Completion Criteria

A Sprint is **Completed** only if **all** conditions are met:

* ✅ Build PASS
* ✅ Type Check PASS
* ✅ Lint PASS
* ✅ Unit Tests PASS
* ✅ Integration Tests PASS (if defined)
* ✅ GitHub Actions PASS
* ✅ No Critical Security Alerts
* ✅ Branch Protection satisfied
* ✅ Release Tag available

---

## Release Candidate Status

Implementation: COMPLETE
Validation: PENDING

Waiting For:
- GitHub Build
- GitHub Lint
- GitHub Tests
- GitHub Security Checks

Evidence Source:
GitHub Actions

Current State:
VALIDATION_PENDING

---

## Sprint State Machine

```text
PLANNED
    │
    ▼
IMPLEMENTING
    │
    ▼
CODE_COMPLETE
    │
    ▼
VALIDATION_PENDING
    │
    ├──────────────┐
    │              │
    ▼              ▼
VALIDATED      VALIDATION_FAILED
    │              │
    ▼              │
RELEASED ◄─────────┘
```

**State Transitions:**
- Kod yazmak → `CODE_COMPLETE`
- GitHub Actions çalışıyor → `VALIDATION_PENDING`
- Tüm kontroller yeşil → `VALIDATED`
- Tag + Release → `RELEASED`

---

## Validation State Rule

No task may transition from CODE_COMPLETE to VALIDATED without objective evidence.

The only accepted validation sources are:

- GitHub Actions
- CI artifacts
- Test reports
- Release artifacts

Engineering judgement alone cannot change the validation state.

---

## Sprint 2 Transition Criteria

Sprint 2 may only be started when all of the following are PASS:

* ✅ Build
* ✅ TypeScript Type Check
* ✅ Python Lint
* ✅ Python Tests
* ✅ Security Scan (CodeQL)
* ✅ Secret Scanning
* ✅ Branch Protection
* ✅ Signed Commit Policy
* ✅ Signed Release Tag

Only when these criteria are met may Sprint 1 be considered "frozen foundation" and upper layer development begin.

---

## Operator Interaction Policy

You are an autonomous build engineer.

Never ask the operator to:

- wait for CI
- report GitHub Actions status
- report build results
- report lint results
- report test results

If local validation is complete, stop.

If GitHub-hosted validation cannot be inspected because of missing permissions, simply state:

"GitHub-hosted validation cannot be inspected from this environment."

End the report.

Never request additional user interaction unless a blocking error requires a human decision.

Do not ask questions after successful push.
Do not ask for GitHub screenshots.
Do not ask the user to paste GitHub logs unless the user explicitly requests CI debugging.

---

## MIGE Engineering Rule

```text
No implementation may be reported as complete without verifiable evidence.

Every engineering statement must be traceable to an objective source.

Engineering assessments must never be presented as externally verified facts.
```

---

**Copyright © 2026 Mucize Platform. All Rights Reserved.**

## Repository Information

**Repository:** MIGE-OS
**Classification:** Commercial Proprietary Software
**Visibility:** Private
**License:** Commercial

---

## Devin AI Agent Policy

### Core Rules

1. **Never create public repositories.**
   - All repositories must be private.
   - Code is proprietary intellectual property.

2. **Never push secrets.**
   - No API keys in code.
   - No credentials in environment files.
   - All secrets in GitHub Secrets.

3. **Never disable GitHub Secret Scanning.**
   - Secret scanning must remain enabled.
   - Push protection must remain enabled.

4. **Never bypass Branch Protection.**
   - All merges must go through pull requests.
   - All status checks must pass.
   - No force pushes to protected branches.

5. **All commits must be signed.**
   - GPG signing required.
   - Unsigned commits will be rejected.
   - Tags must be signed.

6. **All release tags must be signed.**
   - Use `git tag -s` for signed tags.
   - Verify signatures before release.

7. **Never rewrite protected branch history.**
   - No `git push --force` to main.
   - No rebase on protected branches.
   - Preserve commit history.

8. **All Pull Requests must pass:**
   - Build
   - Test
   - Type Check
   - Lint
   - Security Scan

9. **Architecture contracts marked as Frozen must not be modified without explicit approval.**
   - Sprint 1 packages are frozen.
   - Only bug fixes allowed.
   - Breaking changes require review.

10. **All new functionality must preserve deterministic behavior.**
    - Evidence compilation must be deterministic.
    - Graph operations must be reproducible.
    - Tests must validate determinism.

11. **Any breaking interface change requires a new major version proposal.**
    - SemVer must be followed.
    - Breaking changes require major version increment.
    - Deprecation notices required.

12. **Never remove Provenance information.**
    - Audit trail must be preserved.
    - Metadata must be immutable.
    - History cannot be deleted.

13. **Never remove audit metadata.**
    - All operations must be auditable.
    - Logs must be preserved.
    - Traceability is mandatory.

14. **Preserve backwards compatibility whenever possible.**
    - Deprecated APIs must remain for one major version.
    - Migration paths must be provided.
    - Breaking changes must be documented.

15. **Treat this repository as commercial intellectual property.**
    - No open source licensing.
    - No public contributions.
    - All code is proprietary.

---

## Development Guidelines

### Code Quality
- TypeScript strict mode required
- No `any` types allowed
- All functions must have return types
- Comprehensive test coverage required

### Security
- All secrets in GitHub Secrets
- No hardcoded credentials
- Regular dependency updates
- Security scanning enabled

### Documentation
- All changes must be documented
- README must reflect current state
- CHANGELOG must be updated
- Architecture decisions must be recorded

### Testing
- Unit tests for all new code
- Integration tests for critical paths
- E2E tests for user flows
- Coverage minimum 80%

---

## Release Process

1. Create release branch from `develop`
2. Update version in package.json
3. Update CHANGELOG.md
4. Run full test suite
5. Create pull request to `main`
6. Approve and merge
7. Create signed tag
8. Create GitHub Release

---

## Sprint Policy

### Sprint 1 (Foundation) - FROZEN
- Packages: common, normalizer, core-contracts, evidence-compiler
- Status: Feature freeze
- Only bug fixes allowed

### Sprint 2 (Identity Core) - PLANNED
- Identity resolver
- Identity registry
- Identity merger
- Identity repository

### Sprint 3 (Graph Platform) - PLANNED
- Graph builder
- Node factory
- Edge factory
- Graph mutation

### Sprint 4 (Query Platform) - PLANNED
- Query engine
- AST parser
- Query planner
- Execution engine

### Sprint 5 (Runtime Platform) - PLANNED
- Runtime orchestrator
- REST API
- gRPC API
- Worker system

---

## Emergency Procedures

### Security Incident
1. Immediately notify security@mucizeplatform.com
2. Create hotfix branch
3. Fix the issue
4. Run security scan
5. Expedited review
6. Emergency release

### Production Outage
1. Create incident issue
2. Investigate root cause
3. Implement fix
4. Deploy to production
5. Post-mortem document

---

## Contact

**Technical Lead:** @yunKALKAN
**Security:** security@mucizeplatform.com
**Licensing:** licensing@mucizeplatform.com