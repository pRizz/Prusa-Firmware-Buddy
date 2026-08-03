# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

v1.0 established the source-backed Rust+Bazel parity evidence foundation. v1.1 hardened the remaining cutover blockers into durable CI, simulator, hardware, live-service, release, retained-code, upstream-result, and maintainer-review gate capabilities. v1.2 executed those external evidence and acceptance flows, closed upstream evidence flow into final readiness, and produced archival-ready milestone evidence. v1.3 consumed real sanitized maintainer/operator evidence packets, triaged blockers, recorded explicit maintainer decisions, generated final readiness from real consumed rows, and produced a go/no-go cutover decision artifact. v1.4 now brings up the first real Bazel-native Rust firmware image for one development target: `MINI/BUDDY/STM32F407VG`.

The replacement firmware is not yet cut over. CMake/C++ remains a separately named reference and rollback oracle. Physical qualification, release signing, production flashing, behavior parity, cutover, and reference demotion remain blocked and outside v1.4; none can be inferred from a passing development safe-boot image.

## Milestones

- **v1.0 Rust Port Evidence Foundation** - Phases 1-12, 38 plans, shipped 2026-06-15. Archives: [roadmap](milestones/v1.0-ROADMAP.md), [requirements](milestones/v1.0-REQUIREMENTS.md), [audit](milestones/v1.0-MILESTONE-AUDIT.md), [phase history](milestones/v1.0-phases/).
- **v1.1 Cutover Evidence Hardening** - Phases 13-22, 13 plans, shipped 2026-06-22. Archives: [roadmap](milestones/v1.1-ROADMAP.md), [requirements](milestones/v1.1-REQUIREMENTS.md), [audit](milestones/v1.1-MILESTONE-AUDIT.md).
- **v1.2 Cutover Evidence Execution and Acceptance** - Phases 23-30, 9 plans, shipped 2026-07-02. Archives: [roadmap](milestones/v1.2-ROADMAP.md), [requirements](milestones/v1.2-REQUIREMENTS.md), [audit](milestones/v1.2-MILESTONE-AUDIT.md).
- **v1.3 Cutover Approval and Reference Demotion Trial** - Phases 31-41, 37 plans, shipped 2026-08-02. Archives: [roadmap](milestones/v1.3-ROADMAP.md), [requirements](milestones/v1.3-REQUIREMENTS.md), [audit](milestones/v1.3-MILESTONE-AUDIT.md), [phase history](milestones/v1.3-phases/).
- **v1.4 Bazel-Native Rust Firmware Bring-Up** - Phases 42-49, active. One development-only MINI/BUDDY/STM32F407VG safe-boot image; no production authority.

## Phases

<details>
<summary>v1.0 Rust Port Evidence Foundation (Phases 1-12) - SHIPPED 2026-06-15</summary>

- [x] Phase 1: Reference Baseline and Safety Envelope - completed 2026-06-02
- [x] Phase 2: Bazel Authority and Developer Facade - completed 2026-06-02
- [x] Phase 3: Artifact and Generator Parity - completed 2026-06-03
- [x] Phase 4: Rust Architecture and Invariant Model - completed 2026-06-03
- [x] Phase 5: Foreign Code, Unsafe, and Runtime Boundary - completed 2026-06-03
- [x] Phase 6: Printing Core, Safety, and Feature Gates - completed 2026-06-04
- [x] Phase 7: Persistence, Storage, and Resource Compatibility - completed 2026-06-06
- [x] Phase 8: Local Interface and Workflow Parity - completed 2026-06-13
- [x] Phase 9: Network, Web Services, and Transfers - completed 2026-06-14
- [x] Phase 10: Auxiliary Controllers and Expansion Ecosystem - completed 2026-06-14
- [x] Phase 11: Parity Pyramid and Cutover Evidence - completed 2026-06-14
- [x] Phase 12: Milestone Evidence Hygiene - completed 2026-06-15

Full phase details are archived in `.planning/milestones/v1.0-ROADMAP.md`.

</details>

<details>
<summary>v1.1 Cutover Evidence Hardening (Phases 13-22) - SHIPPED 2026-06-22</summary>

