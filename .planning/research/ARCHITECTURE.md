# Architecture Research: Bazel-Native Rust Safe Boot

**Project:** Prusa Firmware Buddy Rust Port — milestone v1.4
**Domain:** STM32F407 embedded firmware bring-up
**Researched:** 2026-08-02
**Overall confidence:** HIGH for repository boundaries and build/link facts; MEDIUM for simulator observability until Mini404 is exercised with the new image

## Executive Decision

Build one MINI/BUDDY/STM32F407VG Rust safe-boot ELF with Bazel. Retain the existing STM32F407 startup assembly and linker layout as a narrow boot veneer, but have that veneer branch directly to a non-returning Rust entrypoint after `.data` and `.bss` initialization. From that symbol onward, Rust owns startup, hazardous-output inhibition, fault handling, and the idle/watchdog loop. Do not link C++ application code, Marlin, the full STM32 HAL, or FreeRTOS into this milestone image.

The safe-boot image must have no path that enables motion or heating. Its first board action writes safe output levels before configuring the corresponding GPIOs as outputs, then latches a typed `OutputsInhibited` state. Reset, panic, default interrupt, and hard-fault paths all converge on the same allocation-free, lock-free inhibition primitive.

Bazel must build the real cross-compiled ELF and own every derived artifact action. The map, raw binary, unsigned development BBF, hashes, and provenance manifest all derive from that same ELF. The existing CMake image remains a separately built reference oracle and rollback path; it is not linked into the Rust runtime and a successful reference build must not masquerade as a successful Rust build.

## Standard Architecture

### System Overview

```text
Developer / CI
      |
      v
 just (thin aliases only)
      |
      v
Bazel MINI platform + real Rust/ARM toolchain
      |
      +------------------------- reference-only ----------------------+
      |                                                               |
      v                                                               v
Rust safe-boot binary target                                  CMake reference build
      |                                                               |
      | links retained startup veneer + linker script                 |
      v                                                               |
ELF + map -------------------- metadata comparator <------------------+
      |
      +--> ELF/link validator --> objcopy --> BIN --> unsigned BBF
      |                                  \----------> provenance manifest
      |
      +--> Mini404 MINI safe-boot harness --> normalized observations
                                               |
                                               v
                                  fail-closed evidence aggregation
```

The runtime dependency direction is inward:

```text
mini-safe-boot executable
  -> safe-boot core (pure state machine and policy)
  -> MINI board adapter (unsafe MMIO contained here)
  -> runtime fault/watchdog adapter

safe-boot core -> no hardware, allocator, RTOS, HAL, filesystem, or networking
board/runtime adapters -> safe-boot core contracts, never application services
post-link tools -> ELF outputs; firmware code never depends on packaging or evidence
```

### Component Responsibilities

| Component | Change | Responsibility | Must Not Own |
| --- | --- | --- | --- |
| `safe-boot-core` Rust crate | New | `no_std` boot states, fault causes, and transition policy | MMIO, FFI, allocation, logging, or board pin numbers |
| MINI safe-boot executable | New | Compose the boot core with the MINI board and runtime adapters; export `rust_entry() -> !` | General printer behavior, C `main`, task scheduling, or artifact packaging |
| MINI board adapter | New or isolated from the existing host-oriented adapter | Exact BUDDY pin/polarity table and audited volatile MMIO for output inhibition | Boot sequencing policy or generic application state |
| Embedded runtime adapter | New narrow module/crate | Panic/default-interrupt/hard-fault convergence, watchdog policy, terminal idle/reset loop | GPIO policy, heap-backed diagnostics, or FreeRTOS |
| STM32F407 startup veneer | Retained, minimally modified or wrapped | Vector table, initial stack, `.data` copy, `.bss` zero, branch to `rust_entry` | C++ constructors, `main`, HAL startup, scheduler startup |
| STM32F407 linker scripts | Retained and declared to Bazel | Preserve flash/RAM regions, vector placement, boot exchange region, stack, and entry symbol | Product selection or implicit build-mode choice |
| Bazel Rust toolchain/platform | Replace metadata-only declaration | Resolve `thumbv7em-none-eabihf`, ARM linker/binutils, target constraints, and compilation flags | Calling host Cargo through a shell wrapper |
| Post-link artifact rules | New | Validate ELF/map, create `.bin`, unsigned development `.bbf`, hashes, and manifest | Fixture payloads, signing, flashing, or silent fallbacks |
| MINI safe-boot simulator harness | New | Run the real artifact with `MachineType.MINI`; observe reset, faults, watchdog, and hazardous outputs | Full GUI/WUI parity or MK4 fixtures |
| Evidence adapter | Extend | Normalize simulator results and preserve artifact/toolchain identity in the fail-closed pipeline | Converting unsupported hardware claims into pass |
| CMake reference comparator | Modify existing reference lane | Compare target identity, memory map, vector/reset symbols, safe pin policy, and BBF structure | Producing or certifying the Rust artifact |

