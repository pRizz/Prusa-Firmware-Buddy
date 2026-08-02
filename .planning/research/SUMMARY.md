# Project Research Summary

**Project:** Prusa Firmware Buddy Rust Port — v1.4 Bazel-Native Rust Firmware Bring-Up
**Domain:** Safety-conscious Bazel-native embedded Rust bring-up for `MINI/BUDDY/STM32F407VG`
**Researched:** 2026-08-02
**Confidence:** HIGH for scope, dependency order, ABI, repository boundaries, and artifact lineage; MEDIUM for exact Mini404 GPIO/watchdog observability until exercised

## Executive Summary

Milestone v1.4 is a narrow executable bring-up, not another parity-contract milestone and not a production cutover. Its acceptance boundary is one real Bazel-built, cross-compiled Rust image for `MINI/BUDDY/STM32F407VG` that enters through the established STM32F407 boot layout, inhibits motion and thermal outputs at the earliest practical point, reaches a deterministic safe-ready state, and produces genuine ELF, linker map, BIN, and unsigned development BBF artifacts. The C/C++/CMake firmware remains the behavioral reference and rollback path. Printing, GUI, networking, storage, physical safety qualification, release signing, rollout, reference demotion, and every other printer target remain outside v1.4.

The recommended implementation pins Bazel 9.2.0, `rules_rust` 0.71.3, Rust 1.85.0, `rules_cc` 0.2.22, `rules_python` 2.2.0, and Arm GNU 13.2.Rel1. Bazel must own the `thumbv7em-none-eabihf` compile, mixed Rust/ASM final link, validation, artifact derivation, packaging, simulator inputs, and CI evidence. Retain exactly one STM32F407 startup assembly veneer, the selected boot linker script, the existing unsigned BBF encoder, and target-aware Arm binutils as declared boundaries. After the veneer initializes memory and branches to `rust_entry() -> !`, Rust owns safe-output inhibition, typed boot policy, fault convergence, watchdog policy, and the terminal safe loop. Do not pull the full HAL, FreeRTOS, C++ constructors, Marlin, application services, or a new Rust runtime/HAL ecosystem into the first image.

The dominant risks are wrong target or float ABI, double ownership of reset/vectors, unsafe GPIO sequencing, divergent panic/HardFault/watchdog behavior, retained-code creep, non-hermetic Bazel wrappers, split or fixture-backed artifact lineage, and simulator claims that exceed observable evidence. Mitigate them with explicit platforms and pinned executable toolchains, one reset owner and one boot profile per label, latch-before-mode output writes through a sole audited MMIO adapter, a shared idempotent inhibition primitive for every terminal path, ELF/map/symbol acceptance before packaging, digest-bound evidence, and fail-closed `blocked`/`not_observed` statuses. A passing v1.4 result means only that the first Rust safe-boot image is real and honestly testable; it does not authorize physical deployment or production cutover.

## Key Findings

### Recommended Stack

Use a purpose-built Bazel embedded image path rather than extending the current fixture-oriented package surface or calling Cargo/CMake through shell wrappers. A small Starlark final-link rule should combine the Rust firmware archive/object set, one retained startup ASM target, and `stm32f407vg_boot.ld` through the Arm GNU driver, declaring both ELF and genuine GNU linker-map outputs. The accepted ELF is the root of all downstream lineage: Arm GNU `objcopy` derives the BIN, `utils/pack_fw.py --no-sign` derives the development BBF, and a manifest binds hashes, sizes, tools, platform, linker script, boot mode, and signing classification.

The reports considered newer compilers, LLVM linking, `cortex-m-rt`, Rust HALs, and new simulator/packaging stacks. Those are deliberately deferred. The first link should minimize simultaneous change by matching the repository's current Rust floor, hard-float ABI, Arm GNU toolchain, boot memory layout, Mini404 version, and BBF encoder.

**Core technologies:**

