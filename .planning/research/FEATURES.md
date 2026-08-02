# Feature Research

**Domain:** Safety-conscious Bazel-native embedded Rust firmware bring-up for `MINI/BUDDY/STM32F407VG`
**Researched:** 2026-08-02
**Confidence:** HIGH for the required capability set and current repository gap; MEDIUM for the exact Mini404 observation hooks until they are exercised against the new image

## Scope and User

The “users” of this milestone are firmware developers, safety reviewers, release-artifact reviewers, and CI maintainers. A credible bring-up does not need to print, render the production GUI, connect to cloud services, or replace every foreign component. It does need to prove that Bazel produced a real MCU image, that the image starts deterministically on the selected MINI platform, that hazardous outputs remain inhibited, and that the proof is observable outside the firmware’s own claims.

Milestone acceptance must remain explicitly narrower than production readiness. Passing v1.4 means “the first Rust image is real and safely testable.” It does not mean “the Rust firmware has feature parity,” “the image is safe on physical hardware,” “the package is release-signed,” or “reference demotion is authorized.”

## Observed Baseline

The repository already provides strong domain models and evidence plumbing, but its build/runtime surfaces are not yet an embedded bring-up:

- `//platforms:mini_buddy_stm32f407vg` models the product/board/MCU constraints, but the registered firmware “toolchains” are `reference_toolchain` metadata providers rather than Rust/C/ASM compilers and linkers.
- `just build` runs `//tools/bazel:build_firmware`, which exits successfully after printing `python3 utils/build.py` while `BUDDY_BAZEL_EXECUTE_REFERENCE=0` remains the default.
- `just simulator-parity` likewise prints a reference pytest command containing `<firmware.bin>` rather than booting an artifact.
- `//tools/bazel:rust_firmware` builds the host Rust workspace; the current crates are libraries and the runtime adapter explicitly says it does not boot STM32 startup code or FreeRTOS.
- Phase 3 `.bin` and `.map` outputs are deterministic package-surface fixtures marked with `BUDDY_PHASE3_PACKAGE_SURFACE_FIXTURE`; they are not linked MCU artifacts.
- `.github/workflows/ci-evidence.yml` currently writes Phase 19 evidence but does not cross-compile or boot a Rust firmware image.
- The reference firmware already defines the safety target: `hwio_safe_state()` drives fans to their safe state, turns hotend and bed heat off, and disables motors. The existing evidence schemas already distinguish simulator observations from required physical-hardware proof.

These gaps make truthful execution, genuine artifact lineage, independent safe-output observation, and fail-closed claim boundaries table stakes rather than polish.

## Feature Landscape

### Table Stakes (Maintainers Expect These)

Missing any P1 row below makes the bring-up incomplete or misleading.

