# Stack Research

**Domain:** Rust rewrite of STM32/FreeRTOS/Marlin-style 3D printer firmware with Bazel as the authoritative build system
**Researched:** 2026-06-02
**Confidence:** HIGH for current tool versions and official target support; MEDIUM for migration sequencing choices because they combine official facts with repository-specific architecture evidence

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Bazel | 9.1.0 | Authoritative build, test, packaging, generation, and toolchain graph | Current Bazel release is a 9.x LTS release. Big Bang plus behavior parity needs one graph for Rust, retained C/ASM, generated resources, simulator tests, and firmware artifacts. |
| Bzlmod / `MODULE.bazel` | Bazel 9 native | External dependency model | Use Bzlmod from the start. It is the current documented external dependency flow and matches rules_rust and Bazel Central Registry installation snippets. |
| rules_rust | 0.70.0 | Bazel Rust rules, Rust toolchains, `rust_binary`, `rust_library`, `rust_test`, crate integration | Current rules_rust release in the Bazel Central Registry. Release notes include Bazel 9 compatibility work and embedded-relevant improvements such as `thumbv7em-none-eabihf` target support and `rust_objcopy` integration. |
| Rust | 1.96.0 stable | Firmware and host Rust compiler | Current stable Rust channel as of 2026-06-02. Use edition 2024 for new crates and explicitly register this version through rules_rust instead of inheriting a developer-local toolchain. |
| Rust `no_std` | Rust 1.96.0 | Firmware crate environment | Bare-metal firmware should default to `#![no_std]`; `std` stays limited to host tools, tests, simulator helpers, and build-time generators. |
| Rust target triples | Rust 1.96.0 official target list | Cortex-M cross compilation | Use `thumbv7em-none-eabihf` for STM32F4/M4F boards, `thumbv6m-none-eabi` for STM32G0/M0+ boards, and `thumbv8m.main-none-eabi` or `thumbv8m.main-none-eabihf` for STM32H5/M33 boards depending on the exact FPU/ABI requirement. |
| rules_cc | 0.2.19 | Retained C/ASM build support and ARM C toolchain integration | Current Bazel Central Registry version. The rewrite still needs C/ASM for STM32 startup/linker pieces and retained HAL/CMSIS/FreeRTOS/LwIP/mbedTLS/FatFs/littlefs/TinyUSB code during parity migration. |
| ARM GNU / ST C toolchain | Pin from repo bootstrap, currently GCC Arm None Eabi 13.2.1 in codebase map | C/ASM compilation and linking support for retained firmware code | Do not let CMake own this. Register the ARM toolchain in Bazel and make retained C a first-class Bazel input. Existing bootstrap artifacts can seed the pin, but Bazel should be the source of truth. |
| FreeRTOS | Retain current project version initially | Runtime scheduler and task primitives | Behavior parity is the chosen migration strategy. Replacing the scheduler while rewriting language/build system would multiply risk across GUI, networking, transfers, Marlin-style loops, and motion/thermal timing. Wrap it in Rust adapters first. |
| STM32 HAL/CMSIS C stack | Retain current project/vendor versions initially | MCU startup, registers, clocks, interrupts, peripheral access | Keep exact board behavior during the Big Bang rewrite. Introduce Rust traits and typed adapters at boundaries before replacing vendor C peripheral code. |
| just | 1.51.0 | Developer command entrypoint | Use `just` as a small wrapper around Bazel commands and repo bootstrap checks. Keep build truth in Bazel/Starlark, not in shell recipe bodies. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `cortex-m` | 0.7.7 | Low-level Cortex-M intrinsics, interrupt masking, assembly helpers | Use in board/runtime crates where Rust code needs CPU-level operations. Keep direct use out of pure domain crates. |
| `cortex-m-rt` | 0.7.5 | Minimal Cortex-M startup/runtime support | Use only for board personalities where Rust owns reset/startup. If retained vendor startup remains authoritative, keep this optional and avoid two competing startup paths. |
| `embedded-hal` | 1.0.0 | Hardware abstraction traits | Use for Rust-facing driver and adapter boundaries. New Rust code should target 1.0.0 traits, not legacy `embedded-hal` 0.2 APIs. |
| `embedded-io` | 0.7.1 | Byte-stream traits for embedded environments | Use for serial, socket-like, transfer, file, and test-double boundaries where byte I/O abstractions help decouple retained C libraries from pure Rust logic. |
| `embedded-storage` | 0.3.1 | Storage abstraction traits | Use at flash/storage adapter edges where it clarifies EEPROM, flash, and persistent-store responsibilities. Keep product-specific persistence invariants in domain types. |
| `critical-section` | 1.2.0 | Cross-platform critical-section abstraction | Use for shared embedded crates that need critical sections without hard-coding a FreeRTOS or Cortex-M implementation. |
| `heapless` | 0.9.3 | Fixed-capacity collections and strings | Use for firmware queues, buffers, parser state, command metadata, and UI/Connect message structures that must not allocate dynamically. |
| `static_cell` | 2.1.1 | Static allocation with runtime initialization | Use for singleton peripherals, task resources, and long-lived firmware state when ownership must be explicit without heap allocation. |
| `defmt` | 1.1.0 | Compact embedded logging | Use in debug/probe firmware profiles and low-level bring-up. Do not replace production logging/syslog behavior until parity requirements approve it. |
| `defmt-rtt` | 1.2.0 | RTT transport for defmt logs | Use with debug probe configurations, not as the only product logging path. |
| `panic-probe` | 1.0.0 | Probe-friendly panic handler | Use for probe/debug builds. Production panic policy should be mapped to existing watchdog/reboot/error-reporting behavior. |
| `rtt-target` | 0.6.2 | RTT target-side I/O | Use for optional bring-up diagnostics when raw RTT channels are needed outside defmt. |
| `probe-rs` | 0.31.0 | Host flashing/debugging/probe tooling | Use as the preferred host-side probe tool for Rust debug flows. Keep firmware flashing/package validation Bazel-owned. |
| rules_python | 2.0.2 | Python tools and simulator/parity test wrapping | Use to bring existing Python generators, simulator tests, and pytest-style parity checks under Bazel. |
| rules_pkg | 1.2.0 | Build firmware delivery artifacts | Use for Bazel-owned packaging steps where it fits; keep `.bin`, `.bbf`, `.dfu`, map-file, and metadata production in the Bazel graph even when custom rules are needed. |

