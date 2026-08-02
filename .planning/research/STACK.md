# Stack Research

**Domain:** Bazel-native Rust bring-up for the Prusa MINI Buddy board (STM32F407VG)
**Milestone:** v1.4 Bazel-Native Rust Firmware Bring-Up
**Researched:** 2026-08-02
**Confidence:** HIGH for the target ABI, repository integration points, and published Bazel rules; MEDIUM for the final-link rule shape until a real ELF proves the mixed Rust/ASM link

## Recommendation in One Sentence

Pin Bazel 9.2.0, `rules_rust` 0.71.3, Rust 1.85.0, `rules_cc` 0.2.22, and the repository's existing Arm GNU 13.2.Rel1 toolchain; build one `thumbv7em-none-eabihf` MINI image from a `no_std` Rust crate plus the retained STM32F407 startup assembly and boot linker script, then derive genuine ELF/map/BIN/unsigned-development-BBF artifacts and run them through the existing Mini404 0.9.10 pytest evidence path.

This is intentionally a bring-up stack, not the final Rust HAL/runtime stack. It changes build ownership and introduces a real Rust firmware entry point without simultaneously replacing startup, the linker layout, FreeRTOS, the STM32 HAL, packaging, or the simulator.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Bazel | 9.2.0, pinned in `.bazelversion` | Authoritative build, link, artifact, and test graph | This is the installed repository-era Bazel and an official 9.x LTS release. Pinning removes the current host-dependent Bazel version. |
| Bzlmod | Bazel 9.2.0 native | Resolve Bazel rules and host toolchains | `MODULE.bazel` already exists. Use its lockfile as the external-dependency record; do not add WORKSPACE-era parallel resolution. |
| `rules_rust` | 0.71.3 | Register Rust 1.85.0 and compile the embedded crate | This is the latest published BCR release at research time and is tested with Bazel 7/8/9. Its toolchain extension accepts exact Rust versions and extra target triples. |
| Rust | 1.85.0 stable, edition 2024 | Compile firmware and existing workspace crates | `Cargo.toml` already declares `rust-version = "1.85"` and edition 2024. Matching that floor avoids an unrelated compiler upgrade during first firmware bring-up. No nightly or `build-std` is required. |
| Rust target | `thumbv7em-none-eabihf` | STM32F407VG machine code | The STM32F407 is Cortex-M4F and the current CMake flags use FPv4-SP-D16 with the hard-float ABI. Rust documents this exact target for Cortex-M4F/M7F with hardware floating point. |
| `rules_cc` | 0.2.22 | Compile retained startup ASM and provide the Arm linker toolchain | It is the current BCR release and is tested on Bazel 9. A direct dependency is appropriate because this milestone loads its C/C++ toolchain APIs rather than relying on a transitive version. |
| Arm GNU Toolchain | 13.2.Rel1 (`13.2.1` in `utils/bootstrap.py`) | Assemble startup, perform the final link, emit map/BIN, inspect ELF | Reuse the exact reference toolchain and flags for the first link. An opportunistic upgrade would add code-generation and ABI drift while the build boundary is already changing. |
| `rules_python` | 2.2.0 | Run `utils/pack_fw.py` and existing pytest integration tooling under Bazel | Current BCR release tested on Bazel 9. Python remains an implementation dependency of the reference BBF and simulator paths, but Bazel owns invocation and outputs. |
| Mini404 | 0.9.10, repository pin | MINI simulator evidence | This is the emulator already bootstrapped and understood by the integration/evidence scripts. Replacing the simulator would make bring-up failures harder to attribute. |
| `just` | Repository-required facade | Stable developer commands | Keep recipes thin: `just build`, `just test`, and the bring-up evidence recipe must call real Bazel labels and propagate failures. |

### Firmware Inputs and Supporting Code

| Input | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| Rust `core` | Rust 1.85.0 target component | Allocation-free language/runtime primitives | Use everywhere in the embedded image. Do not introduce `std` or `alloc` in this milestone. |
| `buddy-domain`, `buddy-application` | Workspace 0.1.0 | Existing safe domain/application seams | Link only behavior needed by the safe-boot slice; preserve host `rust_test` coverage. |
| `buddy-board-adapter` | Workspace 0.1.0 | Sole audited unsafe/MMIO boundary | Put volatile GPIO/watchdog access or narrow retained-C FFI here. Keep domain, application, and runtime crates `unsafe_code = "forbid"`. |
| `buddy-runtime-adapter` | Workspace 0.1.0 | Startup, linker, panic, and watchdog contracts | Use its existing typed surfaces to describe the safe parked state; do not boot the full scheduler merely to prove the image. |
| `src/device/stm32f4/startup/` | Retained repository code | Reset vector, vector table, RAM initialization | Compile exactly one MINI-compatible startup assembly source. The retained-code manifest already defers replacement until simulator and hardware evidence exist. |
| `stm32f407vg_boot.ld` | Retained repository code | Bootloader-aware memory layout | Make this the development BBF default: FLASH starts at `0x08020200` with 895 KiB, RAM is 128 KiB, and CCMRAM is 64 KiB. |
| `stm32f407vg.ld` | Retained repository code | Direct/no-boot simulator variant | Expose only as a separate explicit Bazel label/config when Mini404 requires a raw image at `0x08000000`; never select it implicitly. |
| `utils/pack_fw.py --no-sign` | Existing reference implementation | Produce development BBF | Reuse the real BBF encoder with Bazel-declared metadata and outputs. A missing Python dependency must fail as bootstrap-required, never fall back to a fixture package. |