| Feature | Why Expected | Complexity | Notes |
| --- | --- | --- | --- |
| Truthful developer commands | `just build`, `just test`, and the simulator command must either perform the named work or exit nonzero; a printed recipe is not a build/test result. | MEDIUM | Preserve stable `just` entrypoints, but make their completion messages name the Bazel target and real output/evidence paths. Keep reference-only commands separately named. |
| One explicit product target | Developers need one unambiguous authority label for `MINI/BUDDY/STM32F407VG`, not a generic host workspace build. | MEDIUM | The existing platform label is the correct selection key. Unsupported platform selections should fail during analysis rather than silently fall back to host or CMake behavior. |
| Real pinned embedded Rust toolchain | Bazel must invoke a known Rust compiler/sysroot/linker for the MCU target instead of exposing metadata-only toolchains. | HIGH | STM32F407 is Cortex-M4 with a single-precision FPU. Select and lock the ABI deliberately; `thumbv7em-none-eabihf` is the conventional hard-float target, but retained C/ASM ABI compatibility must decide the final choice. |
| Bazel-owned `no_std`/`no_main` firmware binary | A host `rlib` or Cargo workspace build cannot boot an MCU. | HIGH | Add an actual binary crate and Bazel Rust rule. It needs a non-returning entrypoint, exactly one panic handler, and no accidental `std` dependency. |
| Correct reset, vector, and memory layout | A linked ARM file is not bootable unless its reset vector, exception vectors, stack, flash/RAM regions, bootloader offset, and sections match the selected MINI image mode. | HIGH | Reuse or explicitly replace the retained STM32F407 startup/linker ownership. Check vector-table placement and `Reset`/`Reset_Handler`, stack start, `.text`, `.data`, `.bss`, and load addresses from the ELF/map. |
| Inspectable embedded ELF acceptance | Reviewers need machine proof that the output is a 32-bit little-endian ARM executable for the intended ABI and memory map. | MEDIUM | Validate architecture, entrypoint, loadable segments, vector section/symbols, section ranges, image size, and absence of fixture markers. A filename ending in `.elf` is insufficient. |
| Genuine artifact family from one link | The milestone promises ELF, map, bin, and unsigned development BBF artifacts, all derived from the same embedded image. | HIGH | `bin` must be extracted from ELF loadable content; the map must come from the actual link; BBF must wrap that bin through the repository’s reference-format packer. Do not substitute Phase 3 fixture payloads. |
| Artifact identity and development-only provenance | Maintainers must be able to prove which source, toolchain, platform, and ELF produced each derivative without mistaking it for a production release. | MEDIUM | Emit hashes, sizes, target triple/ABI, Bazel labels, source revision, linker script identity, retained-component identities, and `unsigned-development`/`non-production` classification. Cross-check ELF→bin→BBF hashes. |
| Deterministic safe-boot state machine | The first image must reach a bounded, named safe-ready state rather than merely loop somewhere after reset. | HIGH | Recommended observable sequence: reset entered → earliest safe-output write → memory/runtime init → retained-boundary init if required → watchdog armed → safe outputs verified → safe-ready heartbeat/quiescent loop. Transitions should be typed and host-tested. |
| Earliest practical hazardous-output inhibition | Heaters and motion enables must be driven inactive before nonessential initialization can fail or hang. | HIGH | Match the reference polarity and behavior for MINI: hotend heat off, bed heat off, X/Y/Z/E motor enables disabled, fans in the documented safe state. If pre-RAM action is needed, keep it in retained/generated assembly or narrowly reviewed unsafe code; do not assume ordinary Rust can safely run before RAM initialization. |
| Independent safe-output observation | A firmware log saying “outputs safe” cannot be its own only proof. | HIGH | Simulator evidence should inspect modeled GPIO/PWM/peripheral state or a Mini404 trace after each critical transition. A firmware marker may delimit the observation point, but pass/fail must be derived by the harness. |
| Panic, HardFault, and unexpected-interrupt convergence | A credible bring-up defines what happens when Rust panics, the CPU HardFaults, or an unhandled interrupt fires. | HIGH | Each fatal path must be non-returning, attempt safe outputs using a bounded allocation-free path, emit a distinguishable sanitized marker when possible, and then halt or await watchdog reset. Test at least one Rust panic and one CPU/exception fault path. |
| Watchdog normal and expiry behavior | STM32F407 provides an independent watchdog specifically to reset the device when software stops progressing; ignoring it leaves the safe-loop claim weak. | HIGH | Arm IWDG in the embedded image, feed it only from an explicit healthy safe-ready condition, inject starvation, observe reset cause/count, and prove the reboot re-enters safe state. Simulator timing is evidence for logic, not physical timeout calibration. |
| Real-image Mini404 startup scenario | The existing simulator machinery is only relevant to v1.4 if it boots the newly linked image. | HIGH | Pass the real ELF/bin to `qemu-system-buddy`; pin the `MINI` machine, CPU assumptions, arguments, and dependency identity. Use bounded timeouts and fail on early exit, hang, missing safe-ready, or unsafe output. |
| Simulator fault/watchdog/safe-output scenario set | One happy-path boot does not exercise the safety contract named by the milestone. | HIGH | Minimum set: cold reset to safe-ready, panic/fault convergence, watchdog starvation/reset/re-entry, and hazardous-output inhibition throughout. Keep each scenario’s status and artifacts separate. |
| Host tests for pure boot/safety policy | Hardware adapters are effectful, but transition policy and watchdog-feed eligibility should be cheap to test exhaustively. | MEDIUM | Follow the existing functional-core/imperative-shell split. Unit-test legal state transitions, failure convergence, output intent, and feed/no-feed decisions; adapter integration belongs in simulator checks. |
| Explicit retained-boundary bill of materials | Retained startup, linker, CMSIS, HAL, ASM, RTOS, or C helpers must be visible rather than quietly linked. | MEDIUM | For each retained component record owner, exact source/label, reason, ABI, unsafe/FFI surface, initialization order, safety responsibility, test evidence, and replacement/defer decision. Confirm actual linked symbols against the declaration. |
| Clean-checkout CI build and simulator gate | A local-only bring-up is not credible if CI cannot recreate it from declared inputs. | HIGH | CI must cross-build, inspect ELF/map, derive artifacts, run host tests and Mini404 scenarios, and retain redacted logs/manifests. Missing simulator/toolchain prerequisites must fail or produce an explicitly blocked non-passing job, never a green placeholder. |
| Fail-closed evidence and claim vocabulary | Existing evidence machinery relies on distinguishing passed, failed, blocked, and exception-requested results. | MEDIUM | Real-image rows must carry artifact identity and source refs. Simulator pass must retain residual `pending-hardware`/manual-hardware boundaries and must not alter production cutover or reference-demotion authority. |

