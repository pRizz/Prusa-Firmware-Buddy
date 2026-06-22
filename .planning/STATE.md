---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Cutover Evidence Hardening
status: completed
stopped_at: Milestone v1.1 archived
last_updated: "2026-06-22T19:36:38Z"
last_activity: 2026-06-22
progress:
  total_phases: 10
  completed_phases: 10
  total_plans: 13
  completed_plans: 13
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-22)

**Core value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.
**Current focus:** Between milestones — v1.1 archived; next milestone not defined

## Current Position

Milestone: v1.1 Cutover Evidence Hardening — COMPLETE
Phase: none active
Plan: none active
Status: Milestone v1.1 archived; next milestone not defined
Last activity: 2026-06-22

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 13
- Average duration: N/A
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 13 | 1 | - | - |
| 14 | 1 | - | - |
| 15 | 1 | - | - |
| 16 | 1 | - | - |
| 17 | 1 | - | - |
| 18 | 1 | - | - |
| 19 | 1 | - | - |
| 20 | 2 | - | - |
| 21 | 1 | - | - |
| 22 | 3 | - | - |

**Recent Trend:**

- Last 5 plans: Phase 20 P02, Phase 21 P01, Phase 22 P01, Phase 22 P02, Phase 22 P03
- Trend: v1.1 archived with cutover evidence gates validated; next milestone should start from clean requirements