No third-party Rust crates are needed for this milestone. In particular, direct volatile access can remain in the existing narrow board-adapter unsafe boundary; adding a HAL/runtime crate now would expand the proof surface without helping establish a truthful cross-compiled image.

### Required Toolchain Configuration

```starlark
module(name = "prusa_firmware_buddy")

bazel_dep(name = "rules_rust", version = "0.71.3")
bazel_dep(name = "rules_cc", version = "0.2.22")
bazel_dep(name = "rules_python", version = "2.2.0")

rust = use_extension("@rules_rust//rust:extensions.bzl", "rust")
rust.toolchain(
    edition = "2024",
    extra_target_triples = ["thumbv7em-none-eabihf"],
    versions = ["1.85.0"],
)
use_repo(rust, "rust_toolchains")
register_toolchains("@rust_toolchains//:all")
```

The Arm toolchain must be a checksum-pinned Bazel repository/toolchain, not a lookup on `PATH` and not an undeclared read from `.dependencies`. Preserve these target flags from the reference build:

```text
-mthumb -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16
-ffunction-sections -fdata-sections
-Wl,--gc-sections -Wl,--print-memory-usage
```

Use `panic=abort`, no unwinding, no default allocator, and no hosted startup. The final link must use the Arm GCC driver so retained ASM/native objects, Rust hard-float objects, the linker script, and libgcc conventions share one explicit ABI boundary.

## Bazel Target and Artifact Pattern

Use a small purpose-built Starlark firmware image rule rather than stretching the existing fixture-oriented Phase 3 macro:

```text
rules_rust firmware crate/archive
            + retained startup cc/asm target
            + stm32f407vg_boot.ld
            + Arm GNU linker toolchain
                         |
                         v
                 declared ELF + linker MAP
                         |
           arm-none-eabi-objcopy -O binary
                         |
                         v
                        BIN
                         |
            utils/pack_fw.py --no-sign
                         |
                         v
             development-only unsigned BBF
```

The final-link action must declare both `.elf` and `.map`; a post-link text dump named `.map` is not equivalent. The ELF should remain unstripped for inspection. Generate `.bin` with the same Arm GNU `objcopy`, and validate all outputs with `readelf`, `nm`, and `size` from that pinned toolchain. A provenance manifest should record SHA-256, Bazel/Rust/Arm tool versions, target triple, linker script, boot mode, and signing mode.

Required structural checks before simulator execution:

- ELF machine is ARM, entry is `Reset_Handler`, and hard-float attributes match the toolchain contract.
- `.isr_vector` begins at the selected FLASH origin; `.data`, `.bss`, stack, RAM, and CCMRAM stay within the linker-script regions.
- No undefined hosted/syscall, allocator, unwinding, or semihosting symbols are present.
- The BIN is derived from the ELF, the BBF contains that BIN, and the BBF is marked unsigned/development-only.
- Map and size budgets are real linker evidence, not fixture or bootstrap-marker output.

## Integration Points

| Existing Surface | Required Change | Contract to Preserve |
|------------------|-----------------|----------------------|
| `MODULE.bazel`, `.bazelrc`, `platforms/BUILD.bazel` | Replace descriptive toolchain registrations with real Rust/Arm toolchains for `//platforms:mini_buddy_stm32f407vg` | Existing platform/config label remains the selection point. |
| `tools/bazel/toolchains/reference_toolchain.bzl` | Keep reference-only labels separate; add real toolchain definitions rather than relabeling fake targets as executable | Truthful evidence classification. |
| `justfile` and `//tools/bazel:build_firmware` | Route to the real MINI image label; remove the shell script that only prints reference behavior | `just build` either produces real artifacts or fails. |
| `tools/bazel/artifact_rules.bzl` / packager helpers | Add a real-image path that accepts the Bazel ELF/BIN; disable fixture/bootstrap fallback for v1.4 success | Existing BBF format and unsigned-local policy. |
| `utils/pack_fw.py` | Invoke via a declared Python target with `--no-sign` and MINI metadata derived from the Bazel product profile | BBF format remains reference-compatible; no private key enters the graph. |
| `tests/integration/conftest.py` and Phase 14/23 evidence tooling | Pass the real BIN and adjacent real BBF plus the pinned `qemu-system-buddy` | Existing launch/readiness/timeout and evidence schemas. |
| `.github/workflows/ci-evidence.yml` | Build, inspect, and simulate the exact real target on canonical Linux; upload ELF/MAP/BIN/BBF and evidence manifests | Simulator claims remain CI-verifiable and artifact-backed. |