### Differentiators (Valuable After the P1 Bring-Up)

| Feature | Value Proposition | Complexity | Notes |
| --- | --- | --- | --- |
| Byte-for-byte reproducible development artifacts | Two clean builds with identical source/config producing equal ELF/bin/BBF hashes makes the Bazel authority unusually strong and exposes timestamp/path leakage early. | HIGH | First make actions hermetic and use stable provenance separate from volatile run metadata. Cross-host reproducibility can follow same-host double-build proof. |
| Link-time flash/RAM/stack budgets | Prevents a “boots once” image from growing beyond the STM32F407VG envelope and makes map review actionable. | MEDIUM | Gate flash/RAM section ranges immediately; add policy thresholds and stack-paint/high-water evidence after the safe runtime is stable. |
| Typed, machine-readable boot trace | Gives reviewers one canonical transition ledger shared by host tests, simulator assertions, and CI evidence. | MEDIUM | Prefer stable state/reason enums and monotonic sequence numbers over free-form logs. Treat it as diagnostics, not sole safety proof. |
| Reference-image structural comparison | Shows intentional differences in vector placement, memory use, package metadata, and safe-output polarity without demanding byte identity between Rust and C++. | MEDIUM | Compare normalized facts, not raw binaries. Any behavior-parity claim remains deferred. |
| Expanded deterministic fault-injection matrix | Exercises default interrupts, invalid memory access, assertion/panic, retained-boundary failure, and watchdog edge cases before full firmware complexity arrives. | HIGH | Add only once the minimum panic/HardFault/watchdog scenarios are stable and independently observable. |
| Physical MINI safe-output smoke with instrumentation | Adds electrical evidence that GPIO polarity and reset behavior match the real board. | HIGH | Valuable next gate, but it requires hardware, operator procedure, probes/fixtures, and existing Phase 24 evidence handling. It does not belong in the minimum simulator/CI bring-up definition. |
| Flash/debug developer facade | A discoverable `just flash-mini-dev` or debug-server command shortens hardware iteration and ties the flashed image to provenance. | MEDIUM | Must require an explicit development target/device and never auto-flash production hardware from normal build/test commands. |
| Build Event Protocol or action-graph provenance | Provides strong audit links from CI outputs back to the exact Bazel actions and toolchain. | MEDIUM | Add after the essential artifact manifest exists; avoid making a dashboard a prerequisite. |
| Differential safe-output trace against C reference | Detects polarity/order drift while the Rust runtime is still small. | HIGH | Compare normalized simulator traces for only the safe-boot envelope. Do not expand the comparison into full printer behavior in v1.4. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
| --- | --- | --- | --- |
| All printer/board targets in the first bring-up | Feels closer to eventual parity. | Multiplies linker, startup, HAL, simulator, and safety variables before one vertical slice works. | Make `MINI/BUDDY/STM32F407VG` real and keep other platforms explicitly unsupported by the new target. |
| Printing, motion commands, or heating | Demonstrates visible printer usefulness. | Authorizing hazardous actuation changes the safety envelope and expands into Marlin/planner/thermal parity. | Keep all motion and heating commands unavailable; prove their outputs remain inhibited. |
| Production GUI, networking, storage, Connect, or transfer flows | Existing evidence contracts already mention these capabilities. | These are full-parity concerns, not prerequisites for reset-to-safe bring-up. They also introduce large retained dependency graphs. | Emit a minimal simulator/debug boot marker and defer application services. |
| Signed or release-publishable BBF | Makes the artifact look complete. | Pulls private-key handling, release authorization, device installation policy, and rollback risk into a development milestone. | Produce a structurally valid unsigned development BBF with an unmistakable non-production classification. |
| Production flashing, rollout, cutover, or reference demotion | Converts the bring-up into a practical deployment. | v1.4 has neither feature parity nor physical safety proof, and prior milestones keep these authorizations independent and fail-closed. | Retain C/C++ production firmware and all demotion/cutover gates unchanged. |
| Full Rust replacement of startup/HAL/CMSIS/ASM/FreeRTOS | Maximizes Rust ownership immediately. | Rewrites multiple safety-critical boundaries before the Rust image can provide evidence; it obscures whether failures are build, ABI, startup, or application defects. | Retain narrowly justified components behind explicit Bazel/FFI boundaries and replace them in later, evidence-driven work. |
| Introduce a new async executor or RTOS architecture | Modern embedded Rust ecosystems make this attractive. | It adds scheduling, interrupt, timer, and memory decisions unrelated to proving safe boot and may conflict with future parity architecture. | Use the smallest deterministic loop or explicitly retained runtime needed for safe bring-up. |
| Let CMake/Python fallback satisfy Bazel build success | Keeps developer commands working while Bazel matures. | A green command would no longer prove Bazel built the Rust image; authority remains ambiguous. | Give reference builds a clearly named compatibility command and make the Bazel firmware command fail when its own target fails. |
| Keep fixture payloads behind production-looking filenames | Existing Phase 3 fixtures are deterministic and convenient. | `.bin`, `.map`, and `.bbf` extensions can mislead reviewers even though no MCU link occurred. | Reject the fixture marker and require all derivatives to trace to the accepted embedded ELF. |
| Self-reported safe outputs only | Easy to add as a log line. | The same broken code that leaves a heater enabled can print that it disabled it. | Combine a firmware transition marker with independent simulator GPIO/PWM observation. |
| Treat simulator pass as physical safety qualification | Avoids scarce hardware work. | Emulation cannot prove board-level pull states, electrical polarity, power transients, or physical watchdog timing. | Preserve explicit residual hardware gates and schedule instrumented hardware smoke separately. |
| Full crash-dump/recovery parity | Rich failure artifacts are useful. | CrashCatcher, storage, UI, and recovery flows expand far beyond panic/fault convergence for a first image. | Emit bounded sanitized fault identity and prove safe halt/watchdog reset; defer full dump compatibility. |
| Byte identity with the C/C++ firmware | Sounds like the strongest compatibility proof. | Different languages, linkers, runtimes, and ownership boundaries make binary equality meaningless. | Compare normalized memory/package/safe-output facts and later compare observable behavior. |
| Automatic evidence approval from a green CI job | Reduces maintainer steps. | Conflates bring-up evidence with production readiness and demotion authority. | Publish scoped evidence rows only; keep all prior explicit decision predicates intact. |

