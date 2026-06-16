---
phase: 09-network-web-services-and-transfers
plan: 02
subsystem: rust-domain-network
tags: [rust, buddy-domain, network, connect, prusalink, transfers]

requires:
  - phase: 09-network-web-services-and-transfers
    provides: Phase 9 network context, research, validation, and UI/evidence contracts
provides:
  - Pure Rust Phase 9 network, WUI, service, transfer, evidence, proof, and redaction contracts
  - Feature-gated network service contract constructors for Connect and WUI-backed services
  - Unit-tested transfer range, command ID, proxy, auth, encrypted metadata, and evidence/proof invariants
affects: [phase-09-verifier, IFCE-02, IFCE-03, buddy-domain]

tech-stack:
  added: []
  patterns:
    - Fallible Rust newtypes/enums for raw network boundary values
    - Named-only secret and encrypted-payload metadata contracts
    - FeatureSet-gated service availability checks

key-files:
  created:
    - rust/crates/domain/src/network.rs
  modified:
    - rust/crates/domain/src/lib.rs

key-decisions:
  - "Represent Phase 9 network, WUI, transfer, evidence, proof, and redaction facts in pure buddy-domain types before adapter code can consume them."
  - "Keep credential and AES-CTR metadata named-only, with no key, IV, token, password, or certificate byte storage."
  - "Gate Prusa Connect on Feature::Connect and WUI/SNTP/mDNS/DNS/metrics/syslog on Feature::WebUi."

patterns-established:
  - "NetworkEvidenceClass mirrors prior GUI/storage evidence locality while rejecting local proof for simulator, hardware, and manual evidence."
  - "NetworkParityRowId and ConnectCommandId reject empty, path-like, whitespace/control, non-printable, and over-96-byte identifiers."
  - "NetworkServiceContract enforces service feature gates at construction time."

requirements-completed: [IFCE-02, IFCE-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 9-2026-06-14T02-15-21
generated_at: 2026-06-14T03:37:31Z

duration: 11 min
completed: 2026-06-14
---

# Phase 09 Plan 02: Network Domain Contracts Summary

**Pure Rust Phase 9 network, PrusaLink/WUI, service, transfer, evidence, proof, and redaction contracts in buddy-domain**

## Performance

- **Duration:** 11 min
- **Started:** 2026-06-14T03:26:51Z
- **Completed:** 2026-06-14T03:37:31Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `rust/crates/domain/src/network.rs` with typed Phase 9 contracts for evidence classes, proof scopes, row IDs, secret handling, Connect command IDs/states, telemetry/WebSocket surfaces, proxy modes, WUI endpoint/auth modes, transfer sources/states/ranges/encryption/recovery/errors, service surfaces, and parity/service contracts.
- Extended `rust/crates/domain/src/lib.rs` with public network exports and exact Phase 9 invariant error variants/messages.
- Verified the Rust workspace with focused network tests, formatting, clippy, all-targets build, and full Rust tests.

## Task Commits

1. **Task 1: Add failing network domain tests** - `7db3d2f05` (test)
2. **Task 2: Implement network domain contracts and exports** - `79201a260` (feat)

_Note: This TDD plan produced the expected RED commit followed by the GREEN implementation commit._

## Files Created/Modified

- `rust/crates/domain/src/network.rs` - Pure Phase 9 network/service/transfer/evidence domain contracts and unit tests.
- `rust/crates/domain/src/lib.rs` - Public exports and invariant errors for the new network domain contracts.

## Decisions Made

- Followed the established `buddy-domain` pattern of parsing raw boundary values into fallible Rust types and keeping adapter/runtime effects out of the domain crate.
- Kept secret-bearing and encrypted-payload evidence as named identities only; no fields or getters expose token/password/certificate/key/IV bytes.
- Limited the final planning metadata commit to `09-02-SUMMARY.md` because the orchestrator owns `STATE.md`, `ROADMAP.md`, and config writes after wave completion.

## Deviations from Plan

None - plan executed exactly as written. Additional full Rust build/test checks were run to satisfy repo pre-commit requirements.

## Issues Encountered

None.

## Known Stubs

None - stub scan found no TODO, FIXME, placeholder, coming-soon, or not-available text in the created/modified files.

## User Setup Required

None - no external service configuration required.

## Verification

- `cargo test -p buddy-domain --all-features network` - passed after Task 2; RED failure was captured before Task 1 commit.
- `cargo fmt --all -- --check` - passed.
- `cargo clippy --all-targets --all-features -- -D warnings` - passed.
- `cargo build --all-targets --all-features` - passed.
- `cargo test --all-features` - passed.
- Task acceptance `rg` checks for tests, exports, invariant errors, service gates, transfer metadata, and no `unsafe` - passed.

## Next Phase Readiness

Ready for Plan 09-03 to consume the exported network contracts in verifier/API-shape checks. Live cloud, physical networking, simulator flows, USB/media races, long-running transfers, and final cutover proof remain non-local evidence as planned.

## Self-Check: PASSED

- `rust/crates/domain/src/network.rs` exists.
- `rust/crates/domain/src/lib.rs` exists.
- Commit `7db3d2f05` exists: `test(09-02): add failing tests for network domain contracts`.
- Commit `79201a260` exists: `feat(09-02): implement network domain contracts`.
- Threat surface scan found no new network endpoints, filesystem access, live TLS/cloud calls, schema changes, or unsafe implementation in the created/modified domain files.

---
*Phase: 09-network-web-services-and-transfers*
*Completed: 2026-06-14*