- **Bazel 9.2.0 + Bzlmod:** authoritative build, link, artifact, simulator, and test graph — removes the current host-dependent and print-only ambiguity.
- **`rules_rust` 0.71.3 + Rust 1.85.0/edition 2024:** registered `thumbv7em-none-eabihf` compiler and sysroot — matches the workspace floor and avoids mixing a compiler migration into first-link diagnosis.
- **`rules_cc` 0.2.22 + Arm GNU 13.2.Rel1:** retained startup assembly, hard-float native ABI, final link, `readelf`, `nm`, `size`, and `objcopy` — matches the C reference toolchain and flags.
- **`rules_python` 2.2.0:** declared execution of the established BBF encoder and pytest-based evidence helpers — missing dependencies must fail rather than select fixtures.
- **Mini404 0.9.10:** existing MINI simulator lane — retain the known emulator while proving what it can independently observe.
- **`just`:** thin developer facade over real Bazel labels — `just build`, `just test`, and the safe-boot simulation command must perform their named work or exit nonzero.
- **Rust `core` only in the firmware:** allocation-free runtime primitives — do not add `std`, `alloc`, nightly `build-std`, or third-party embedded crates in v1.4.
- **Retained STM32F407 startup ASM and linker script:** narrow reset/vector/RAM-init veneer and bootloader-compatible layout — replacement requires later simulator and hardware evidence.

**Critical configuration decisions:**

- Target `thumbv7em-none-eabihf` with Cortex-M4, hard-float, FPv4-SP-D16 compatibility across every object at an ABI boundary.
- Pin all downloadable tools with checksums and commit `MODULE.bazel.lock`; do not resolve tools from `PATH` or undeclared `.dependencies` directories.
- Use `panic=abort`, no unwinding, no allocator, no hosted startup, and no implicit semihosting.
- Default the development BBF to `stm32f407vg_boot.ld` at `0x08020200`. If Mini404 needs the direct layout at `0x08000000`, expose it as a separately named load configuration and do not build a behaviorally different second firmware silently.
- Make canonical Linux CI the reproducibility authority. Unsupported macOS/Apple-silicon toolchain or Mini404 prerequisites must fail with an actionable message, not use a different Arm release.

### Expected Features

**Must have (v1.4 table stakes):**

- Truthful `just` and Bazel commands that produce real outputs/evidence or fail visibly.
- One explicit `//platforms:mini_buddy_stm32f407vg` product target; unsupported products fail during analysis.
- A pinned, executable embedded Rust/Arm toolchain and a genuine `no_std`/`no_main` Cortex-M4 firmware binary.
- Exactly one reset/vector/RAM-init owner, one explicit boot profile per label, one non-returning Rust handoff, and structural ELF/map checks.
- A genuine ELF, linker map, BIN, unsigned-development BBF, and provenance bundle derived from one accepted link.
- A typed safe-boot sequence that makes `OutputsInhibited` a prerequisite for safe-ready and exposes no motion/heating capability.
- Earliest practical inhibition of MINI hotend, bed, and X/Y/Z/E motor-enable outputs, with latch-before-output-mode ordering and independently observed simulator state where supported.
- Panic, HardFault, default-interrupt, and watchdog paths that converge on the same allocation-free, idempotent inhibition primitive.
- Host unit tests for pure boot/fault/watchdog policy and MINI-specific Mini404 scenarios for cold boot, supported fault injection, watchdog behavior, and output inhibition.
- An explicit retained-boundary bill of materials checked against the real linked symbol/section inventory.
- Clean-checkout CI that cross-builds, validates, packages, simulates, and retains redacted, current-run, digest-bound evidence.
- Fail-closed claim vocabulary that preserves physical-hardware, production-cutover, release-signing, and reference-demotion gates.

**Should have after the core bring-up is stable:**

- Same-host, then cross-host, byte reproducibility for development artifacts.
- Enforced flash/RAM/stack budgets based on the first real map.
- A typed machine-readable boot trace used as diagnostics alongside independent observations.
- A broader deterministic fault-injection matrix.
- Normalized structural comparison with the C reference for vectors, memory, package metadata, and safe-output policy.
- An opt-in development flash/debug facade and instrumented physical MINI safe-output smoke through the existing hardware-evidence process.