## Feature Dependencies

```text
[Truthful developer facade]
└──requires──> [Repaired Bazel graph]
                 └──requires──> [Pinned embedded Rust toolchain + MINI platform]
                                    └──requires──> [no_std/no_main firmware target]
                                                       └──requires──> [Linker/startup ownership]
                                                                          └──produces──> [Accepted ELF + real map]
                                                                                              └──produces──> [bin + unsigned dev BBF]
                                                                                                                  └──requires──> [Artifact lineage/provenance]

[Retained-boundary declaration] ──constrains──> [Linker/startup ownership]
[MINI pin polarity + reference safe state] ──requires──> [Earliest safe-output adapter]
[Pure typed boot policy] ──drives──> [Deterministic safe-boot runtime]
[Earliest safe-output adapter] ──requires──> [Deterministic safe-boot runtime]
[Panic/HardFault convergence] ──requires──> [Earliest safe-output adapter]
[Watchdog feed/expiry policy] ──requires──> [Deterministic safe-boot runtime]

[Accepted ELF + real map] ──requires──> [Real-image Mini404 runner]
[Independent simulator observation] ──requires──> [Real-image Mini404 runner]
[Fault injection + watchdog starvation] ──requires──> [Real-image Mini404 runner]
[Safe-boot, fault, watchdog scenarios] ──produce──> [Fail-closed evidence rows]

[Clean-checkout CI]
├──requires──> [Truthful developer facade]
├──requires──> [Artifact lineage/provenance]
├──requires──> [Host policy tests]
└──requires──> [Safe-boot, fault, watchdog scenarios]

[Production signing/cutover] ──conflicts──> [v1.4 development-only bring-up scope]
[Full feature parity] ──conflicts──> [single-platform safe vertical slice]
[Physical hardware qualification] ──enhances──> [simulator evidence; does not replace or retroactively broaden it]
```