## Rust-Owned Reset and Runtime Boundary

### Recommended Boundary

Retain the existing assembly vector/reset prologue for v1.4. It already expresses the repository's two critical layouts: the no-boot image at `0x08000000` and the bootloader application layout at `0x08020200`, along with current stack and RAM initialization behavior. Replace the call to C `main` with a single direct branch to an exported Rust symbol:

```rust
#[unsafe(no_mangle)]
pub extern "C" fn rust_entry() -> ! {
    // 1. Inhibit hazardous outputs.
    // 2. Enter the typed safe-boot state machine.
    // 3. Arm/serve the chosen watchdog policy.
    // 4. Remain in a non-operational loop.
}
```

The exact Rust 2024 unsafe-attribute spelling should be confirmed against the selected compiler; the architectural contract is one unmangled C-ABI symbol that cannot return. The assembly veneer owns only architectural entry and memory initialization. Rust owns all executable runtime behavior after the branch. There is no C `main`, constructor chain, HAL initialization sequence, or RTOS scheduler between reset and Rust.

Using `cortex-m-rt` for the reset/vector table is a sound future option, but not the lowest-risk first bring-up. Its vector-table and linker conventions differ from the repository's `.isr_vector` and bootloader layout. Replacing the veneer should be a later, separately evidenced change after vector addresses, boot exchange memory, fault behavior, and Mini404 startup have been compared.

### Retained Foreign-Code Policy

| Boundary | v1.4 decision | Rationale |
| --- | --- | --- |
| Startup ASM | Retain as a tiny Bazel dependency | Preserves reset/vector and bootloader compatibility while leaving runtime ownership in Rust |
| Linker script | Retain, with one explicit product mode per target | Memory layout is part of firmware compatibility, not build-system trivia |
| CMSIS | Retain constants/headers or a proven-minimal clock routine only if required | Avoid duplicating verified register facts; do not import a runtime framework by default |
| STM32 HAL | Do not link the full HAL | Safe boot needs only a small GPIO/watchdog surface; the HAL would widen the native dependency and startup boundary |
| FreeRTOS/CMSIS-RTOS | Do not link | Safe boot is deliberately single-threaded; scheduler bring-up belongs to a later milestone |
| C++/Marlin/GUI/network/storage | Reference-only | None is needed to prove Rust reset, safe outputs, faults, and artifact generation |
| `utils/pack_fw.py` format logic | Retain as a declared host tool initially | Reuse established BBF encoding while Bazel owns inputs and outputs; replace only with parity tests |
| ARM objcopy/readelf/size | Retain as declared toolchain utilities | Deterministic post-link conversion and validation require target-aware binary tools |

If clock initialization cannot be implemented safely from audited register writes, retain one narrowly named C/ASM clock function behind an explicit FFI target. Hazardous outputs must be inhibited before that call, and every failure path must return to Rust's safe terminal path. Do not retain a generic `HAL_Init()` escape hatch.

## Hazardous-Output Boundary

The MINI/BUDDY adapter must encode the reference safe values as data reviewed against the current implementation:

| Output | Pin | Safe level |
| --- | --- | --- |
| Hotend heater | PB1 | Low |
| Bed heater | PB0 | Low |
| X motor enable | PD3 | High (disabled) |
| Y motor enable | PD14 | High (disabled) |
| Z motor enable | PD2 | High (disabled) |
| E motor enable | PD10 | High (disabled) |

The MMIO sequence must set the output latch to the safe level before switching a pin to output mode, preventing a transient heater or motor-enable pulse. `force_inhibit()` must be idempotent and callable without initialized clocks, heap, locks, logging, or RTOS services. Only the board adapter may contain unsafe volatile access.

Model initialization as unforgeable transitions:

```text
ResetUnknown
   |
   | force_inhibit()
   v
OutputsInhibited
   |
   | optional clock/watchdog initialization
   v
SafeBootLatched

any fault/panic/default interrupt --> force_inhibit() --> FaultLatched/ResetLoop
```

The executable accepts only an `OutputsInhibited` token when entering the safe-boot loop. It exposes no heater-on, motor-enable, motion, or operational-mode API. Tests should prove that all modeled failure transitions converge on inhibition; simulator observation must prove the real pin values do so.

## Recommended Project Structure

```text
rust/
├── crates/
│   ├── safe-boot-core/          # new no_std state machine and policy
│   ├── board-adapter/           # existing contracts; isolate no_std MINI implementation
│   │   └── src/
│   │       ├── mini.rs
│   │       └── mini/
│   │           └── gpio.rs      # only unsafe MMIO owner
│   └── runtime-adapter/         # existing contracts plus isolated embedded fault path
└── firmware/
    └── mini-safe-boot/
        ├── BUILD.bazel
        └── src/main.rs

firmware/mini/
├── BUILD.bazel                  # image, artifact bundle, simulator labels
├── startup/                     # retained/overlay reset veneer
└── linker/                      # declared F407 linker inputs

tools/bazel/
├── rust/                        # real rules_rust toolchain registration
├── embedded/                    # ELF validation and objcopy actions
└── packaging/                   # BBF action and provenance manifest

tests/simulator/mini_safe_boot/
├── scenarios/                   # reset, fault, watchdog, output inhibition
└── evidence/                    # normalized fail-closed adapter
```

Keep the existing host-oriented domain/application crates and their tests intact. Do not make the first image depend on their `std`, `String`, and collection-heavy graph. Extract or add only the fixed-size, `no_std` state needed for safe boot. This preserves current evidence while preventing a broad embedded conversion from blocking bring-up.

## Link and Artifact Flow

Use one canonical bootloader-compatible linked ELF for the milestone unless Mini404 proves that the declared product profile requires a different loader contract. The bootloader mode, linker script, and flash origin must be explicit target attributes, never environment-driven choices.

```text
Rust sources + startup ASM + linker script
  -> rust_binary / embedded link action
  -> mini_safe_boot.elf + mini_safe_boot.map
  -> validate:
       ARM machine and hard-float ABI
       entry = Reset_Handler
       vector section address and size
       flash/RAM region bounds
       required rust_entry and fault symbols
       no forbidden C++/FreeRTOS/Marlin symbols
  -> objcopy -> mini_safe_boot.bin
  -> pack_fw.py --no-sign -> mini_safe_boot.bbf
  -> manifest with SHA-256, Bazel label, platform, toolchain, linker hash,
     source revision, artifact sizes, and validation results
```

The unsigned BBF must consume the real binary action output. Fixture-based Phase 3 artifacts remain test fixtures and cannot satisfy v1.4. Signing, DFU creation, and flashing remain outside the default graph. A packaging or validation failure must fail the Bazel target; no shell wrapper may print a reference command and exit successfully.

The repository's existing boot packaging uses distinct firmware and BBF load offsets. Preserve those rules through the established packer and validate the resulting header rather than assuming that the ELF flash origin is the BBF container address.

## Simulator and CI Data Flow

The existing integration fixture hardcodes an MK4 machine and expects a full application UI. It is not a valid safe-boot qualification path. Add a purpose-built Mini404 harness that selects `MachineType.MINI` explicitly and consumes the Bazel artifact manifest.

```text
Bazel artifact manifest + ELF/BIN
  -> Mini404 `prusa-mini`
  -> machine-readable observations
       reset reached safe latch
       PB0/PB1 remain low
       PD2/PD3/PD10/PD14 remain high
       injected fault re-inhibits outputs
       watchdog/reset returns to safe latch
  -> raw logs/traces
  -> normalizer + redactor
  -> scenario rows bound to artifact SHA-256 and simulator version
  -> existing fail-closed evidence aggregate
```

Prefer simulator GPIO/script traces over firmware self-report. A minimal test-only status channel may supplement those traces, but it cannot be the sole proof that physical outputs were inhibited. Record unsupported observations as `blocked` or `not_observed`, never `pass`. Hardware evidence remains explicitly pending after simulator success.

CI should execute these gates in order:

1. Resolve the MINI target platform and real Rust/ARM toolchain.
2. Run host tests for the pure safe-boot state machine and pin-policy model.
3. Cross-compile and link the real ELF.
4. Validate ELF, symbols, vector placement, and map bounds.
5. Derive the binary, unsigned BBF, hashes, and provenance manifest.
6. Run MINI safe-boot reset, fault, watchdog, and output scenarios.
7. Run reference metadata comparison against a separately built CMake image.
8. Publish a fail-closed evidence result even when a later gate fails.

## Reference Comparison and Rollback

CMake remains an oracle and an immediately available rollback path during v1.4. Comparison is structural and safety-focused, not byte-for-byte equality:

- Same MINI/BUDDY/STM32F407VG identity and explicit bootloader mode.
- Compatible flash/RAM origins, vector placement, stack, and boot exchange memory.
- Required reset and fault symbols.
- Same hazardous-output pins, polarities, and safe levels.
- Compatible unsigned BBF header and payload relationship.
- Recorded size deltas and section inventory, with thresholds rather than assumed equality.

Use separate, honest labels and commands such as `build-mini-safe-boot`, `simulate-mini-safe-boot`, and `compare-mini-reference`. The rollback action is selecting the established CMake reference target; there is no production cutover or automatic flash action in this milestone. Do not make the Rust target silently fall back to CMake.

## Implementation Order

1. **Make build labels truthful.** Preserve existing reference labels, but introduce a distinct real Rust image label whose success requires a real ELF.
2. **Install the executable toolchain.** Register `rules_rust`, `thumbv7em-none-eabihf`, ARM linker/binutils, and canonical target constraints; add a link-only smoke image.
3. **Create the pure safe-boot core.** Add fixed-size `no_std` states and host tests for every success/fault transition.
4. **Declare the retained boot boundary.** Build the startup veneer and linker script under Bazel; validate entry, vectors, RAM initialization, and the chosen boot profile.
5. **Implement the MINI hazardous-output adapter.** Add the pin table, latch-before-mode MMIO, idempotent force-inhibit path, and model/reference comparison tests.
6. **Link the Rust-owned runtime.** Export `rust_entry`, connect panic/fault/default-interrupt paths, and produce the first validated ELF/map.
7. **Derive real release-shape artifacts.** Create binary, unsigned BBF, hashes, and provenance from the same ELF.
8. **Add MINI simulator and evidence gates.** Exercise reset, injected fault, watchdog/reset, and pin states; keep hardware claims blocked.
9. **Freeze the reference comparison and rollback procedure.** Record deltas and demonstrate that CMake and Rust builds remain separately selectable.

This order preserves rollback at every step: no existing CMake reference path is replaced, and no derived artifact or simulator claim can exist before the real linked image passes structural validation.

## Architectural Patterns to Follow

### Functional Core, Imperative Boot Shell

Keep boot decisions and state transitions pure; place volatile writes, watchdog access, and terminal loops in thin adapters. This permits exhaustive host testing without weakening the real hardware boundary.

### Capability-Gated Safety State

Represent successful inhibition with an unforgeable value. Later startup code must consume that value, so an initialization reorder cannot accidentally skip the safe-output step.

### Single-Source Artifact Lineage

Treat the ELF as the root artifact. Every binary/container/hash/evidence record carries the same Bazel target and ELF digest. This prevents fixture or stale-artifact substitution.

### Explicit Foreign Boundary

Every retained ASM/C function is its own Bazel target with a documented symbol contract. A tiny declared veneer is reviewable; a generic native library glob is not.

## Anti-Patterns to Avoid

### Compiling the Entire Host Rust Workspace for Embedded

The current domain/application graph uses `std`, owned strings, and host collections. Forcing it onto the first image turns a reset-boundary milestone into a broad platform port. Extract only the fixed-size safe-boot core.

### Keeping C `main` as the Runtime Owner

Calling Rust from the existing C++ application shell does not demonstrate Rust reset/runtime ownership and leaves HAL/FreeRTOS initialization ahead of the safety proof.

### Linking Full HAL or FreeRTOS “For Later”

Unused native subsystems enlarge the binary, introduce constructors/interrupts, and obscure which runtime owns faults. Add them only with a milestone-specific contract and evidence.

### Two Behaviorally Different “Same” Images

Do not independently link a simulator image and a BBF image from different features or linker profiles. Teach the simulator adapter how to load the canonical ELF/BIN and record the load contract.

### Self-Reported Safety Only

