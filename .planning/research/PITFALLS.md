# Domain Pitfalls

**Domain:** Bazel-native Rust firmware bring-up for `MINI/BUDDY/STM32F407VG`
**Milestone:** v1.4 Bazel-Native Rust Firmware Bring-Up
**Researched:** 2026-08-02
**Overall confidence:** HIGH for repository, startup, linker, artifact, and workflow risks; MEDIUM for Mini404 GPIO/watchdog observability until exercised against the real image

## Phase Vocabulary

The phase assignments below use the implementation sequence recommended by the current architecture research:

1. **Truthful Bazel labels and executable toolchain**
2. **Pure `no_std` safe-boot core**
3. **Retained reset/link boundary**
4. **MINI hazardous-output adapter**
5. **Rust runtime, faults, and validated link**
6. **Real artifact derivation and provenance**
7. **MINI simulator and fail-closed evidence**
8. **Reference comparison, CI qualification, and rollback freeze**

## Critical Pitfalls

### Pitfall 1: Target, CPU, and Floating-Point ABI Drift

**What goes wrong:** Rust or retained native objects are built for the wrong architecture or ABI. A host build, soft-float object, generic Thumb target, or mismatched Arm linker can still compile far enough to create an ELF, yet fail at link time, fault at runtime, or corrupt calls across the Rust/ASM/native boundary.

**Why it happens:** Bazel separates execution and target platforms; `rules_rust` and `rules_cc` resolve toolchains independently unless the target contract is explicit. The required Rust target is `thumbv7em-none-eabihf`, while the retained Arm GNU path uses Cortex-M4, hard-float, and FPv4-SP-D16 flags. Startup assembly may advertise `softvfp` despite containing no floating-point call boundary, which is safe only if that assumption is verified rather than generalized.

**Consequences:** The image may not boot, may fault only when floating-point code is reached, or may pass host tests while being unusable on STM32F407VG. Diagnosis becomes especially expensive if host-dependent linkers or newer opportunistic toolchains produce different symptoms.

**Prevention:**

- Pin Bazel, Rust 1.85.0, `rules_rust`, `rules_cc`, and Arm GNU 13.2.Rel1 in declared repositories/toolchains.
- Require the explicit MINI target platform and `thumbv7em-none-eabihf`; never infer firmware target selection from the host.
- Preserve `-mthumb -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16` for all native objects participating in an ABI boundary.
- Use the Arm GCC driver for the first mixed-language final link.
- Gate the ELF on ARM machine type, EABI attributes, entry symbol, undefined-symbol inventory, and absence of hosted/unwinding/allocator dependencies.

**Warning signs:** Firmware targets build without an explicit platform; `cargo build` is invoked with no target; host tests and firmware share indistinguishable labels; `readelf -A` is absent from validation; link errors are addressed with broad flags; local developers silently use different `arm-none-eabi-*` versions.

**Phase assignment:** Phase 1 establishes the executable cross-toolchain; Phase 5 blocks the first linked image on ABI inspection. Keep the check mandatory for every later firmware artifact.

### Pitfall 2: Two Owners for Reset, Vectors, and RAM Initialization

**What goes wrong:** Retained startup assembly and Rust runtime machinery both define the reset handler, vector table, `.data` copy, `.bss` zeroing, stack, or default interrupts. Alternatively, neither side fully owns one of those responsibilities. The result can be duplicate symbols, the wrong entry point, stale RAM, invalid interrupt dispatch, or an image linked at the wrong flash origin.

**Why it happens:** `cortex-m-rt` is a familiar Rust default, but v1.4 deliberately retains the repository's STM32F407 startup veneer and linker scripts. The bootloader-compatible image starts at `0x08020200`, while the direct/no-boot layout starts at `0x08000000`; treating these as interchangeable build flags creates behaviorally different images under one product name.

**Consequences:** Safe Rust can begin execution with invalid memory assumptions, fault before output inhibition, or package a BIN/BBF whose load contract does not match its vector table. A separately linked simulator image can mask a broken bootloader-compatible image.

**Prevention:**