### Dependency Notes

- **The Bazel graph and embedded toolchain precede runtime work:** until Bazel owns a compiler, target sysroot, linker, and output-producing rule, all later “firmware” capabilities can accidentally remain host or reference wrappers.
- **ABI choice precedes retained-code linkage:** hard-float versus soft-float must agree across Rust and any retained C/ASM objects. The STM32F407VG has a single-precision FPU, but hardware capability alone does not prove the retained ABI.
- **Safe-output polarity precedes boot-state implementation:** output intent is not enough; MINI pin polarity and reset behavior determine which writes actually inhibit heaters and motors.
- **ELF acceptance precedes packaging and simulation:** bin/BBF extraction and Mini404 execution must consume only an ELF that passed architecture, memory, vector, and anti-fixture checks.
- **Independent observation precedes a safety pass:** the firmware may publish state markers, but simulator/hardware adapters must decide whether output states satisfy the contract.
- **Normal watchdog service and starvation are one feature:** proving only that the image pets the watchdog can hide a dead watchdog; proving only reset can hide a reset loop. Both healthy service and deliberate expiry/re-entry are required.
- **CI consumes existing evidence machinery:** v1.4 should add real-image producer rows and artifacts, then reuse fail-closed normalization/redaction patterns. It should not redesign cutover approval.
- **Hardware proof remains additive:** simulator evidence can validate deterministic logic and modeled peripherals; electrical and physical timing claims remain blocked until a separate hardware run supplies them.

## MVP Definition

For this research, “MVP” means the minimum v1.4 milestone acceptance packet, not a production firmware launch.

### Launch With (v1.4)

- [ ] `just build` builds one Bazel-native embedded Rust target for `MINI/BUDDY/STM32F407VG` and names its outputs; failure is nonzero.
- [ ] The target is a real `no_std`/`no_main` Cortex-M4 image built by a pinned Bazel Rust toolchain with deliberate ABI selection.
- [ ] ELF inspection proves ARM architecture, entry/vector placement, memory ranges, linked ownership, and absence of Phase 3 fixture content.
- [ ] Bazel emits a genuine ELF, link map, bin, unsigned development BBF, and machine-readable lineage/provenance bundle.
- [ ] The runtime drives MINI hotend heat off, bed heat off, X/Y/Z/E motor enables disabled, and fans to the documented safe state before nonessential work.
- [ ] The runtime reaches a deterministic safe-ready state and remains quiescent with hazardous commands unavailable.
- [ ] Panic, HardFault/unhandled exception, and watchdog expiry converge on safe outputs and an observable non-returning/reset path.
- [ ] Mini404 boots the real image and independently verifies safe-ready, hazardous-output inhibition, fault convergence, and watchdog reset/re-entry.
- [ ] Host tests cover the pure boot-state and watchdog-feed policy.
- [ ] Retained startup/HAL/CMSIS/ASM/RTOS/C boundaries are declared and checked against the actual link.
- [ ] CI repeats build, ELF/artifact inspection, host tests, simulator scenarios, and redacted evidence retention from a clean checkout.
- [ ] Every output and evidence row is labeled development-only; physical safety, production cutover, and reference demotion remain blocked.