**Deferred beyond v1.4:**

- Additional printer, board, or MCU targets.
- FreeRTOS/task orchestration, full STM32 HAL ownership, or a new async executor/RTOS architecture.
- Marlin, printing, heating, motion, GUI, persistence, networking, Connect, PrusaLink, transfers, or full crash-dump parity.
- `cortex-m-rt`, `stm32f4xx-hal`, Embassy, RTIC, `defmt`, `probe-rs`, or other ecosystem additions not required for the first safe image.
- New Rust BBF encoding, release signing, DFU/install flows, production flashing, rollout, cutover, or reference demotion.
- Replacement of retained startup/HAL/CMSIS/ASM/vendor boundaries before targeted evidence justifies it.

### Architecture Approach

Apply the Bright Builds functional-core/imperative-shell and type-driven boundary rules at embedded scale. A fixed-size `safe-boot-core` owns pure states, transitions, fault causes, and watchdog-feed eligibility. A MINI board adapter is the sole unsafe MMIO owner and encodes exact pin/polarity facts. A narrow runtime adapter owns panic, exception, watchdog, and terminal-loop effects. The retained startup veneer owns only vectors, initial stack, `.data` copy, `.bss` zero, and the direct branch to Rust. Packaging and evidence remain host-side consumers of firmware outputs, never runtime dependencies.

**Major components:**

1. **Bazel MINI platform and executable toolchains** — resolve the pinned Rust target, Arm native/link tools, and declared Python/simulator host tools.
2. **`safe-boot-core`** — model `ResetUnknown -> OutputsInhibited -> SafeBootLatched` and all fault/watchdog transitions without hardware, heap, RTOS, or logging dependencies.
3. **MINI board adapter** — own the reviewed BUDDY pin table, latch-before-mode MMIO, and idempotent `force_inhibit()` unsafe boundary.
4. **Embedded runtime adapter and MINI executable** — export `rust_entry() -> !`, compose boot policy with GPIO/watchdog/fault effects, and park without operational capabilities.
5. **Retained startup/link boundary** — provide one reset/vector/RAM-init veneer and one explicit linker profile per target label.
6. **Post-link validation and artifact rules** — accept the real ELF/map, derive BIN/BBF, and emit immutable lineage/provenance with no fixture fallback.
7. **MINI simulator/evidence adapter** — bind Mini404 scenarios and normalized fail-closed observations to the exact artifact digest.
8. **Separate CMake reference comparator** — compare normalized structural/safety facts and preserve a selectable rollback path without satisfying Rust build success.

**Resolved architecture choices:**

- Retain startup ASM and linker layout now; defer `cortex-m-rt` ownership.
- Let Rust own executable behavior immediately after memory initialization; do not keep C `main` or full HAL/FreeRTOS ahead of the safety latch.
- Create a small new `no_std` safe-boot core rather than forcing the current host-oriented `std` crate graph into the firmware. Reuse compatible typed contracts, not incompatible runtime dependencies.
- Produce one canonical bootloader-layout image. Adapt the simulator loader if needed; do not hide two independently linked images behind one identity.
- Use a dedicated declared final-link/artifact rule because a plain `rust_binary` does not by itself guarantee the paired GNU linker map and mixed-language ABI boundary required here.

### Critical Pitfalls