- Retain exactly one MINI-compatible startup assembly target and one explicit linker script per boot mode.
- Define a single handoff symbol, `extern "C" fn rust_entry() -> !`, and prohibit a competing C `main`, Rust reset runtime, constructor chain, or second vector table.
- Assert `.isr_vector` address/size, `Reset_Handler`, stack placement, `.data`, `.bss`, RAM, CCMRAM, and boot-exchange regions from the real ELF and linker map.
- Keep boot and no-boot configurations as separately named labels; default development BBF generation to the bootloader-compatible layout.
- Do not replace startup ownership until reset, vector, RAM-init, fault, simulator, and hardware evidence exists for the replacement.

**Warning signs:** `cortex-m-rt` appears while retained startup objects are still linked; two reset/vector symbols exist; a linker script is selected by an environment variable; the simulator and BBF use separately linked images; `.data`/`.bss` behavior is inferred from source rather than checked in the output.

**Phase assignment:** Phase 3 owns this boundary and its structural tests; Phase 5 proves the completed Rust handoff; Phase 8 freezes the reference comparison.

### Pitfall 3: Hazardous Outputs Are Inhibited Too Late or Only in the Happy Path

**What goes wrong:** Heater, motor-enable, or other hazardous pins briefly assert during reset-to-Rust handoff, clock setup, GPIO mode changes, panic, default interrupt, or watchdog recovery. Firmware may report a safe state while external pin state is unsafe.

**Why it happens:** GPIO safety depends on exact BUDDY pins, active polarities, register sequencing, and reset assumptions. A generic HAL initialization path can change modes before output latches are set. A UART or in-memory marker proves only what firmware believes, not what the pins did. Rust's type safety does not validate MMIO addresses, polarities, or ordering inside an unsafe adapter.

**Consequences:** A bring-up image intended to be non-operational can energize real hardware. This is the milestone's highest safety risk and invalidates simulator or artifact success regardless of other results.

**Prevention:**

- Encode the MINI safe pin table and polarities as reviewed data derived from `hwio_safe_state` and board definitions.
- Set output latches to safe values before switching pin modes; make `force_inhibit()` idempotent and callable from reset, panic, HardFault, default interrupt, and watchdog paths.
- Model `ResetUnknown -> OutputsInhibited -> SafeBootLatched` with an unforgeable capability; later boot steps must require the `OutputsInhibited` value.
- Keep the adapter as the sole audited MMIO/unsafe owner; expose no heater-on, motion, or operational capability in v1.4.
- Prefer external Mini404 GPIO traces over firmware self-report, then require hardware validation before any cutover claim.

**Warning signs:** Clock/HAL initialization precedes inhibition; pin polarity is duplicated in procedural code; output mode is changed before its latch; only the normal boot path calls the safety function; tests assert a status string rather than observed pins; a generic `HAL_Init()` is retained as an escape hatch.

**Phase assignment:** Phase 2 proves the pure transition model; Phase 4 implements and reviews MINI MMIO; Phase 5 converges all terminal paths; Phase 7 observes pins externally.

### Pitfall 4: Panic, HardFault, Default Interrupt, and Watchdog Paths Diverge

**What goes wrong:** Normal reset safely parks, but an unexpected interrupt, panic, HardFault, or watchdog event spins with outputs unchanged, recursively faults, corrupts crash evidence, or returns to an uninitialized state. The watchdog may be serviced accidentally or ignored until behavior differs from the reference contract.

**Why it happens:** `panic=abort` prevents unwinding but does not itself establish a safe terminal policy. Retained vectors, Rust handlers, linker symbols, watchdog registers, and any crash marker form one cross-language runtime contract. Simulator support for watchdog injection or observation may also be incomplete.

**Consequences:** Fault handling becomes less safe than normal boot, failures become nondeterministic, and a green reset smoke test creates false confidence about the actual runtime boundary.

**Prevention:**

- Define one terminal runtime policy: inhibit outputs, record only bounded safe evidence where possible, then enter a deliberate park or reset loop.
- Route panic, HardFault, default interrupt, invariant failure, and watchdog recovery through the same idempotent inhibition primitive.
- Use `panic=abort`, prohibit unwinding and allocation, and validate required handler symbols plus forbidden runtime symbols in the ELF.
- Unit-test pure fault transitions; add injected simulator scenarios where Mini404 supports them.
- Mark unsupported watchdog observations as `blocked` or `not_observed`, and preserve an explicit hardware-required gate.