### Add After Validation (v1.x)

- [ ] Same-host then cross-host reproducibility proof — add after artifact timestamps, paths, and provenance fields stabilize.
- [ ] Enforced flash/RAM/stack budgets — add once the first real map establishes a defensible baseline.
- [ ] Broader deterministic fault injection — add after the minimum panic/HardFault/watchdog scenarios are reliable.
- [ ] Instrumented physical MINI safe-output smoke — add when board access, measurement procedure, and operator evidence inputs are available.
- [ ] Explicit flash/debug facade — add when hardware iteration begins; keep it opt-in and development-only.
- [ ] Normalized structural comparison with the C reference — add after Rust artifact facts are stable enough to avoid noisy comparisons.

### Future Consideration (Later Milestones)

- [ ] Additional printer/board/MCU targets — defer until the MINI vertical slice establishes reusable toolchain, boundary, and evidence patterns.
- [ ] FreeRTOS/task orchestration and application services — defer until safe bare-metal/retained-runtime bring-up is trustworthy.
- [ ] Printing, thermal control, motion planning, GUI, persistence, networking, Connect, PrusaLink, and transfers — these are parity work, not bring-up.
- [ ] Full crash-dump and recovery compatibility — defer until the runtime can safely own storage and recovery paths.
- [ ] Signed release candidate and installation flows — defer to an explicitly authorized release/cutover milestone with physical evidence.
- [ ] Replacement of retained vendor/HAL/ASM components — replace boundary by boundary only when evidence shows replacement risk is lower than retention risk.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
| --- | --- | --- | --- |
| Truthful `just`/Bazel commands | HIGH | MEDIUM | P1 |
| Pinned cross-compiling Rust toolchain | HIGH | HIGH | P1 |
| `no_std`/`no_main` MINI firmware target | HIGH | HIGH | P1 |
| Linker/vector/memory ownership and ELF validation | HIGH | HIGH | P1 |
| Genuine ELF/map/bin/unsigned BBF lineage | HIGH | HIGH | P1 |
| Deterministic safe-boot state | HIGH | HIGH | P1 |
| Earliest hazardous-output inhibition | HIGH | HIGH | P1 |
| Panic/HardFault/default-handler convergence | HIGH | HIGH | P1 |
| Watchdog healthy-service and expiry/re-entry proof | HIGH | HIGH | P1 |
| Independent Mini404 safe-output observation | HIGH | HIGH | P1 |
| Host boot/safety policy tests | HIGH | MEDIUM | P1 |
| Explicit retained-boundary bill of materials | HIGH | MEDIUM | P1 |
| Clean-checkout CI and retained redacted evidence | HIGH | HIGH | P1 |
| Fail-closed non-hardware/non-production claims | HIGH | MEDIUM | P1 |
| Byte reproducibility | MEDIUM | HIGH | P2 |
| Memory and stack budgets | MEDIUM | MEDIUM | P2 |
| Physical MINI safe-output smoke | HIGH | HIGH | P2 |
| Expanded fault matrix | MEDIUM | HIGH | P2 |
| Flash/debug facade | MEDIUM | MEDIUM | P2 |
| Additional product targets | HIGH eventually | HIGH | P3 |
| Printing/application parity | HIGH eventually | HIGH | P3 |
| Production signing/cutover | HIGH eventually | HIGH | P3 |

**Priority key:**

- P1: Required for v1.4 acceptance
- P2: Valuable after the first credible bring-up is stable
- P3: Later parity, release, or cutover milestone

## Baseline Approach Comparison