1. **Target, CPU, or float ABI drift** — pin target and tools, align all native flags, link through Arm GCC, and reject ELFs that fail machine/EABI/undefined-symbol inspection.
2. **Two reset/vector/runtime owners** — retain exactly one startup veneer and linker profile, prohibit competing C `main`/Rust runtime/vector symbols, and assert output layout from the ELF/map.
3. **Hazardous outputs inhibited late or only on the happy path** — set safe latches before output modes, require an unforgeable inhibition capability, and route reset/fault/watchdog paths through the sole audited MMIO primitive.
4. **Retained-code creep makes Rust ownership nominal** — keep every retained symbol in a narrow declared target with rationale and retirement condition; fail on HAL, FreeRTOS, Marlin, C++ constructors, GUI, network, or storage symbols.
5. **Bazel is a shell wrapper or artifact names hide split lineage** — declare every tool/input/output, root all derivatives in one validated ELF digest, reject fixture/bootstrap markers, and fail on missing prerequisites.
6. **Simulator success is overclaimed** — use a MINI-specific harness, treat self-report as supplementary, publish unsupported observations as `blocked`/`not_observed`, and leave hardware qualification and cutover authority unchanged.
7. **Stale/reference/archive evidence re-qualifies a failed current image** — use immutable run IDs and explicit roots, bind rows to revision/label/ELF digest, and publish a current fail-closed result even when a later gate aborts.

## Implications for Roadmap

The research supports eight dependency-ordered phases. They are intentionally milestone-specific and end at a qualified development image, not a releasable printer firmware.

### Phase 1: Truthful Bazel Graph and Executable MINI Toolchain

**Rationale:** Every later capability can produce false progress until Bazel resolves an actual target compiler/linker and developer commands stop treating printed reference commands as successful firmware work.

**Delivers:** Pinned Bazel/rules/tool versions, checksum-declared Rust 1.85.0 and Arm GNU 13.2.Rel1 toolchains, explicit MINI platform resolution, separate reference-only labels, thin truthful `just` recipes, and a real ARM link-smoke artifact.

**Addresses:** Truthful developer commands, explicit product target, real embedded toolchain, clean host/target separation.

**Avoids:** Print-only success, host builds mislabeled as firmware, Cargo/CMake/PATH fallback, and soft/hard-float drift.

### Phase 2: Pure `no_std` Safe-Boot Policy

**Rationale:** The boot, fault, and watchdog decisions should be exhaustively testable before MMIO and retained startup complexity are introduced.

**Delivers:** Fixed-size `safe-boot-core`, typed legal transitions, output-inhibition intent, fault convergence, watchdog feed/no-feed policy, and focused Arrange/Act/Assert host tests.

**Addresses:** Deterministic safe-boot state machine and host tests for pure boot/safety policy.

**Implements:** Functional core and capability-gated safety state.

**Avoids:** Happy-path-only safety, forgeable safe-ready state, allocation/`std` leakage, and policy buried in hardware effects.

### Phase 3: Retained Reset, Vector, and Link Boundary

**Rationale:** The runtime cannot be trusted until reset, vector placement, memory initialization, stack, flash origin, and the Rust handoff have exactly one declared owner.

**Delivers:** One MINI startup ASM veneer, explicit boot/no-boot labels, canonical boot linker selection, `rust_entry() -> !` contract, retained-boundary manifest, and structural link tests for vectors, `.data`, `.bss`, RAM, CCMRAM, stack, and boot exchange.

**Addresses:** Correct reset/vector/memory layout and explicit foreign-code bill of materials.

**Avoids:** Duplicate reset/vector symbols, hidden C constructors or `main`, environment-selected linker scripts, and behaviorally different images sharing an identity.

### Phase 4: MINI Hazardous-Output Adapter

**Rationale:** Exact BUDDY pin polarity and reset-state sequencing must be established before any clock, watchdog, or nonessential runtime work can safely precede the latch.

**Delivers:** Reviewed MINI pin/polarity data, sole unsafe MMIO module, latch-before-mode writes, idempotent `force_inhibit()`, adapter/reference-model tests, and an `OutputsInhibited` capability consumed by later startup.

**Addresses:** Earliest practical heater/motor inhibition and fault-safe output convergence.

**Avoids:** Generic HAL startup ahead of safety, wrong active polarity, transient assertion during mode changes, duplicated unsafe register code, and self-report-only safety.

### Phase 5: Rust Runtime, Faults, Watchdog, and Validated ELF

**Rationale:** With policy, reset, and GPIO boundaries established, Rust can own all executable behavior after the veneer and produce the first credible image.