**Warning signs:** `panic_handler` is a placeholder loop; default vectors alias an unreviewed symbol; faults bypass `force_inhibit()`; watchdog servicing has no explicit policy; absence of simulator support is converted to pass; a panic path allocates, formats unbounded text, or assumes initialized peripherals.

**Phase assignment:** Phase 2 defines fault-state semantics; Phase 5 owns real handlers and watchdog policy; Phase 7 exercises supported injections; Phase 8 retains hardware-required evidence gaps.

### Pitfall 5: The Retained Foreign Boundary Expands Until Rust Ownership Is Nominal

**What goes wrong:** The first successful link pulls in full STM32 HAL, CMSIS runtime helpers, FreeRTOS, C++ initialization, or broad native libraries. Rust becomes a leaf called after the existing runtime rather than the owner of executable behavior after reset.

**Why it happens:** Reusing a broad native target makes missing register setup or symbols disappear quickly. CMake-era global include/link surfaces make it easy to add an entire subsystem when only one constant, clock operation, or veneer is needed. Temporary FFI tends to become permanent without explicit manifests and exit criteria.

**Consequences:** Startup and fault ownership become ambiguous, constructors and interrupts re-enter the image, unsafe review surface grows, map/size evidence becomes noisy, and later replacement work cannot distinguish required compatibility from accidental linkage.

**Prevention:**

- Retain only the startup veneer, linker scripts, established BBF encoder, and declared Arm binutils by default.
- Give every retained ASM/C function its own Bazel target, symbol contract, rationale, owner, evidence, and retirement condition.
- If clock setup is unavoidable, retain one narrowly named function after output inhibition; do not link generic HAL or scheduler entrypoints.
- Enforce map/symbol allowlists and fail on C `main`, C++ constructors, FreeRTOS, Marlin, GUI, networking, or storage symbols in the safe-boot image.
- Keep policy in pure Rust and effects in the board/runtime adapters; do not expose broad native global state to domain code.

**Warning signs:** A glob imports a native directory; the link adds HAL/FreeRTOS “for later”; bindgen output becomes a general API; the retained-code manifest does not match actual symbols; C `main` remains the runtime owner; image size grows without explained map deltas.

**Phase assignment:** Phase 3 declares the retained boundary; Phase 5 enforces symbol and section allowlists; Phase 8 records the frozen boundary and rollback path.

### Pitfall 6: Bazel Is Only a Non-Hermetic Wrapper Around Cargo, PATH, or `.dependencies`

**What goes wrong:** Bazel labels invoke host Cargo, discover linkers on `PATH`, read undeclared `.dependencies`, or emit side-effect outputs. Builds work on one workstation but resolve different tools, targets, or files in CI. Bazel is authoritative in name only.

**Why it happens:** The repository already has bootstrap-managed binaries and descriptive Bazel scaffolding, making shell wrappers an easy short-term bridge. Cross-compilation involves Rust, Arm GCC, binutils, Python packaging, and Mini404, so one undeclared tool can undermine the whole graph.

**Consequences:** Outputs are not reproducible or remotely cacheable, action failures appear host-specific, provenance is incomplete, and CMake/Cargo fallback can satisfy milestones without Bazel owning the firmware.

**Prevention:**

- Pin tool archives and checksums through Bzlmod/repository rules and commit `MODULE.bazel.lock`.
- Register executable Rust and Arm toolchains; never resolve firmware tools from `PATH` or an undeclared local directory.
- Declare every source, linker script, tool, environment input, output, and execution requirement in the action graph.
- Invoke `pack_fw.py --no-sign` as a declared Python tool with declared inputs/outputs; missing dependencies must fail closed.
- Keep host tests and target firmware platforms separate, and make canonical Linux CI the reproducibility authority where local host packages are unsupported.

**Warning signs:** Actions run `cargo build`; scripts use `which arm-none-eabi-gcc`; local `.dependencies` paths appear in action commands; a Bazel build modifies the source tree; an action's output is found by globbing afterward; Apple and Linux silently use different Arm releases.

**Phase assignment:** Phase 1 closes toolchain and platform gaps; Phase 6 closes host-tool packaging gaps; Phase 8 proves clean CI reconstruction.