- [x] Phase 13: CI Evidence Orchestration - completed 2026-06-16
- [x] Phase 14: Simulator Evidence Gates - completed 2026-06-17
- [x] Phase 15: Hardware Safety and Media Qualification - completed 2026-06-18
- [x] Phase 16: Live Network and Transfer Qualification - completed 2026-06-18
- [x] Phase 17: Release Candidate Artifact and Signing Gates - completed 2026-06-19
- [x] Phase 18: Retained-Code Acceptance and Cutover Review - completed 2026-06-20
- [x] Phase 19: Aggregate Cutover Evidence CI - completed 2026-06-21
- [x] Phase 20: Release Candidate Artifact Production - completed 2026-06-21
- [x] Phase 21: Final Readiness Result Consumption - completed 2026-06-21
- [x] Phase 22: Evidence Metadata Reconciliation - completed 2026-06-21

Full phase details are archived in `.planning/milestones/v1.1-ROADMAP.md`.

</details>

<details>
<summary>v1.2 Cutover Evidence Execution and Acceptance (Phases 23-30) - SHIPPED 2026-07-02</summary>

- [x] **Phase 23: Simulator Evidence Execution** - Maintainers supply and retain real simulator results for startup, G-code, GUI, storage, transfer, and selected failure flows. (completed 2026-06-23)
- [x] **Phase 24: Hardware, Media, and Safety Evidence Execution** - Maintainers supply and retain real hardware, storage-media, UI-input, auxiliary, and safety evidence. (completed 2026-06-23)
- [x] **Phase 25: Live-Service Evidence Execution** - Maintainers supply and retain real Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, and crash-dump evidence. (completed 2026-06-23)
- [x] **Phase 26: Release, Signing, and Upstream Result Evidence** - Release managers supply secret-safe release outputs while maintainers receive upstream result rows for every cutover gate. (completed 2026-06-24)
- [x] **Phase 27: Retained-Code and Maintainer Acceptance Decisions** - Maintainers record retained-code, residual-risk, exception, and final-readiness decisions as machine-readable inputs. (completed 2026-06-25)
- [x] **Phase 28: Final Readiness Packet and Demotion Gate** - Maintainers generate the final readiness packet while reference demotion stays blocked unless explicitly approved. (completed 2026-06-25)
- [x] **Phase 29: Upstream Evidence Flow Closure** - Phase 26 consumes Phase 23-25 upstream row artifacts, Phase 28 reflects real evidence flow, and audit metadata debt is reconciled. (completed 2026-06-25)
- [x] **Phase 30: Milestone Metadata Cleanup** - Refresh state, extraction, and verification-report metadata so v1.2 can be archived without contradictory planning artifacts. (completed 2026-06-27)

Full phase details are archived in `.planning/milestones/v1.2-ROADMAP.md`.

</details>

<details>
<summary>v1.3 Cutover Approval and Reference Demotion Trial (Phases 31-41) - SHIPPED 2026-08-02</summary>

- [x] Phase 31: Final Evidence Intake - completed 2026-07-03
- [x] Phase 32: Blocker Register and Evidence Triage - completed 2026-07-03
- [x] Phase 33: Maintainer Decision Inputs - completed 2026-07-04
- [x] Phase 34: Final Readiness and Demotion Dry Run - completed 2026-07-25
- [x] Phase 35: Cutover Decision Artifact - completed 2026-07-26
- [x] Phase 36: Normalize Evidence and Blocker Rows - completed 2026-07-26
- [x] Phase 37: Reconcile Decisions Into Readiness - completed 2026-07-26
- [x] Phase 38: Fail-Closed Cutover Workflow - completed 2026-07-27
- [x] Phase 39: Milestone Metadata Reconciliation - completed 2026-07-29
- [x] Phase 40: File Length Refactoring - completed 2026-07-28
- [x] Phase 41: Terminal Milestone Metadata Coherence - completed 2026-08-01

Full phase details are archived in `.planning/milestones/v1.3-ROADMAP.md`; requirements, audit evidence, and execution history are archived beside it.