### Development Tools

| Tool | Version | Purpose | Why |
|------|---------|---------|-----|
| `rustfmt` | Rust 1.96.0 component | Formatting | Required by Bright Builds Rust verification. Run through Bazel/just, not ad hoc editor state. |
| Clippy | Rust 1.96.0 component | Rust linting | Required for Rust code quality. Gate warning-free pure/core crates early. |
| `rust-src` | Rust 1.96.0 component | Core/std source for cross targets and tooling | Needed by many `no_std` cross-compilation and analysis flows. Register it hermetically through the toolchain. |
| `llvm-tools-preview` | Rust 1.96.0 component | Rust-side objcopy/size/nm workflows | Prefer rules_rust-integrated tools where possible; use GNU ARM tools only where required by existing firmware artifact parity. |
| `bazelisk` or pinned Bazel binary | Bazel 9.1.0 | Local Bazel version enforcement | Store `.bazelversion` with `9.1.0`. Developers can use Bazelisk, but the repo pin is authoritative. |
| `just` | 1.51.0 | Human command facade | Standardize `just build`, `just test`, `just fmt`, `just clippy`, `just package`, and `just parity` as small wrappers. |

## Installation

Recommended initial Bazel module shape:

```starlark
module(name = "prusa_firmware_buddy_rust")

bazel_dep(name = "rules_rust", version = "0.70.0")
bazel_dep(name = "rules_rust_bindgen", version = "0.70.0")
bazel_dep(name = "rules_cc", version = "0.2.19")
bazel_dep(name = "rules_python", version = "2.0.2")
bazel_dep(name = "rules_pkg", version = "1.2.0")

rust = use_extension("@rules_rust//rust:extensions.bzl", "rust")
rust.toolchain(
    edition = "2024",
    versions = ["1.96.0"],
)
use_repo(rust, "rust_toolchains")
```

Recommended Rust dependency set for the first firmware graph:

```toml
[dependencies]
cortex-m = "0.7.7"
cortex-m-rt = { version = "0.7.5", optional = true }
critical-section = "1.2.0"
embedded-hal = "1.0.0"
embedded-io = "0.7.1"
embedded-storage = "0.3.1"
heapless = "0.9.3"
static_cell = "2.1.1"
defmt = { version = "1.1.0", optional = true }
defmt-rtt = { version = "1.2.0", optional = true }
panic-probe = { version = "1.0.0", optional = true }
rtt-target = { version = "0.6.2", optional = true }

[features]
probe-debug = ["dep:defmt", "dep:defmt-rtt", "dep:panic-probe", "dep:rtt-target"]
```