**Delivers:** MINI `no_std`/`no_main` executable, panic/default-interrupt/HardFault handlers, watchdog healthy-service and expiry policy, terminal safe loop, genuine ELF/map, ABI and memory acceptance, required/forbidden symbol checks, and no hosted runtime dependencies.

**Addresses:** Real firmware binary, deterministic safe-ready runtime, terminal-path convergence, watchdog behavior, and inspectable embedded ELF acceptance.

**Avoids:** Divergent fault paths, accidental watchdog feeding, recursive fault behavior, allocator/unwinding/semihosting dependencies, and retained HAL/RTOS/application creep.

### Phase 6: Genuine Artifact Family and Immutable Provenance

**Rationale:** Packaging is credible only after an accepted ELF exists, and every derivative must preserve one verifiable identity.

**Delivers:** Declared ELF-rooted map/BIN/unsigned-development-BBF actions, BBF structure and payload validation, SHA-256 lineage, tool/platform/linker/source provenance, immutable current-run identity, and negative tests that reject fixture or stale fallback.

**Addresses:** Genuine artifact family, development-only identity, truthful build outputs, and artifact-to-evidence lineage.

**Avoids:** Fake maps, Phase 3 fixtures in production-looking filenames, stale directory reuse, split boot profiles, unsigned artifacts mistaken for release candidates, and successful fallback after a real action fails.

### Phase 7: MINI Simulator Scenarios and Fail-Closed Evidence

**Rationale:** Simulator acceptance must consume the exact validated artifact and independently observe each claim it reports before CI can qualify the bring-up.

**Delivers:** Purpose-built Mini404 MINI loader, cold-boot/safe-ready scenario, external GPIO observations where supported, panic/fault injection, watchdog starvation/reset/re-entry where supported, bounded timeouts, scenario-specific rows, redacted traces, and explicit `blocked`/`not_observed` gaps.

**Addresses:** Real-image simulation, independent safe-output observation, fault/watchdog scenarios, and honest non-hardware evidence.

**Avoids:** MK4/full-UI fixture reuse, arbitrary firmware paths, self-reported pass, unsupported observation promoted to pass, and simulator evidence presented as physical safety proof.

### Phase 8: Clean CI Qualification, Reference Comparison, and Rollback Freeze

**Rationale:** The milestone is complete only when a clean canonical environment reproduces the image and evidence while preserving the reference path and all production authority boundaries.

**Delivers:** Canonical Linux CI build/inspect/package/simulate pipeline, artifact and evidence retention on pass/failure, current/reference/archive root separation, stale-evidence regression tests, normalized CMake reference comparison, documented rollback selection, and final non-production claim audit.

**Addresses:** Clean-checkout CI, fail-closed evidence, structural reference comparison, and durable developer workflow.

**Avoids:** Local-only success, historical pass resurrection, CMake reference artifacts satisfying Rust gates, simulator overclaim, and accidental production-cutover or demotion authority.

### Phase Ordering Rationale

- Toolchain truth comes first because no runtime or artifact work is meaningful until Bazel produces target code itself.
- Pure policy precedes effects so legal boot/fault/watchdog behavior can be tested cheaply and the MMIO shell stays small.
- Reset/link ownership precedes GPIO/runtime integration because memory and vector ambiguity can prevent Rust from reaching the safety primitive.
- The hazardous-output boundary precedes nonessential initialization and is then reused by every terminal path.
- Structural ELF acceptance precedes BIN/BBF derivation and simulator execution; downstream consumers never accept a file by extension alone.
- Artifact lineage precedes evidence so every scenario and CI row can bind to the exact image it qualified.
- Simulator qualification precedes final CI/reference freeze, while physical safety remains an additive later gate rather than an implied consequence.
- CMake remains separately selectable throughout, providing comparison and rollback without weakening Bazel's authority over the Rust image.

### Research Flags

Phases needing focused `/gsd-research-phase` work during planning:

- **Phase 3:** Confirm the exact MINI boot/no-boot startup sources, handoff symbol spelling under Rust 2024, boot-exchange sections, and canonical linker/load contract from a real link.
- **Phase 4:** Review STM32F407 reset-state GPIO behavior, required peripheral clocks, latch-before-mode register sequence, and whether any pre-RAM/pre-clock inhibition must remain in assembly.
- **Phase 6:** Verify the unsigned BBF header, firmware/load offsets, metadata, and payload relationship against `utils/pack_fw.py` and a known reference artifact.
- **Phase 7:** Prove Mini404 support for the canonical boot layout, independent GPIO traces, fault injection, and watchdog observation before writing passing acceptance criteria.
- **Phase 8:** Specify immutable current/reference/archive evidence roots, failed-run publication behavior, and retention semantics so stale success cannot become current authority.

Phases with well-documented patterns that can skip standalone research unless implementation uncovers a new constraint:

- **Phase 1:** Official Bazel/rules documentation and repository evidence already define the pinning, platform, hermetic toolchain, and truthful-facade pattern.
- **Phase 2:** The functional-core, type-state, `no_std`, and focused host-unit-test approach is established by Bright Builds and Rust guidance.
- **Phase 5:** Panic-abort, symbol/ELF inspection, single runtime owner, and thin adapter patterns are established; use Phase 3/4 findings rather than reopening generic runtime research.

## Confidence Assessment

| Area | Confidence | Notes |
| --- | --- | --- |
| Stack | HIGH | Versions and target ABI are supported by official Bazel/rules/Rust/Arm documentation and align with repository manifests; the precise mixed Rust/ASM Starlark link shape remains implementation-validated. |
| Features | HIGH | Table stakes and anti-features derive directly from the v1.4 goal, current repository gaps, safe-state source, and existing fail-closed evidence contracts. |
| Architecture | HIGH | Reset/link boundaries, pin policy, artifact flow, and dependency direction are repository-backed and align with Bright Builds functional-core/type-safety rules. Mini404 observation mechanics remain MEDIUM. |
| Pitfalls | HIGH | ABI, reset, linker, GPIO, workflow, fixture, lineage, and stale-evidence risks are evidenced by current source and prior milestone machinery. |

**Overall confidence:** HIGH for milestone scope and roadmap sequencing; MEDIUM for simulator capability details and a few hardware/load-format facts that the flagged phases must prove.

### Gaps to Address

- **Mini404 load contract:** Determine whether it loads the canonical `0x08020200` boot-layout ELF/BIN directly or needs an explicit base-address adapter. Keep one firmware identity.
- **Mini404 observability:** Verify external GPIO, watchdog, reset-cause, and fault-injection support. Unsupported rows remain blocked rather than weakening acceptance to firmware self-report.
- **Earliest GPIO safety point:** Confirm reset-state registers, clock prerequisites, and whether output inhibition can occur safely immediately after Rust entry or requires a tiny pre-Rust action.
- **Mixed-language final-link mechanics:** Prove the dedicated Starlark action emits a genuine declared GNU map while preserving hard-float attributes and Rust/native symbol resolution.
- **BBF offsets and metadata:** Validate the exact unsigned container header and load/payload relationship against the established packer and reference image.
- **Darwin host support:** Resolve or explicitly document unsupported Apple-silicon Arm GNU/Mini404 paths; canonical Linux CI remains authoritative.
- **Physical safety:** v1.4 simulator evidence cannot prove electrical polarity, reset transients, or watchdog timing. Schedule an instrumented MINI hardware smoke as later evidence before any deployment decision.

## Sources

### Primary — Repository Evidence (HIGH confidence)