*Updated after each plan completion*
| Phase 07 P01 | 11min | 3 tasks | 4 files |
| Phase 07 P02 | 6 min | 3 tasks | 4 files |
| Phase 07 P03 | 10 min | 2 tasks | 4 files |
| Phase 07 P04 | 8 min | 2 tasks | 3 files |
| Phase 07 P05 | 7 min | 2 tasks | 6 files |
| Phase 11 P01 | 10m43s | 2 tasks | 4 files |
| Phase 11 P02 | 6m09s | 1 tasks | 2 files |
| Phase 11 P03 | 8m12s | 2 tasks | 4 files |
| Phase 11 P04 | 8m01s | 2 tasks | 3 files |
| Phase 11 P05 | 21m | 3 tasks | 9 files |
| Phase 12 P01 | 7 min | 3 tasks | 7 files |
| Phase 13 P01 | 18 min | 3 tasks | 12 files |
| Phase 15 P01 | 23m31s | 3 tasks | 7 files |
| Phase 18 P01 | 30m 21s | 3 tasks | 7 files |
| Phase 19 P01 | 18 min | 4 tasks | 9 files |
| Phase 20 P01 | 12 min | 2 tasks | 4 files |
| Phase 20 P02 | 13m02s | 2 tasks | 8 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Migration posture: Big Bang replacement, not incremental dual production ownership.
- Compatibility bar: Behavior Parity for currently supported printers, release artifacts, resources, tests, network behavior, storage, and safety-critical firmware behavior.
- Build system posture: Bazel Primary Now; CMake remains reference/comparison only where needed.
- Developer facade: `justfile` required for common Bazel/Rust workflows.
- Standards: Bright Builds Rules apply, including Rust-specific standards and no active local overrides.
- Rust architecture: pure domain invariants live in `buddy-domain`; application and adapter crates consume typed profiles instead of unchecked primitives.
- [Phase 07]: Represent Phase 7 persistence parity as source-backed JSON contracts before adding Rust verifier code.
- [Phase 07]: Keep credential-bearing storage evidence name-only and classify USB, flash, semihosting, and media proof as non-local evidence.
- [Phase 07]: Represent IFCE-05 resource and generated-output parity as source-backed JSON contracts before adding aggregate verifier code.
- [Phase 07]: Preserve known Phase 7 risks as explicit disposition rows unless a later plan introduces intentional deltas with tests.
- [Phase 07]: Represent Phase 7 storage, filesystem, fixture, credential-redaction, and journal hash compatibility as fallible Rust domain types.
- [Phase 07]: Represent Phase 7 resource paths and generated-output labels as fallible Rust domain types tied to source-backed runtime path constants.
- [Phase 07]: Keep Phase 7 quick verification static and deterministic while reserving Cargo checks for --all.
- [Phase 07]: Keep Bazel and just facade checks scope-compatible with Plan 07-04 until later wiring work owns facade edits.
- [Phase 07]: Validate current Phase 7 manifest evidence classes without rewriting prior plan artifacts.
- [Phase 07]: Expose Phase 7 aggregate verification through Bazel labels and just phase7-verify using the existing Rust workflow dispatch pattern.
- [Phase 07]: Record only passed local verifier, Bazel, just, and Rust evidence as green while preserving hardware, media, simulator, generator, and release parity as non-local evidence.
- [Phase 07]: Reference the redacted migration catalog from the root filegroup through the tools/bazel package label to respect Bazel package boundaries.
- [Phase 11]: Plan 11-01 classified simulator, CI, release, hardware, manual, and retained-code evidence as non-local or pending proof rather than local pass evidence.
- [Phase 11]: Plan 11-01 implemented later Phase 11 verifier modes now so absent later-owned manifests fail with explicit missing-manifest errors.
- [Phase 11]: Preserved release-candidate, simulator, hardware, live network, and final cutover proof as named blockers instead of local pass evidence.
- [Phase 11]: Referenced Plan 11-03 and Plan 11-04 manifests as pending evidence classes rather than source artifacts until those files exist.
- [Phase 11]: Represent every VERF-03 comparison row as normalized semantic evidence with guarded reference-only execution.
- [Phase 11]: Keep byte-identity claims available only through an explicit Rust contract requiring fixture and normalization data.
- [Phase 11]: Classify simulator, hardware, manual, and retained-code evidence as non-local so local cutover proofs cannot overclaim.
- [Phase 11]: Keep criteria-reference-demotion-blocked at status not-cutover-ready with demotion_allowed false.
- [Phase 11]: Represent retained-code islands as accepted, blocked, or deferred while preserving simulator, hardware, live network/TLS, storage media, release-candidate, signing, MMU, RS485, and toolchanger proof as required evidence.
- [Phase 11]: Carry known codebase and phase concern dispositions into cutover evidence instead of treating local static verification as final proof.
- [Phase 11]: Expose Phase 11 aggregate verification through Bazel root aliases and just phase11-verify.
- [Phase 11]: Keep local sign-off limited to deterministic source, manifest, Bazel, lifecycle, and Rust checks while non-local gates remain blocked.
- [Milestone v1.0]: Archive source-backed local proof separately from non-local cutover approval; v1.1 should execute the remaining non-local gates rather than recasting them as already complete.
- [Milestone v1.1]: Treat CI, simulator, hardware, live-service, release-candidate, signing, retained-code acceptance, and maintainer review as first-class requirements.
- [Phase 13]: Phase 13 CI evidence uses a checked-in JSON contract plus a thin read-only GitHub Actions wrapper around repo-owned Python verifier modes. — This keeps evidence gate semantics reviewable in source, keeps workflow logic minimal, and preserves later non-local evidence as pending instead of local pass claims.
- [Phase 15]: Phase 15 quick mode leaves physical hardware-observation rows pending; only operator evidence can mark them passed or failed.
- [Phase 15]: Phase 15 operator evidence requires complete device, build, operator, timestamp, scenario, result, artifact ref, and residual-risk metadata.
- [Phase 15]: Phase 15 artifact paths and operator refs stay repo-relative under build/ci-evidence/phase15 and are scanned before retention.
- [Phase 15]: Phase 15 follows the existing Bazel rust_workflow dispatch model and just phase15-verify runs tests before the verifier.
- [Phase 18]: Quick-mode output is review material only; demotion_allowed remains false without maintainer decision input.
- [Phase 18]: Phase 18 source refs resolve against approved prior-phase manifests instead of prose-only evidence references.
- [Phase 18]: Security scanning rejects secret, payload, crash-dump, credential, and cutover-approval overclaim markers across inputs and generated artifacts.
- [Phase 20]: Phase 20 Plan 01 keeps release rows pending in quick mode unless approved release input is supplied.
- [Phase 20]: Phase 20 release refs are limited to external://phase20/... or repo-relative build/ci-evidence/phase20 paths.
- [Phase 20]: Phase 20 rejects private key, credential, token, password, raw payload, and crash-dump field names at the release input boundary.
- [Phase 20]: Phase 17 release identity now resolves to the Phase 20 release-environment input manifest instead of remaining empty.
- [Phase 20]: Representative smoke and phase3 verifier labels remain separate and are rejected as production release identity dependencies.
- [Phase 20]: Phase 20 just and Bazel verifier facades run tests before verifier quick output.

### Pending Todos

None yet.

### Blockers/Concerns

- Hardware availability and failure-injection scope must be confirmed before final cutover qualification.
- Live Connect/WUI/TLS evidence must avoid committing secrets, tokens, certificates, or production payloads.
- Release-candidate signing evidence must preserve key hygiene and avoid putting private key material into planning artifacts.

## Session Continuity

Last session: 2026-06-22T19:36:38Z
Stopped at: Milestone v1.1 archived
Resume file: .planning/milestones/v1.1-MILESTONE-AUDIT.md