The safe-boot firmware should do the minimum observable work: enter through the retained reset vector, establish hazardous-output inhibit through the board adapter, expose a deterministic marker/state for the simulator, service or deliberately test watchdog behavior, and park. Full HAL, FreeRTOS, Marlin, UI, networking, and storage integration belongs after this first image is reproducible.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Retain startup ASM and linker script | `cortex-m-rt` owns reset/vector/link layout | After the retained-code boundary is deliberately retired and simulator plus hardware evidence covers reset, interrupts, bootloader offset, RAM initialization, and fault behavior. |
| Arm GNU 13.2.Rel1 final linker/tools | `rust-lld` plus LLVM tools | After ELF sections, map semantics, native ABI, BBF input, and simulator/hardware behavior have a passing baseline. |
| Existing Mini404 0.9.10 | Renode, stock QEMU, or a new simulator | Only if Mini404 cannot model the required MINI boot/watchdog observation and the replacement has an explicit evidence mapping. |
| Existing Python BBF encoder | New Rust BBF encoder | After byte/structural compatibility tests exist and packaging replacement is itself a scoped milestone. |
| Rust 1.85.0 | Current stable Rust | Upgrade separately once the real image is reproducible; do not mix compiler migration with first-link diagnosis. |

## What NOT to Add in v1.4

| Avoid | Why | Use Instead |
|------|-----|-------------|
| `cortex-m-rt` or a Rust vector table | Creates two startup authorities and bypasses the retained-code decision | Existing STM32F407 startup ASM. |
| `stm32f4xx-hal`, Embassy, or RTIC | Replaces peripheral and scheduling behavior before the build/boot proof exists | Existing board/runtime adapter seam and narrowly retained code. |
| `cortex-m`, `critical-section`, `heapless`, `defmt`, `panic-probe`, `probe-rs` | Useful later, but none is necessary to link, safely park, package, or simulate the first image | `core`, a tiny panic handler, existing logging/evidence surfaces, and Arm GNU inspection tools. |
| `crate_universe` | There are no external Rust crates to resolve in this slice | First-party `rust_library`/firmware targets only. |
| `rules_pkg` | BBF is a firmware-specific format already encoded by the reference script | Bazel action around `utils/pack_fw.py --no-sign`. |
| CMake/Cargo product-build fallback | Would let the milestone pass without Bazel owning the real image | Bazel must own compile, link, artifacts, simulator inputs, and CI evidence. |
| Synthetic payloads, bootstrap-marker BBFs, or fake map files | Repeat the current descriptive facade and produce false progress | Fail closed unless all real outputs are produced and validated. |
| Release signing keys | The milestone requests a development BBF, not a release artifact | Explicit unsigned-local metadata and `--no-sign`. |

## Version Compatibility and Risks

| Area | Decision / Risk | Mitigation |
|------|-----------------|------------|
| Bazel / rules | Bazel 9.2.0 + `rules_rust` 0.71.3 + `rules_cc` 0.2.22 + `rules_python` 2.2.0 | Pin versions and commit `MODULE.bazel.lock`; all three rule releases declare Bazel 9 support. |
| Rust edition | Edition 2024 requires Rust 1.85+ | Pin exactly 1.85.0 in the rules_rust extension and keep `Cargo.toml` aligned. |
| FPU ABI | `eabihf` Rust objects must not mix with soft-float native objects | Preserve `-mfloat-abi=hard -mfpu=fpv4-sp-d16`; inspect ELF attributes and fail on mismatch. The startup file's `.fpu softvfp` directive is acceptable only because it contains no floating-point ABI boundary; verify this in the real link. |
| Memory layout | Boot and no-boot linker scripts have different FLASH origins and sizes | Separate Bazel labels/configs; default the development BBF to the boot script and assert section addresses. |
| Rust sections/symbols | Orphan unwind, vector, panic, or allocator sections can silently bloat or break startup | `panic=abort`, no allocator, link-map allowlist/budget checks, and undefined-symbol checks. |
| Genuine map output | `rust_binary` alone does not provide a declared paired GNU linker map | Make the final firmware link a dedicated Starlark action with ELF and map outputs; do not accept a side effect or renamed `objdump`. |
| Arm toolchain hosts | Repository-pinned 13.2.Rel1 has Linux x86_64/aarch64 and Windows archives, but the current Darwin URL is x86_64-only and ends in the suspicious `.tar.xzg` suffix | Make Linux CI canonical. Fail with an actionable unsupported-host message on Apple silicon unless a verified Rosetta/x86_64 archive path is supplied. Do not silently use Arm GNU 15.x on one host. |
| Mini404 host runtime | Prior local evidence found a missing `libfdt` dynamic library on macOS | Run canonical simulator evidence on pinned Linux; add a bootstrap preflight that reports missing host libraries before tests. |
| Simulator fidelity | Mini404 evidence is not hardware proof | Treat v1.4 as build/simulator bring-up. Preserve explicit hardware-required evidence for later cutover phases. |
| Unsigned BBF confusion | A valid development BBF can be mistaken for releasable firmware | Include `signing_mode=unsigned-local`, a development artifact name, and a CI policy that forbids release-candidate classification. |

