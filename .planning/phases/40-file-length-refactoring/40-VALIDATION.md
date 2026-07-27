---
phase: "40"
slug: "file-length-refactoring"
status: planned
nyquist_compliant: true
wave_0_complete: false
created: "2026-07-27"
---

# Phase 40 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Managed Bun checker, Python `unittest`, Cargo, Catch2/CTest, Bazel, simulator integration |
| **Config file** | `scripts/bright-builds-check.ts`, `pyproject.toml`, `Cargo.toml`, `tests/CMakeLists.txt`, `MODULE.bazel` |
| **Quick run command** | `bun scripts/bright-builds-check.ts all` |
| **Full suite command** | `just phase40-verify` plus the current campaign's language/firmware gate |
| **Estimated runtime** | ~2 seconds quick; campaign gates vary from focused seconds to firmware/simulator minutes |

## Sampling Rate

- **After every task commit:** Run `bun scripts/bright-builds-check.ts all`, the focused behavior test, and `git diff --check`.
- **After every plan wave:** Run `just phase40-verify` plus every affected language or firmware gate listed below.
- **Before `/gsd-verify-work`:** Run terminal reconciliation, the ordered Rust sequence, all affected Python phase gates, host tests, representative firmware builds, and simulator parity.
- **Max feedback latency:** 30 seconds for the task-level focused check; broad build and simulator gates run at plan or wave boundaries.

## Per-Campaign Verification Map

| Campaign | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline | Exact 838 permanent + 95 temporary partition | T-40-01 | New or misclassified oversized paths fail closed | policy/unit | `just phase40-verify` | ⬜ pending |
| Rust domain | Four stable Rust interfaces | T-40-02 | No visibility, error, or feature drift | unit/build | ordered Cargo sequence, then Rust `just` gates | ⬜ pending |
| Utilities | CLI/import compatibility | T-40-03 | Arguments, exits, and output paths remain stable | unit/contract | utility tests, `python3 utils/build.py --help`, underlying build command | ⬜ pending |
| Phases 5–11 | Existing verifier contracts | T-40-04 | Artifact and exit semantics remain stable | contract | `just phase5-verify` through `just phase11-verify` as affected | ⬜ pending |
| Phases 13–17 | Evidence producer contracts | T-40-04 | Security and evidence schemas remain stable | contract | `just phase13-verify` through `just phase17-verify` as affected | ⬜ pending |
| Phases 18–28 | Readiness evidence contracts | T-40-04 | Fail-closed outputs and schemas remain stable | contract | affected Phase 18–28 `just` gates | ⬜ pending |
| Phases 31–38 | Finality and cutover contracts | T-40-04 | Authority, provenance, and failure publication remain stable | integration | affected Phase 31–38 `just` gates | ⬜ pending |
| Firmware tests | Characterization coverage | T-40-05 | Splitting tests does not drop or combine behavior | unit | owning Catch/CTest targets and `just test` underlying command | ⬜ pending |
| Parser/UI/WUI | Public rendering and protocol behavior | T-40-06 | Public headers, resources, HTTP behavior, and state mapping remain stable | host/build | focused host tests plus representative build | ⬜ pending |
| Network/media | Network and transfer behavior | T-40-07 | Protocols, filenames, recovery, and statuses remain stable | host/simulator | focused tests, representative build, simulator parity | ⬜ pending |
| Persistent storage | Stored schema and migration behavior | T-40-08 | Layout, hashes, defaults, and migration remain stable | unit/generated | storage tests, generated check, build, simulator parity | ⬜ pending |
| Hardware/auxiliary | HAL and wire behavior | T-40-09 | Register, protocol, and hardware adapter behavior remain stable | unit/build/simulator | focused tests, board builds, simulator where supported | ⬜ pending |
| Print/safety | Lifecycle and safety behavior | T-40-10 | Queue ordering, state transitions, fatal paths, and recovery remain stable | characterization/integration | host tests, supported build matrix, simulator integration | ⬜ pending |
| Terminal reconciliation | Exact final ledger and zero findings | T-40-01 | No temporary or unauthorized permanent exceptions survive | policy/full | `just phase40-verify --terminal` or equivalent terminal mode | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

## Wave 0 Requirements

- [ ] `tools/bazel/phase40_file_length_policy.py` — parse the user-owned TSV and enforce approved reason/path categories without modifying the managed checker.
- [ ] `tools/bazel/phase40_file_length_policy_test.py` — one-concern tests for malformed rows, unauthorized owned permanence, temporary-set growth, and terminal reconciliation.
- [ ] `just phase40-verify` — execute the policy verifier/tests and `bun scripts/bright-builds-check.ts all`.
- [ ] `.bright-builds-rules-checks.tsv` — sorted exact-path baseline with 838 permanent and 95 temporary reasons.

Existing Cargo, Python, Catch2/CTest, Bazel, build, and simulator infrastructure covers the remaining campaigns.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
| --- | --- | --- | --- |
| Hardware-aware review | Firmware safety contract preservation | Some hardware coupling is not represented by host tests or simulator models | Review changed HAL/safety paths against reference behavior and record simulator coverage gaps. |
| Physical hardware behavior | Only behavior changes or simulator gaps | Hardware is unnecessary for structural moves with complete simulator coverage | When triggered, run the affected board/printer scenario and attach observed before/after evidence. |

## Validation Sign-Off

- [x] All campaigns have an automated focused or wave-level verification command.
- [x] Sampling continuity prevents three consecutive tasks without automated verification.
- [x] Wave 0 defines every missing policy-verification artifact.
- [x] No watch-mode flags are used.
- [x] Task-level focused feedback target is below 30 seconds.
- [x] `nyquist_compliant: true` is set in frontmatter.

**Approval:** approved 2026-07-27