- `.planning/PROJECT.md` — v1.4 goal, four active requirements, and explicit no-production-cutover boundary.
- `.planning/research/STACK.md` — pinned stack, ABI, toolchain, artifact graph, alternatives, and host constraints.
- `.planning/research/FEATURES.md` — table stakes, anti-features, dependency graph, MVP boundary, and evidence expectations.
- `.planning/research/ARCHITECTURE.md` — reset/runtime ownership, component boundaries, hazardous-output type state, artifact flow, and implementation order.
- `.planning/research/PITFALLS.md` — critical failure modes, prevention gates, phase warnings, and research flags.
- `Cargo.toml` and `rust/crates/*/Cargo.toml` — Rust 1.85/edition 2024 floor and current host-oriented crate graph.
- `cmake/GccArmNoneEabi.cmake`, `cmake/AnyGccArmNoneEabi.cmake`, and `utils/bootstrap.py` — Cortex-M4F hard-float flags, Arm GNU 13.2.Rel1, and Mini404 0.9.10.
- `src/device/stm32f4/startup/` and `src/device/stm32f4/linker/stm32f407vg{,_boot}.ld` — reset/vector ownership and the two memory layouts.
- `src/hwio_safe_state/hwio_safe_state.cpp` and MINI/BUDDY pin definitions — current heater/motor safe values and polarity reference.
- `tools/bazel/toolchains/reference_toolchain.bzl`, `tools/bazel/reference_contract.sh`, and the `justfile` — current metadata-only/print-only boundaries.
- `tools/bazel/artifact_rules.bzl`, `tools/bazel/artifact_packager.py`, and `utils/pack_fw.py` — fixture risk and established BBF path.
- `utils/simulator/simulator.py`, `tests/integration/conftest.py`, and Phase 14/23/24 manifests — current simulator integration and simulator-versus-hardware claim boundaries.
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/verification.md`, `standards/core/testing.md`, and `standards/languages/rust.md` — repository workflow and applicable Bright Builds architecture, verification, testing, and Rust rules; no active local override changes the recommendation.

### Primary — Official External Documentation (HIGH confidence)

- [Bazel 9.2.0 release](https://github.com/bazelbuild/bazel/releases/tag/9.2.0) — pinned Bazel release.
- [Bazel platforms and toolchains](https://bazel.build/concepts/platforms) — explicit target/execution platform and toolchain resolution model.
- [Bazel hermeticity](https://bazel.build/concepts/hermeticity) — declared tools, inputs, outputs, and reproducibility expectations.
- [Bazel Central Registry: rules_rust](https://registry.bazel.build/modules/rules_rust) — 0.71.3 publication and Bazel compatibility.
- [rules_rust Bzlmod toolchains](https://bazelbuild.github.io/rules_rust/rust_bzlmod.html) — exact compiler version and extra target registration.
- [rules_rust rule reference](https://bazelbuild.github.io/rules_rust/rust.html) and [toolchain reference](https://bazelbuild.github.io/rules_rust/rust_toolchains.html) — Rust targets, linker scripts, native dependencies, and toolchain selection.
- [Bazel Central Registry: rules_cc](https://registry.bazel.build/modules/rules_cc) and [rules_python](https://registry.bazel.build/modules/rules_python) — pinned native and Python rule releases.
- [Rust Armv7E-M bare-metal targets](https://doc.rust-lang.org/stable/rustc/platform-support/thumbv7em-none-eabi.html) — Cortex-M4F hard-float target contract.
- [Embedded Rust Book: `no_std`](https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html) and [panicking](https://docs.rust-embedded.org/book/start/panicking.html) — bare-metal runtime and panic requirements.
- [Arm GNU Toolchain downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) — official 13.2.Rel1 toolchain family.
- [STM32F407VG datasheet](https://www.st.com/resource/en/datasheet/stm32f407vg.pdf) — Cortex-M4F, memory/peripheral, and watchdog facts.

### Secondary — Implementation Validation Required (MEDIUM confidence)

- [`cortex-m-rt` documentation](https://docs.rs/cortex-m-rt/latest/cortex_m_rt/) — useful comparison for future Rust-owned vectors/runtime; not selected for v1.4.
- Local Mini404 behavior — repository integration confirms the simulator lane, but exact MINI GPIO/watchdog/fault observability must be proved with the new image.

***

*Research completed: 2026-08-02*
*Ready for roadmap: yes — scoped to one development-only MINI safe-boot image with no production cutover*