</details>

### v1.4 Bazel-Native Rust Firmware Bring-Up (Phases 42-49) - ACTIVE

- [ ] **Phase 42: Truthful Bazel Graph and Executable MINI Toolchain** - Developers get hermetic target selection and commands that perform their named work or fail visibly.
- [ ] **Phase 43: Pure Safe-Boot Policy** - Maintainers can prove the legal safe-boot, fault, and watchdog decisions without hardware effects.
- [ ] **Phase 44: Retained Reset, Vector, and Link Boundary** - The image has one inspectable startup owner and one structurally enforced memory layout.
- [ ] **Phase 45: MINI Hazardous-Output Adapter** - The board boundary inhibits every scoped hazardous output with reviewed, transient-safe sequencing.
- [ ] **Phase 46: Rust Runtime, Faults, Watchdog, and Validated ELF** - The real Rust image reaches safe-ready and survives terminal paths without gaining operational capabilities.
- [ ] **Phase 47: Genuine Artifact Family and Immutable Provenance** - Every development artifact derives from one accepted ELF and one immutable identity.
- [ ] **Phase 48: MINI Simulator Scenarios and Fail-Closed Evidence** - Mini404 exercises the exact image and reports only independently observable claims.
- [ ] **Phase 49: Clean CI Qualification and Non-Production Claim Freeze** - Canonical CI reproduces and retains current-run qualification without granting production or demotion authority.

## Phase Details

### Phase 42: Truthful Bazel Graph and Executable MINI Toolchain

**Goal**: Developers can select the explicit MINI/BUDDY/STM32F407VG target and trust Bazel and `just` to execute hermetic target work or fail visibly.
**Depends on**: Nothing (first v1.4 phase; Phase 41 closed v1.3)
**Requirements**: BUILD-02, BUILD-03, BUILD-04, TOOL-01
**Success Criteria** (what must be TRUE):

1. From a clean checkout, the explicit MINI platform resolves pinned, checksum-verified Rust, Arm GNU, Python, and simulator tools without undeclared `PATH` or `.dependencies` fallback.
2. Named build, test, package, and simulator commands perform their named work and emit genuine outputs, or exit nonzero with an actionable diagnostic; printing a reference command cannot count as success.
3. Unsupported product, board, MCU, target, or host combinations fail during analysis or toolchain resolution instead of selecting host code, fixtures, CMake outputs, or archived artifacts.
4. Separately named CMake/C++ reference commands and labels remain usable as the comparison and rollback oracle but cannot satisfy any Rust firmware success gate.

**Plans**: 5 plans

Plans:
- [ ] 42-01-PLAN.md — Pin exact module/tool versions, checksum-backed repositories, rules_python, and stable lock provenance.
- [ ] 42-02-PLAN.md — Define the canonical hard-float MINI platform and executable host/toolchain provider contract.
- [ ] 42-03-PLAN.md — Produce and inspect the genuine Cortex-M4 hard-float ARM link smoke.
- [ ] 42-04-PLAN.md — Enforce the negative platform matrix and configured/action/provider graph isolation.
- [ ] 42-05-PLAN.md — Gate false authority, split reference semantics, and deliver the canonical aggregate verifier.
**Research**: No standalone phase research expected; use the pinned-toolchain, explicit-platform, and truthful-facade patterns already established by repository research and official Bazel/rules documentation.

### Phase 43: Pure Safe-Boot Policy

**Goal**: Maintainers can prove the legal safe-boot, fault, and watchdog decisions as an allocation-free Rust policy before hardware effects are introduced.
**Depends on**: Phase 42
**Requirements**: BOOT-01, SAFE-02, SAFE-05
**Success Criteria** (what must be TRUE):

1. Focused host tests prove that boot policy permits only reset-unknown to outputs-inhibited to deterministic safe-ready transitions and rejects every illegal transition.
2. Rust cannot construct safe-ready without an outputs-inhibited capability, and the policy exposes no motion, heating, printing, allocation, RTOS, or hosted-runtime capability.
3. Maintainers can run focused host tests for boot, output-inhibition, terminal-fault convergence, and watchdog feed/no-feed decisions without MMIO, CMake, firmware hardware, or Mini404.