## Verification Commands the Stack Must Enable

```bash
bazel build --config=mini //rust/firmware/mini:development_artifacts
bazel test //rust/...
bazel test --config=mini //tests/integration:mini_safe_boot_simulator
just build
just test
```

The exact labels may change during planning, but the semantics may not: the first command must create the real ELF/MAP/BIN/BBF output group, and the simulator test must consume those outputs rather than prebuilt CMake firmware or fixtures.

## Sources

### Authoritative external sources

- [Bazel 9.2.0 release](https://github.com/bazelbuild/bazel/releases/tag/9.2.0) — verified 9.2.0 is a 9.x LTS minor release (HIGH).
- [Bazel Central Registry: rules_rust](https://registry.bazel.build/modules/rules_rust) — verified published version 0.71.3 and Bazel 7/8/9 test matrix (HIGH).
- [rules_rust Bzlmod toolchain docs](https://bazelbuild.github.io/rules_rust/rust_bzlmod.html) — verified exact Rust version, edition, and `extra_target_triples` configuration (HIGH).
- [rules_rust rule reference](https://bazelbuild.github.io/rules_rust/rust.html) and [toolchain reference](https://bazelbuild.github.io/rules_rust/rust_toolchains.html) — verified native link dependencies, linker scripts, linker selection, and objcopy/toolchain surfaces (HIGH).
- [Bazel Central Registry: rules_cc](https://registry.bazel.build/modules/rules_cc) — verified 0.2.22 and Bazel 9 support (HIGH).
- [Bazel Central Registry: rules_python](https://registry.bazel.build/modules/rules_python) — verified 2.2.0 and Bazel 9 support (HIGH).
- [Rust `thumbv7em-none-eabi*` target documentation](https://doc.rust-lang.org/beta/rustc/platform-support/thumbv7em-none-eabi.html) and [Embedded Rust installation guide](https://doc.rust-lang.org/stable/embedded-book/intro/install.html) — verified Cortex-M4F hard-float target selection (HIGH).
- [Arm GNU Toolchain downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) — verified 13.2.Rel1 remains an official release branch and that current Apple-silicon host packages are a later toolchain capability (HIGH).

### Repository evidence

- `Cargo.toml`; `rust/crates/*/Cargo.toml` — Rust 1.85/edition 2024, first-party crate graph, and unsafe-code policy (HIGH).
- `cmake/GccArmNoneEabi.cmake`; `cmake/AnyGccArmNoneEabi.cmake`; `utils/bootstrap.py` — Cortex-M4F hard-float flags, Arm GNU 13.2.1, Mini404 0.9.10, and host archive constraints (HIGH).
- `src/device/stm32f4/startup/`; `src/device/stm32f4/linker/stm32f407vg_boot.ld`; `src/device/stm32f4/linker/stm32f407vg.ld` — reset/vector ownership and exact memory layouts (HIGH).
- `utils/pack_fw.py`; `tools/bazel/artifact_rules.bzl`; `tools/bazel/artifact_packager.py` — BBF reference path and current fixture/bootstrap fallback that v1.4 must not treat as success (HIGH).
- `tests/integration/README.md`; `tests/integration/conftest.py`; `tools/bazel/phase14_*`; `tools/bazel/phase23_*` — Mini404 invocation and simulator evidence contracts (HIGH).
- `.planning/PROJECT.md`; `.planning/codebase/{STACK,ARCHITECTURE,INTEGRATIONS,CONCERNS}.md`; retained-code/unsafe-audit manifests under `tools/bazel/manifests/` — milestone scope and staged startup/HAL/runtime boundary (HIGH).

***

*Stack research for: v1.4 Bazel-Native Rust Firmware Bring-Up*
*Researched: 2026-08-02*