### Pitfall 7: Artifact Names Exist Without Single-Source Lineage

**What goes wrong:** ELF, map, BIN, BBF, hashes, or simulator evidence come from different builds, linker profiles, fixtures, or stale directories. A renamed text dump is accepted as a linker map, or a bootstrap-marker/fixture payload is packaged as if it were the real firmware.

**Why it happens:** Existing artifact helpers include fixture-oriented paths, while the real release shape spans linking, `objcopy`, Python BBF packaging, and evidence tooling. File existence is easier to test than derivation and content identity.

**Consequences:** Reviewers cannot prove what was simulated or packaged. A valid-looking development BBF may contain the wrong BIN; memory reports may describe another image; stale artifacts can produce false passes.

**Prevention:**

- Treat the validated unstripped ELF as the root artifact and derive the genuine linker map, BIN, and unsigned development BBF through declared actions.
- Record SHA-256, Bazel target, source revision, Bazel/Rust/Arm versions, target triple, linker-script digest, boot mode, signing mode, sizes, and validations in one manifest.
- Require the simulator and evidence records to consume and repeat the same artifact digest.
- Validate BBF headers and payload relationship using the established packer; forbid fixture/bootstrap fallback for v1.4 success.
- Mark the BBF `unsigned-local` in both metadata and naming; never let it enter a release-candidate path.

**Warning signs:** Outputs are copied from `build/` by filename; map generation is a post-link `objdump` renamed `.map`; the simulator accepts an arbitrary path outside the artifact bundle; digests are computed but not connected across stages; packaging succeeds after the real BIN action fails.

**Phase assignment:** Phase 5 establishes the root ELF/map; Phase 6 owns all derivation and provenance; Phase 7 binds scenarios to the digest; Phase 8 checks publication and retention.

### Pitfall 8: Simulator Success Is Reported as Hardware or Printer Success

**What goes wrong:** A Mini404 boot marker, lack of an observed fault, or firmware self-report is promoted to proof of GPIO safety, watchdog behavior, bootloader compatibility, or printer readiness. Existing MK4/full-UI integration fixtures may be reused for MINI safe boot despite validating a different machine and contract.

**Why it happens:** Simulator runs provide visible progress and are automatable, while hardware evidence is slower. Mini404's exact GPIO, watchdog, boot-offset, and fault-injection observability is not yet proven for the new image. “No observation” is easily mistaken for “safe.”

**Consequences:** Unsupported claims become green evidence, hazardous behavior can remain invisible, and the milestone drifts from build/simulator bring-up toward an unjustified replacement claim.

**Prevention:**

- Add a purpose-built `MachineType.MINI` safe-boot harness consuming the real artifact manifest.
- Separate claims for reset reachability, external GPIO state, fault convergence, watchdog/reset behavior, artifact load contract, and hardware qualification.
- Prefer simulator traces over firmware self-report; a status channel may supplement but not replace external observations.
- Emit `blocked` or `not_observed` for unsupported checks and keep hardware-required evidence explicit.
- Scope v1.4 acceptance to a genuine Bazel-built safe-boot artifact plus honest simulator evidence; printing, UI, network, and production cutover remain out of scope.

**Warning signs:** The harness selects MK4; a UART marker is the only safety assertion; simulator absence of an event counts as pass; no simulator version or artifact digest is recorded; roadmap language says “printer works” or “hardware safe” after simulator-only tests.

**Phase assignment:** Phase 7 owns claim-level simulator evidence; Phase 8 audits wording, unresolved observations, and the later hardware gate.

## Moderate Pitfalls

### Pitfall 9: Print-Only or Reference-Only Workflows Masquerade as Successful Builds

**What goes wrong:** `just build`, `//tools/bazel:build_firmware`, or a shell action prints the command that would run, prints a reference contract, or creates marker outputs, then exits zero without compiling and validating the Rust firmware.

**Why it happens:** The current Bazel boundary includes descriptive/reference targets useful in earlier phases. Keeping their labels while changing their claimed meaning lets dashboards and developer habits report progress without an executable toolchain.

**Consequences:** Developers trust commands that do not produce firmware; CI can pass on metadata; downstream artifact and simulator stages consume fixtures; the milestone's core value is not delivered.