**Plans**: TBD
**Research**: No standalone phase research expected; apply the established Bright Builds functional-core, type-state, `no_std`, and focused Arrange/Act/Assert testing guidance.

### Phase 44: Retained Reset, Vector, and Link Boundary

**Goal**: Maintainers can inspect and reject startup images until reset ownership, Rust handoff, and the selected MINI memory layout are singular and structurally correct.
**Depends on**: Phases 42-43
**Requirements**: LINK-01, LINK-02
**Success Criteria** (what must be TRUE):

1. Each firmware label selects one explicit boot/load layout, and inspection rejects an invalid entry point, vector placement, section placement, RAM range, stack contract, undefined symbol, or incompatible EABI.
2. The link contains exactly one reset/vector/RAM-initialization owner that initializes stack, `.data`, and `.bss`, then hands control directly to one non-returning Rust entry point.
3. Boot and direct-load needs, if both remain necessary, are exposed as separately named load configurations without silently creating two behaviorally different firmware identities.

**Plans**: TBD
**Research**: Focused research required before planning: confirm exact MINI boot/no-boot startup sources, Rust 2024 handoff symbol spelling, boot-exchange sections, and canonical linker/load behavior from a real link.

### Phase 45: MINI Hazardous-Output Adapter

**Goal**: The MINI board boundary can inhibit every scoped hazardous output at the earliest practical point using reviewed, transient-safe register sequencing.
**Depends on**: Phases 43-44
**Requirements**: SAFE-01
**Success Criteria** (what must be TRUE):

1. Maintainers can inspect one MINI/BUDDY pin-and-polarity definition covering hotend heat, bed heat, X/Y/Z/E motor enables, and every documented fan output in scope.
2. Adapter tests prove that safe latch values are written before pins enter output mode and that repeated inhibition is idempotent.
3. All scoped hazardous-output MMIO is confined to one audited unsafe adapter that returns the capability required by safe-ready; simulator proof remains separate and physical electrical qualification remains blocked.

**Plans**: TBD
**Research**: Focused research required before planning: verify STM32F407 reset-state GPIO behavior, clock prerequisites, latch-before-mode register ordering, output polarities, and whether any inhibition must occur before Rust/RAM initialization.

### Phase 46: Rust Runtime, Faults, Watchdog, and Validated ELF

**Goal**: Maintainers can build and inspect a real Rust-owned MINI image that reaches deterministic safe-ready and returns every terminal path to inhibited outputs.
**Depends on**: Phases 42-45
**Requirements**: BUILD-01, TOOL-02, LINK-03, SAFE-03, SAFE-04, ARTF-01
**Success Criteria** (what must be TRUE):

1. Bazel cross-compiles the explicit MINI/BUDDY/STM32F407VG `no_std`/`no_main` firmware and emits a genuine Cortex-M ELF plus GNU linker map from one accepted final link.
2. Pre-package inspection proves every Rust and retained native object uses the compatible Cortex-M4 hard-float `thumbv7em-none-eabihf` ABI, has no unresolved symbols, and contains only the declared retained-code bill of materials with rationale and retirement conditions.
3. The runtime hands off directly into Rust, inhibits outputs, reaches deterministic safe-ready, and remains in a non-returning terminal loop with no HAL, FreeRTOS, Marlin, C++ constructor, GUI, network, storage, motion, heating, or printing path.
4. Panic, HardFault, default-interrupt, and other terminal handlers converge on the same allocation-free, idempotent output-inhibition primitive before entering a non-returning terminal state.
5. The watchdog is fed only while policy is healthy; starvation causes a bounded reset and re-entry that inhibits outputs again and never treats reset as operational readiness.

**Plans**: TBD
**Research**: No standalone research expected beyond consuming Phase 44 reset/link and Phase 45 GPIO findings; validate the mixed Rust/ASM final-link mechanics during planning and execution.

### Phase 47: Genuine Artifact Family and Immutable Provenance