| Capability | Current C/C++/CMake Reference | Current Rust/Bazel Surface | Recommended v1.4 Approach |
| --- | --- | --- | --- |
| Firmware build | Produces supported production firmware through `utils/build.py` and CMake. | `build_firmware` prints the reference command by default; `rust_firmware` builds host libraries. | One real Bazel `rust_binary`/equivalent embedded target selected by the MINI platform. |
| Startup/runtime | Mature STM32 startup, HAL, CMSIS, FreeRTOS, and application task graph. | Typed contracts describe retained surfaces; no Rust MCU entrypoint exists. | Small Rust-owned safe-boot state machine with explicitly retained minimum startup/ABI boundaries. |
| Safety outputs | `hwio_safe_state()` turns heaters off, disables motors, and sets fans safe. | Pure Rust safety models classify the behavior but do not drive pins. | Implement the MINI safe-output adapter and verify its actual simulator-visible state before safe-ready. |
| Fault/watchdog | Existing fatal/crash/watchdog code includes IWDG handling and hardware evidence boundaries. | Boundary contracts name the symbols and evidence classes only. | Minimum panic/HardFault/watchdog implementation with normal service, injected expiry, safe reset, and retained residual hardware proof. |
| Artifacts | Real `.bin`, `.bbf`, `.dfu`, `.map`, and resources. | Phase 3 produces deterministic fixture package surfaces. | ELF/map/bin/unsigned dev BBF derived from one accepted Rust ELF, with hashes and non-production provenance. |
| Simulator | Existing integration harness can launch Mini404 with a firmware kernel and script I/O. | Evidence contracts can ingest real rows, but default commands do not boot a Rust image. | Boot the new image directly, inspect modeled outputs, inject minimum faults, and publish scenario-specific evidence. |
| CI | Jenkins/reference flows build production C/C++; GitHub evidence workflow emits evidence packets. | No GitHub job cross-builds and boots embedded Rust. | Clean-checkout cross-build + artifact inspection + host tests + real-image Mini404 job, retaining redacted artifacts even on failure. |
| Claim boundary | Production reference behavior is real but separate cutover decisions are required. | Evidence tooling is deliberately fail-closed. | Reuse fail-closed statuses and preserve `pending-hardware`, production-cutover, and demotion boundaries. |

## Evidence and Confidence Assessment

| Area | Confidence | Basis |
| --- | --- | --- |
| Current repository gap | HIGH | Direct execution and inspection of Bazel labels, `justfile`, `reference_contract.sh`, Rust crates, artifact packager, simulator harness, and CI workflow. |
| Bare-metal Rust requirements | HIGH | Rust target documentation, Rust Reference, Embedded Rust Book, and `cortex-m-rt` documentation agree on `no_std`, entry/panic ownership, target triple, vector table, linker memory layout, and ELF inspection. |
| STM32F407 target/watchdog facts | HIGH | Current ST datasheet identifies Cortex-M4 with single-precision FPU and describes IWDG as an independent-clock reset mechanism. |
| Bazel toolchain and hermetic artifact expectations | HIGH | Current official `rules_rust` and Bazel documentation describe registered toolchains, Rust binary rules, declared outputs/actions, sandboxing, and reproducibility. |
| Safe-output scope | HIGH | Direct reference implementation in `src/common/safe_state.cpp` and existing Phase 6/15/24 safety contracts. |
| Exact Mini404 GPIO/watchdog probes | MEDIUM | The local harness proves real-kernel launch and script I/O, but the exact independent observation/fault-injection command set for the new minimal image must be confirmed during phase research. If Mini404 lacks a needed probe, add a narrow emulator trace hook or keep that row blocked; do not downgrade to self-report. |

## Sources

### Repository Sources (HIGH confidence)