Use rules_rust crate integration to materialize these into Bazel targets. Cargo may remain a metadata input for crate resolution, but Cargo must not become the authoritative build, test, feature, or packaging entrypoint.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Build authority | Bazel 9.1.0 with Bzlmod | Cargo workspace plus CMake or `xtask` | Cargo is strong for Rust-only work, but this firmware needs one graph for Rust, C/ASM, generated assets, simulator tests, and firmware packaging. |
| Rust Bazel rules | rules_rust 0.70.0 | Handwritten `genrule` calls to `rustc` | Handwritten rustc actions lose toolchain semantics, dependency metadata, test support, and future IDE/build integration. |
| Runtime | Retained FreeRTOS with Rust adapters | Embassy or RTIC as primary runtime | Good greenfield runtimes, but adopting them now would change scheduling and interrupt/task semantics during a behavior-parity Big Bang rewrite. Consider later only after parity tests prove timing-sensitive behavior. |
| MCU/HAL layer | Retained STM32 HAL/CMSIS C with Rust wrappers | Community STM32 HAL crates as the foundation | Community HAL crates are useful, but this project already has board-specific vendor behavior. Replace peripheral areas only after a board-by-board parity proof. |
| Hardware traits | `embedded-hal` 1.0.0 | `embedded-hal` 0.2.x | 1.0.0 is the current stable trait set. Legacy drivers should be shimmed at boundaries instead of pulling old traits into new code. |
| Logging/debug | Existing production logging plus optional defmt/probe-rs debug profile | Replace product logging wholesale with defmt | defmt is excellent for constrained debug logs, but production logging is externally visible behavior and should not change until parity requirements approve it. |
| Packaging | Bazel-owned firmware package rules, with rules_pkg where it fits | Shell scripts outside Bazel | Artifact identity, map files, `.bin`, `.bbf`, `.dfu`, metadata, and signing/checksum steps must be reproducible and testable in the graph. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| CMake as the authoritative build during the rewrite | Conflicts with the selected Bazel Primary Now migration and makes parity artifacts depend on two graphs | Bazel owns the graph; CMake can be read as source material only. |
| Cargo as the product build authority | Cannot directly own retained C/ASM/vendor libraries, generated firmware resources, and product packages as one embedded graph | rules_rust and Bzlmod with Cargo metadata as an input, not the driver. |
| Scheduler replacement in the first rewrite phase | Changes runtime behavior while the language, architecture, and build system are already changing | Keep FreeRTOS, wrap it, then evaluate scheduler alternatives after parity. |
| Runtime-wide heap as the default firmware model | Hides memory budgets and failure modes on constrained MCUs | Prefer `heapless`, `static_cell`, explicit arenas, and typed capacities. |
| Raw FFI spread through domain code | Makes illegal states, lifetimes, task ownership, and error handling hard to reason about | Put FFI in thin adapter crates and expose typed, fallible Rust APIs. |
| Generated `#define`-style Rust constants as the main configuration model | Recreates the current feature-gate complexity without stronger invariants | Generate typed board/printer/config models and parse at Bazel-owned boundaries. |
| `embedded-hal` 0.2.x in new public APIs | Locks new code to legacy traits | Use `embedded-hal` 1.0.0 and isolate legacy drivers behind shims. |
| `probe-run` as the main debug tool | probe-rs is the current host-side project/tooling direction | Use `probe-rs` directly for probe workflows. |

## Stack Patterns by Variant

### Pure Firmware Core

Use `std`-enabled host builds for fast unit tests and `no_std` firmware builds for target integration. This is where most behavior parity tests should live.

Recommended crates/modules:

```text
crates/firmware_core/
  src/lib.rs
  src/gcode.rs
  src/gcode/
  src/motion.rs
  src/motion/
  src/thermal.rs
  src/thermal/
  src/config.rs
  src/config/
```

Rules:

- Model invariants with newtypes and enums: temperature ranges, axis IDs, planner states, fan PWM limits, bed mesh dimensions, printer model capabilities, transfer states, and persistent-store schema versions.
- Use `foo.rs` plus `foo/` directories for multi-file modules.
- Prefer `let...else` guards for early exits.
- Prefix optional values with `maybe_`.
- Keep hardware, FreeRTOS, filesystem, networking, and UI side effects out of this layer.
- Add Bazel `rust_test` targets for pure logic first; unit tests should use Arrange, Act, Assert comments when they improve clarity.

### Board and Runtime Adapter Layer

Use one adapter boundary per external subsystem:

```text
crates/firmware_board/
crates/firmware_hal_stm32/
crates/firmware_rtos_freertos/
crates/firmware_fs/
crates/firmware_net/
crates/firmware_usb/
crates/firmware_ui_adapter/
```

Rules:

- Retained C libraries are `cc_library` targets.
- Rust wrappers are `rust_library` targets with minimal `unsafe` modules.
- FFI types do not cross into pure core crates.
- Each adapter parses C/global/raw state into typed Rust values at the boundary.
- Adapter APIs should return typed errors; do not swallow C status codes.

### Firmware Images

Use Bazel platforms and configuration settings for printer/board variants:

```text
//platforms/printer:mk4_xbuddy
//platforms/printer:mk3_5_xbuddy
//platforms/printer:mini_buddy
//platforms/printer:xl_xbuddy
```

Each image target should declare:

- Board target triple.
- Linker script.
- Memory layout.
- Startup ownership: retained vendor startup or Rust `cortex-m-rt`, not both.
- Feature set as typed generated Rust inputs.
- Artifact outputs: ELF, BIN, DFU where applicable, BBF package, map file, size report, manifest/checksums.

### Host Tools and Simulator Tests

Use `std` Rust and Python under Bazel:

- `rust_binary` for new deterministic generators and package tools.
- `py_test` or Bazel-wrapped pytest for existing simulator/parity flows.
- `rust_test` for host-only pure firmware logic.
- `sh_test` only for thin smoke checks when a native rule is not practical.

## Version Compatibility

| Area | Recommendation | Notes |
|------|----------------|-------|
| Bazel / rules_rust | Bazel 9.1.0 with rules_rust 0.70.0 | Bazel 9 removed old C++ provider compatibility paths that can break older rules. Pin current rulesets and avoid stale transitive rule versions. |
| Rust / rules_rust | Rust 1.96.0 registered explicitly through rules_rust | rules_rust 0.70.0 has an MSRV below this. Register stable Rust rather than using the rules default toolchain version. |
| Rust editions | Edition 2024 for new crates | Avoid edition drift across the rewrite unless a third-party crate forces a narrower choice. |
| Cortex-M targets | Official Rust target triples listed above | Confirm exact FPU ABI per board before final platform definitions. The F4/M4F case should use hardfloat; H5/M33 must be verified per MCU/board. |
| `no_std` and allocation | `no_std` by default; optional `alloc` only with an explicit memory budget | `libcore` is the base environment for firmware. Use `std` only in host/test/build tools. |
| `embedded-hal` | 1.0.0 for new APIs | Isolate any driver requiring 0.2.x behind compatibility adapters. |
| defmt/probe-rs | defmt 1.1.0, defmt-rtt 1.2.0, probe-rs 0.31.0 | Treat as debug profile tooling unless production logging parity is intentionally changed. |
| rules_python | 2.0.2 | Use for existing Python tooling/tests under Bazel; do not keep Python as an untracked side channel. |
| rules_pkg | 1.2.0 | Useful for packaging primitives, but firmware-specific package/sign/checksum rules may still need custom Starlark. |

## Sources

- Bazel releases, 9.1.0 latest release: https://github.com/bazelbuild/bazel/releases/tag/9.1.0
- Bazel Bzlmod / external dependencies docs: https://bazel.build/docs/bzlmod
- Bazel platforms docs: https://bazel.build/docs/platforms
- Bazel Central Registry, rules_rust 0.70.0: https://registry.bazel.build/modules/rules_rust
- rules_rust docs: https://bazelbuild.github.io/rules_rust/
- rules_rust 0.70.0 release: https://github.com/bazelbuild/rules_rust/releases/tag/0.70.0
- Bazel Central Registry, rules_cc 0.2.19: https://registry.bazel.build/modules/rules_cc
- Bazel Central Registry, rules_python 2.0.2: https://registry.bazel.build/modules/rules_python
- Bazel Central Registry, rules_pkg 1.2.0: https://registry.bazel.build/modules/rules_pkg
- Rust stable channel manifest, Rust 1.96.0: https://static.rust-lang.org/dist/channel-rust-stable.toml
- Rust platform support target list: https://doc.rust-lang.org/rustc/platform-support.html
- Rust Embedded Book, `no_std`: https://docs.rust-embedded.org/book/intro/no-std.html
- cortex-m crate: https://crates.io/crates/cortex-m
- cortex-m-rt crate: https://crates.io/crates/cortex-m-rt
- embedded-hal crate: https://crates.io/crates/embedded-hal
- embedded-io crate: https://crates.io/crates/embedded-io
- embedded-storage crate: https://crates.io/crates/embedded-storage
- critical-section crate: https://crates.io/crates/critical-section
- heapless crate: https://crates.io/crates/heapless
- static_cell crate: https://crates.io/crates/static_cell
- defmt crate: https://crates.io/crates/defmt
- defmt-rtt crate: https://crates.io/crates/defmt-rtt
- panic-probe crate: https://crates.io/crates/panic-probe
- rtt-target crate: https://crates.io/crates/rtt-target
- probe-rs crate: https://crates.io/crates/probe-rs
- probe-rs project docs: https://probe.rs/
- just 1.51.0 release: https://github.com/casey/just/releases/tag/1.51.0
- Bright Builds architecture standard: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md
- Bright Builds Rust standard: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md