**Goal**: Developers receive genuine development artifacts whose payloads and evidence all trace to one accepted embedded link.
**Depends on**: Phase 46
**Requirements**: ARTF-02, ARTF-03, ARTF-04
**Success Criteria** (what must be TRUE):

1. Bazel derives a raw BIN and explicitly unsigned development BBF from the accepted ELF, and validation proves the BBF payload matches that accepted image.
2. The ELF, map, BIN, BBF, validation results, and downstream evidence rows share one immutable identity containing source revision, target label, boot layout, pinned tool versions, and cryptographic digests.
3. Missing tools, invalid ELF structure, packaging failure, stale outputs, fixture markers, split lineage, or reference/archive substitution cause visible failure and cannot fall back to an older artifact.

**Plans**: TBD
**Research**: Focused research required before planning: verify unsigned BBF header fields, firmware/load offsets, metadata, and payload lineage against `utils/pack_fw.py` and a known CMake/C++ reference artifact.

### Phase 48: MINI Simulator Scenarios and Fail-Closed Evidence

**Goal**: Maintainers can exercise the exact validated development image in Mini404 and distinguish observed behavior from unsupported simulator claims.
**Depends on**: Phase 47
**Requirements**: SIM-01, SIM-02, SIM-03
**Success Criteria** (what must be TRUE):

1. A MINI-specific Mini404 scenario boots the exact digest-bound v1.4 image and reaches deterministic safe-ready within a bounded timeout.
2. Evidence independently observes each hazardous-output state that Mini404 exposes; unsupported observations are reported as `blocked` or `not_observed` and firmware self-report cannot promote them to pass.
3. Supported panic/fault and watchdog-starvation/reset/re-entry scenarios run against the real image with bounded timeouts, while unsupported injections or observations fail closed.

**Plans**: TBD
**Research**: Focused research required before planning: prove the canonical boot-layout load contract plus Mini404 GPIO, reset-cause, watchdog, and fault-injection observability before defining passing scenario assertions.

### Phase 49: Clean CI Qualification and Non-Production Claim Freeze

**Goal**: Maintainers can reproduce and retain current-run safe-boot qualification in canonical CI without converting development evidence into production authority.
**Depends on**: Phase 48
**Requirements**: CI-01, CI-02, CLAIM-01
**Success Criteria** (what must be TRUE):

1. A clean canonical Linux CI run resolves pinned toolchains, cross-builds, inspects, packages, host-tests, simulates, and retains current-run artifacts and actionable diagnostics on both success and failure.
2. CI evidence is digest-bound to the current source and accepted ELF, separates current, reference, and archive roots, and publishes fail-closed current-run state so stale or reference evidence cannot requalify a failure.
3. CI comparison rows consume separately rooted, normalized CMake/C++ reference facts while refusing those facts as current Rust qualification evidence.
4. The terminal qualification states only that one development safe-boot image is real and testable; physical safety, production flashing, release signing, behavior parity, cutover, and reference demotion remain explicitly blocked.

**Plans**: TBD
**Research**: Focused research required before planning: specify immutable current/reference/archive evidence roots, current-run publication identity, failed-run replacement behavior, and retention semantics that cannot resurrect stale success.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 42. Truthful Bazel Graph and Executable MINI Toolchain | 0/TBD | Not started | - |
| 43. Pure Safe-Boot Policy | 0/TBD | Not started | - |
| 44. Retained Reset, Vector, and Link Boundary | 0/TBD | Not started | - |
| 45. MINI Hazardous-Output Adapter | 0/TBD | Not started | - |
| 46. Rust Runtime, Faults, Watchdog, and Validated ELF | 0/TBD | Not started | - |
| 47. Genuine Artifact Family and Immutable Provenance | 0/TBD | Not started | - |
| 48. MINI Simulator Scenarios and Fail-Closed Evidence | 0/TBD | Not started | - |
| 49. Clean CI Qualification and Non-Production Claim Freeze | 0/TBD | Not started | - |

**Coverage:** 25/25 active v1.4 requirements mapped exactly once; no orphaned or duplicate mappings.