**Prevention:**

- Preserve descriptive/reference labels with explicit names, but route user-facing build/test recipes to the real MINI targets.
- Require `just build` and the canonical Bazel label to create validated ELF/map/BIN/BBF outputs or fail nonzero.
- Add negative tests proving that missing toolchains, packager dependencies, real BINs, or simulator inputs cannot fall back to fixtures.
- Keep `justfile` recipes thin and observable: one stable Bazel invocation, propagated exit status, and documented output locations.

**Warning signs:** Successful output contains “would run,” “reference only,” or “bootstrap marker”; outputs are tiny fixed fixtures; `just build` invokes CMake/Cargo directly; labels produce only stdout; missing dependencies are warnings rather than failures.

**Phase assignment:** Phase 1 makes build labels truthful; Phase 6 removes artifact fallbacks; Phase 8 verifies the documented developer workflow from a clean environment.

### Pitfall 10: Stale Evidence and Archival Paths Re-Qualify the Wrong Image

**What goes wrong:** Evidence aggregation reads a previous run, a legacy phase directory, a CMake reference artifact, or an archived success record after the current Bazel build or simulator run failed. Cleanup or archive moves can sever the relationship between evidence and its artifacts while leaving pass summaries discoverable.

**Why it happens:** The repository already has phase-specific evidence tooling and historical bootstrap/reference artifacts. File-based pipelines often search conventional directories or “latest” paths, which is convenient but unsafe when multiple build authorities and archived runs coexist.

**Consequences:** CI or roadmap reviews can qualify stale data, failures disappear behind a prior pass, and later investigators cannot reproduce which source revision, toolchain, artifact, simulator, or scenario created the result.

**Prevention:**

- Give each run an immutable ID tied to source revision, Bazel invocation, target label, and root ELF digest; pass those paths explicitly rather than searching for “latest.”
- Keep current results, reference results, fixtures, and archives in distinct schemas/roots with evidence-class metadata.
- Start every canonical run in a new declared output tree; fail if expected current-run records are missing, duplicated, or digest-mismatched.
- Make the aggregate publish a fail-closed current-run result even when build, validation, packaging, or simulation stops early.
- Archive artifacts and evidence together with manifests; archived records are historical and must never satisfy the current gate.

**Warning signs:** Tools glob for the newest JSON; a failed run leaves the prior pass untouched; reference and Rust files share names; archives contain summaries without artifacts/manifests; evidence lacks source revision, tool versions, simulator version, or artifact SHA-256.

**Phase assignment:** Phase 6 defines immutable artifact/run identity; Phase 7 emits complete current-run scenario rows; Phase 8 owns aggregation, CI upload, retention, archive separation, and stale-evidence regression tests.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Required Mitigation / Exit Evidence |
| --- | --- | --- |
| 1. Truthful labels and toolchain | Host/soft-float target or print-only Bazel facade | Explicit MINI platform; pinned executable Rust/Arm toolchains; a link smoke target that produces a real ARM object/image; no Cargo/PATH fallback |
| 2. Pure safe-boot core | Happy-path-only safety model | Exhaustive host tests for reset, inhibition, latch, fault, and watchdog-policy transitions; fixed-size `no_std` code |
| 3. Retained reset/link boundary | Double reset/vector ownership or retained-code creep | One startup veneer, one linker profile per label, one `rust_entry`, explicit retained manifest, section-address checks |
| 4. Hazardous-output adapter | Wrong polarity or unsafe GPIO sequencing | Reviewed MINI pin table, latch-before-mode writes, idempotent `force_inhibit`, narrow audited unsafe module |
| 5. Runtime and validated link | Panic/fault paths bypass safety; ABI mismatch | Real ELF/map; ARM/hard-float, vector, memory, symbol, forbidden-runtime, and size checks; every terminal path inhibits outputs |
| 6. Artifacts and provenance | Fixture BBF, fake map, split lineage, stale run directory | ELF-rooted declared derivation; real map/BIN/unsigned BBF; immutable manifest and digest; no fallback |
| 7. Simulator evidence | MK4 fixture reuse or unsupported checks reported as pass | MINI-specific harness; external pin observations where supported; artifact-bound rows; `blocked`/`not_observed` semantics |
| 8. CI/reference/rollback | Stale or archived evidence re-qualifies; simulator claim overreach | Clean canonical Linux reconstruction, fail-closed aggregate, archive separation, honest hardware gap, separately selectable CMake reference |

