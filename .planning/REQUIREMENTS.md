# Requirements: Prusa Firmware Buddy Rust Port - v1.4 Bazel-Native Rust Firmware Bring-Up

**Defined:** 2026-08-02
**Core Value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

## v1.4 Requirements

These requirements deliver one executable, development-only Rust firmware bring-up for `MINI/BUDDY/STM32F407VG`. They do not authorize production flashing, release signing, printer-behavior cutover, or demotion of the C/C++ reference firmware.

### Build Authority and Toolchains

- [ ] **BUILD-01**: Developer can build a real embedded Rust firmware image for the explicit `MINI/BUDDY/STM32F407VG` platform through Bazel from a clean checkout.
- [ ] **BUILD-02**: Developer-facing build, test, package, and simulator commands either perform the named work and emit genuine outputs or exit nonzero with an actionable error.
- [ ] **BUILD-03**: Unsupported product, board, MCU, or host combinations fail during Bazel analysis or toolchain resolution without silently selecting a host build, fixture, CMake result, or reference artifact.
- [ ] **BUILD-04**: Developer can invoke the CMake/C++ reference path through separately named commands and labels that cannot satisfy Rust firmware success criteria.
- [ ] **TOOL-01**: Maintainer can reproduce the embedded target with pinned, checksum-verified Rust, Arm GNU, Python, and simulator tools without undeclared `PATH` or `.dependencies` fallback.
- [ ] **TOOL-02**: Maintainer can prove every Rust and retained native object in the image uses the compatible Cortex-M4 hard-float `thumbv7em-none-eabihf` ABI, with mismatches rejected before packaging.

### Reset, Link, and Retained Boundary

- [ ] **LINK-01**: The firmware has exactly one reset, vector-table, stack, `.data`, and `.bss` initialization owner that hands control directly to a non-returning Rust entry point.
- [ ] **LINK-02**: Each firmware label selects one explicit boot/load layout, and automated ELF checks reject an invalid entry point, vector placement, section placement, RAM range, stack contract, undefined symbol, or incompatible EABI.
- [ ] **LINK-03**: Maintainer can inspect a declared retained-code bill of materials with rationale and retirement condition, and the real linked image rejects undeclared HAL, FreeRTOS, Marlin, C++ constructor, GUI, network, or storage code.

### Safe-Boot Runtime

- [ ] **BOOT-01**: Maintainer can test an allocation-free `no_std` boot policy that permits only the transition from reset-unknown through outputs-inhibited to a deterministic safe-ready state.
- [ ] **SAFE-01**: On every boot, the MINI adapter inhibits hotend heat, bed heat, X/Y/Z/E motor enables, and documented fan outputs at the earliest practical point using latch-before-output-mode sequencing.
- [ ] **SAFE-02**: Rust cannot construct the safe-ready state without an outputs-inhibited capability, and the v1.4 firmware exposes no operational motion, heating, or printing command path.
- [ ] **SAFE-03**: Panic, HardFault, default-interrupt, and other terminal runtime paths converge on the same allocation-free, idempotent output-inhibition primitive before entering a non-returning terminal state.
- [ ] **SAFE-04**: The watchdog is serviced only while the safe-boot policy is healthy; starvation produces a bounded reset and re-entry path that inhibits outputs again without treating the reset as operational readiness.
- [ ] **SAFE-05**: Maintainer can run focused host tests for pure boot, fault, output-inhibition, and watchdog policy without requiring firmware hardware, MMIO, CMake, or the simulator.

### Artifact Lineage

- [ ] **ARTF-01**: Bazel emits a genuine Cortex-M ELF and GNU linker map from one accepted final link rather than fixture, placeholder, or print-only outputs.
- [ ] **ARTF-02**: Bazel derives a raw BIN and explicitly unsigned development BBF from the accepted ELF, and validation proves the BBF payload matches the accepted image.
- [ ] **ARTF-03**: Every ELF, map, BIN, BBF, validation result, and downstream evidence row is bound to one immutable provenance identity containing source revision, target label, boot layout, tool versions, and cryptographic digests.
- [ ] **ARTF-04**: Missing tools, invalid ELF structure, packaging failure, stale outputs, fixture markers, or split artifact lineage cause visible failure and cannot fall back to an older or reference artifact.

### Simulator and CI Evidence