- `.planning/PROJECT.md` and `.planning/STATE.md` — v1.4 goal, active requirements, and explicit no-cutover boundary.
- `.planning/milestones/v1.3-REQUIREMENTS.md` and `.planning/milestones/v1.3-MILESTONE-AUDIT.md` — fail-closed evidence, separate demotion approval, and accepted non-local evidence limits.
- `MODULE.bazel`, `.bazelrc`, `platforms/BUILD.bazel`, `tools/bazel/toolchains/BUILD.bazel`, and `tools/bazel/toolchains/reference_toolchain.bzl` — modeled platform and metadata-only toolchains.
- `justfile`, `tools/bazel/reference_contract.sh`, and `tools/bazel/rust_workflow.sh` — current printed reference commands and host Rust workflow.
- `tools/bazel/artifact_rules.bzl`, `tools/bazel/artifact_packager.py`, and `tools/bazel/fixtures/firmware_payloads/` — fixture artifact surfaces and reference-format wrapper behavior.
- `rust/crates/runtime-adapter/src/startup.rs`, `rust/crates/runtime-adapter/src/panic_boundary.rs`, `rust/crates/domain/src/safety.rs`, and the crate manifests — typed contracts without an embedded binary runtime.
- `src/common/safe_state.cpp`, `src/common/wdt.cpp`, `src/buddy/main.cpp`, and `src/buddy/startup_tasks.cpp` — reference safe outputs, watchdog, and fatal startup behavior.
- `utils/simulator/simulator.py`, `tests/integration/test_safety.py`, `tools/bazel/manifests/phase14_simulator_evidence_contract.json`, `tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json`, and `tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json` — simulator capabilities and simulator-versus-hardware claim boundaries.
- `.github/workflows/ci-evidence.yml` — current CI evidence production without an embedded Rust build/run.

### Current Official Ecosystem Sources

- [Rust bare-metal Armv7E-M targets](https://doc.rust-lang.org/nightly/rustc/platform-support/thumbv7em-none-eabi.html) — `thumbv7em-none-eabi`/`thumbv7em-none-eabihf`, Cortex-M4F, FPU and ABI details (HIGH).
- [Rust Reference: panic handlers](https://doc.rust-lang.org/stable/reference/panic.html) — a `no_std` binary requires one non-returning panic handler (HIGH).
- [Embedded Rust Book: `no_std`](https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html) — bare-metal firmware runtime and allocation constraints (HIGH).
- [Embedded Rust Book: QEMU bring-up](https://docs.rust-embedded.org/book/start/qemu.html) — `no_std`/`no_main`, target memory layout, cross-compilation, real ELF execution, and emulator/CPU selection (HIGH).
- [Embedded Rust Book: panicking](https://docs.rust-embedded.org/book/start/panicking.html) and [exceptions](https://docs.rust-embedded.org/book/start/exceptions.html) — explicit panic and HardFault/default-handler behavior (HIGH).
- [`cortex-m-rt` documentation](https://docs.rs/cortex-m-rt/latest/cortex_m_rt/) — vector table, reset/exception symbols, linker scripts, memory sections, ELF inspection, VTOR, and the pre-init safety limitation (HIGH).
- [STM32F407VG datasheet](https://www.st.com/resource/en/datasheet/stm32f407vg.pdf) — Cortex-M4 with single-precision FPU, memory/peripheral facts, and independent/window watchdog behavior (HIGH; DS8626 Rev 12, March 2026).
- [`rules_rust` setup](https://bazelbuild.github.io/rules_rust/) and [`rust_binary` rules](https://bazelbuild.github.io/rules_rust/rust.html) — current Bzlmod dependency/toolchain configuration and output-producing Rust rules (HIGH).
- [`rules_rust` custom toolchains](https://bazelbuild.github.io/rules_rust/rust_toolchains.html) — target triples, linker selection, and registered platform-compatible toolchains (HIGH).
- [Bazel hermeticity](https://bazel.build/concepts/hermeticity) and [remote caching](https://bazel.build/remote/caching) — declared inputs/outputs, pinned tools, sandboxing, and repeat-build hash comparison (HIGH).
- [Upstream Prusa-Firmware-Buddy](https://github.com/prusa3d/Prusa-Firmware-Buddy) — supported product/build context and C/C++ reference implementation (MEDIUM for fast-moving upstream state; local checkout remains authoritative for v1.4 planning).

***

*Feature research for: Bazel-native Rust MINI safe firmware bring-up*
*Researched: 2026-08-02*