A UART message saying “outputs disabled” does not prove GPIO state. Require external simulator observation where supported and preserve gaps honestly.

### Print-Only Build Success

A wrapper that prints a CMake/Cargo command and exits zero is metadata, not a build. User-facing build commands must produce validated outputs or fail.

## Scalability Considerations

| Concern | v1.4 MINI safe boot | Next board | Full firmware matrix |
| --- | --- | --- | --- |
| Product selection | One explicit Bazel platform and boot mode | Add a board implementation and linker profile | Generate reviewed platform facts from one manifest |
| Hazard policy | Fixed MINI pin table | Add typed per-board policy with shared tests | Matrix test every hazardous capability and polarity |
| Runtime | Single-threaded safe loop | Reuse boot/fault core | Introduce scheduler behind an adapter after safety latch |
| Artifacts | ELF/map/bin/unsigned BBF | Same lineage per target | Matrix provenance and release aggregation |
| Simulation | Mini404 MINI scenarios | Board-specific loader/observability adapter | Shared scenario vocabulary with honest capability gaps |

## Sources

### Repository evidence — HIGH confidence

- `src/device/stm32f4/startup/stm32f407xx.s` and `stm32f407xx_boot.s` — current vector/reset and memory-init boundary.
- `src/device/stm32f4/linker/stm32f407vg.ld` and `stm32f407vg_boot.ld` — memory regions, entry, vector, boot exchange, and stack layout.
- `src/hwio_safe_state/hwio_safe_state.cpp` and MINI/BUDDY pin definitions — current hazardous-output safe values.
- `tools/bazel/toolchains/reference_toolchain.bzl`, `tools/bazel/shell_rules.bzl`, and `tools/bazel/reference_contract.sh` — current metadata-only and print-only Bazel boundaries.
- `rust/crates/*/Cargo.toml` and source — current host-oriented dependency graph and deferred embedded wiring.
- `utils/simulator/simulator.py` and `tests/integration/conftest.py` — Mini404 integration and current MK4-oriented fixture.
- `utils/pack_fw.py`, `CMakeLists.txt`, and `cmake/Utilities.cmake` — current BIN/map/BBF flow.

### External primary documentation — HIGH confidence

- [rules_rust overview and Bzlmod setup](https://bazelbuild.github.io/rules_rust/)
- [rules_rust target triples with Bzlmod](https://bazelbuild.github.io/rules_rust/rust_bzlmod.html)
- [rules_rust toolchain configuration](https://bazelbuild.github.io/rules_rust/rust_toolchains.html)
- [rules_rust `rust_binary`, linker scripts, and native link dependencies](https://bazelbuild.github.io/rules_rust/rust.html)
- [Rust `thumbv7em-none-eabihf` target support](https://doc.rust-lang.org/nightly/rustc/platform-support/thumbv7em-none-eabi.html)
- [Bazel platforms and toolchain resolution](https://bazel.build/versions/9.1.0/concepts/platforms)

### External crate documentation — MEDIUM confidence

- [`cortex-m-rt` reset and vector-table behavior](https://docs.rs/cortex-m-rt/latest/cortex_m_rt/) — supports the future pure-Rust alternative; repository-specific boot compatibility still requires local validation.

## Open Questions for Phase Planning

- Whether Mini404 can load the canonical bootloader-layout ELF directly or needs an explicit raw-binary base-address adapter. Resolve before finalizing the simulator action, not by producing a second linked image.
- Whether the board's hardware watchdog can be observed or injected in Mini404. If not, keep the hardware watchdog scenario blocked and separately test the Rust reset/fault policy.
- Whether safe startup requires any clock routine before GPIO inhibition on the actual STM32F407/BUDDY hardware. Review the reset-state register assumptions and datasheet during phase research.
- The exact unsigned BBF header/load-offset relationship for the canonical boot profile. Validate the packer output against the existing reference artifact.

## Confidence Assessment

| Area | Confidence | Reason |
| --- | --- | --- |
| Dependency direction and component boundaries | HIGH | Derived from current crate, Bazel, CMake, linker, and startup sources |
| Reset/link/artifact architecture | HIGH | Existing reset/linker and packaging paths are explicit; external toolchain capabilities are documented |
| Hazard pin policy | HIGH | Current safe-state code and board pin definitions provide a direct reference |
| Simulator data flow | MEDIUM | Mini404 supports the MINI machine, but exact GPIO/watchdog observability needs implementation-time proof |