## Cross-Pitfall Acceptance Gates

The milestone is not complete unless all of the following are simultaneously true:

1. Bazel resolves the pinned MINI Rust/Arm toolchains without Cargo, `PATH`, CMake product-build, or undeclared `.dependencies` fallback.
2. One retained reset/vector/RAM-init veneer hands control directly to Rust, and the real ELF proves its layout and ABI.
3. The safe-boot image externally demonstrates supported hazardous-output observations; all unsupported simulator claims remain explicitly blocked.
4. Panic, default interrupt, HardFault, and watchdog policy converge on the same idempotent output-inhibition boundary.
5. ELF, linker map, BIN, unsigned-development BBF, manifest, simulator rows, and CI uploads share one verifiable artifact lineage.
6. `just build`, `just test`, and canonical Bazel targets either produce their promised real outputs/evidence or fail visibly.
7. Current-run evidence cannot be satisfied by fixtures, CMake reference artifacts, prior runs, or archived records.

## Sources

### Repository evidence — HIGH confidence

- `.planning/research/STACK.md` — pinned toolchain recommendation, hard-float ABI, hermeticity requirements, real artifact graph, and host constraints.
- `.planning/research/FEATURES.md` — v1.4 table stakes, anti-features, fail-closed evidence requirements, and milestone scope.
- `.planning/research/ARCHITECTURE.md` — reset/runtime ownership, hazardous-output state machine, retained boundary, artifact lineage, simulator flow, and implementation order.
- `cmake/GccArmNoneEabi.cmake`, `cmake/AnyGccArmNoneEabi.cmake`, and `utils/bootstrap.py` — reference Cortex-M4F hard-float flags, Arm GNU version, and Mini404 provisioning.
- `src/device/stm32f4/startup/stm32f407xx.s`, `src/device/stm32f4/startup/stm32f407xx_boot.s`, `src/device/stm32f4/linker/stm32f407vg.ld`, and `src/device/stm32f4/linker/stm32f407vg_boot.ld` — reset, vectors, memory initialization, and the two flash layouts.
- `src/hwio_safe_state/hwio_safe_state.cpp` and MINI/BUDDY board pin definitions — current hazardous-output policy and polarity reference.
- `tools/bazel/toolchains/reference_toolchain.bzl`, `tools/bazel/shell_rules.bzl`, and `tools/bazel/reference_contract.sh` — current descriptive/reference and print-only boundaries that cannot satisfy v1.4.
- `tools/bazel/artifact_rules.bzl`, `tools/bazel/artifact_packager.py`, and `utils/pack_fw.py` — current artifact helper, fixture/fallback risk, and established unsigned BBF path.
- `tests/integration/conftest.py`, `utils/simulator/simulator.py`, and phase evidence tooling under `tools/bazel/` — current simulator assumptions, evidence schemas, and stale/reference evidence surfaces.

### Confidence notes

- **HIGH:** ABI, startup/linker ownership, current print-only/reference behavior, packaging lineage requirements, and the safe-state source boundary are directly evidenced by repository files and the current stack/architecture research.
- **MEDIUM:** Exact Mini404 GPIO, watchdog, boot-offset, and fault-injection observability remains an implementation-time question. The safe conclusion is to fail closed and preserve hardware-required claims, not to assume support or impossibility.

## Research Flags for Roadmap Planning

- **Phase 3:** Confirm the exact assembly file selected for MINI boot and no-boot labels and prove the handoff symbol/section contract from a real link.
- **Phase 4:** Review reset-state GPIO assumptions and whether any clock operation is required before safe inhibition on STM32F407/BUDDY hardware.
- **Phase 6:** Verify the unsigned BBF header/load-offset relationship against the existing packer and a reference artifact.
- **Phase 7:** Determine Mini404 support for canonical boot-layout loading, external GPIO traces, fault injection, and watchdog observation before final scenario acceptance is written.
- **Phase 8:** Define current/reference/archive evidence roots and retention rules so historical success can never satisfy a current qualification gate.