- [ ] **SIM-01**: Mini404 boots the exact validated v1.4 image and reaches deterministic safe-ready within a bounded timeout using a MINI-specific scenario.
- [ ] **SIM-02**: Simulator evidence independently observes hazardous-output inhibition where Mini404 supports it and reports unsupported observations as `blocked` or `not_observed` instead of accepting firmware self-report as proof.
- [ ] **SIM-03**: Simulator scenarios exercise supported fault and watchdog reset/re-entry behavior against the real image, with unsupported injections or observations failing closed.
- [ ] **CI-01**: A clean canonical Linux CI run resolves toolchains, cross-builds, inspects, packages, host-tests, simulates, and retains current-run artifacts and diagnostics on both success and failure.
- [ ] **CI-02**: CI evidence is digest-bound to the current source and accepted ELF, separates current/reference/archive roots, and cannot resurrect stale or reference evidence after a current-run failure.
- [ ] **CLAIM-01**: Milestone qualification states only that the development safe-boot image is real and testable; physical safety, production flashing, release signing, behavior parity, cutover, and reference demotion remain separately blocked.

## Future Requirements

Deferred to later milestones after the first executable Rust image is stable.

### Qualification and Expansion

- **REPRO-01**: Maintainer can reproduce byte-identical development artifacts across repeated canonical builds and, later, supported hosts.
- **BUDGET-01**: Maintainer can enforce reviewed flash, RAM, and stack budgets derived from the first real linker map.
- **TRACE-01**: Maintainer can consume a typed machine-readable boot trace as supplementary diagnostics without substituting it for independent observations.
- **FAULT-01**: Maintainer can execute an expanded deterministic fault-injection matrix beyond the v1.4 simulator-supported paths.
- **COMPARE-01**: Maintainer can compare normalized Rust and C reference facts for vectors, memory layout, package metadata, and safe-output policy.
- **HW-01**: Maintainer can run an instrumented physical MINI safe-output smoke test through the existing hardware-evidence process.
- **DEV-01**: Developer can use an opt-in flash/debug facade for the development image with explicit hardware and signing safeguards.
- **PARITY-01**: Maintainer can add the first operational behavior slice after safe boot while preserving the v1.4 safety and provenance boundaries.

## Out of Scope

Explicitly excluded to prevent the first real image from becoming an implicit production cutover.

| Feature | Reason |
|---------|--------|
| Additional printer, board, or MCU targets | v1.4 proves one explicit `MINI/BUDDY/STM32F407VG` product path before generalizing the platform matrix. |
| FreeRTOS, full STM32 HAL ownership, or a new async executor | The first image needs a minimal safe runtime, not application scheduling or a runtime-architecture decision. |
| Marlin, printing, heating, motion, GUI, persistence, networking, Connect, PrusaLink, transfers, or full crash handling | Operational behavior parity belongs after deterministic safe boot is executable and evidenced. |
| New `cortex-m-rt`, Rust HAL, Embassy, RTIC, `defmt`, or `probe-rs` dependencies | Retaining narrow known startup and tooling boundaries reduces simultaneous change during first-link diagnosis. |
| Replacing retained startup, linker, packaging, vendor, or imported boundaries broadly | Retained code must be explicit and justified; broad replacement requires targeted evidence in later milestones. |
| Release signing, DFU/install workflows, production flashing, rollout, cutover, or C++ reference demotion | A development safe-boot image is not a release candidate and grants no production authority. |
| Physical hardware qualification | Mini404 and structural evidence are the v1.4 acceptance boundary; physical qualification remains an additive later gate. |
| New printer UX or behavior beyond the safe-ready terminal state | v1.4 establishes executable infrastructure and safety, not product functionality. |
| Committing private keys, tokens, certificates, service payloads, raw crash dumps, or other secret-bearing artifacts | All build and evidence outputs must remain secret-safe and reviewable. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BUILD-01 | Phase 46 | Pending |
| BUILD-02 | Phase 42 | Pending |
| BUILD-03 | Phase 42 | Pending |
| BUILD-04 | Phase 42 | Pending |
| TOOL-01 | Phase 42 | Pending |
| TOOL-02 | Phase 46 | Pending |
| LINK-01 | Phase 44 | Pending |
| LINK-02 | Phase 44 | Pending |
| LINK-03 | Phase 46 | Pending |
| BOOT-01 | Phase 43 | Pending |
| SAFE-01 | Phase 45 | Pending |
| SAFE-02 | Phase 43 | Pending |
| SAFE-03 | Phase 46 | Pending |
| SAFE-04 | Phase 46 | Pending |
| SAFE-05 | Phase 43 | Pending |
| ARTF-01 | Phase 46 | Pending |
| ARTF-02 | Phase 47 | Pending |
| ARTF-03 | Phase 47 | Pending |
| ARTF-04 | Phase 47 | Pending |
| SIM-01 | Phase 48 | Pending |
| SIM-02 | Phase 48 | Pending |
| SIM-03 | Phase 48 | Pending |
| CI-01 | Phase 49 | Pending |
| CI-02 | Phase 49 | Pending |
| CLAIM-01 | Phase 49 | Pending |

**Coverage:**

- v1.4 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0
- Duplicate mappings: 0

***

*Requirements defined: 2026-08-02*
*Last updated: 2026-08-02 after v1.4 roadmap creation*
