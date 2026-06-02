# Architecture Research

**Domain:** Behavior-parity Rust+Bazel embedded firmware rewrite
**Project:** Prusa-Firmware-Buddy Rust port
**Researched:** 2026-06-02
**Confidence:** HIGH for architectural direction; MEDIUM for exact embedded Rust toolchain triples until the first Bazel toolchain spike validates each MCU/FPU combination.

## Standard Architecture

### System Overview

The replacement should be a Rust firmware product family built by Bazel, not a Rust translation of the existing CMake source tree. The current C/C++ firmware remains the behavioral reference and parity oracle, while the Rust implementation owns the release path once parity gates pass.

```text
+--------------------------------------------------------------------------------+
| Bazel product matrix and release graph                                          |
| MODULE.bazel, platforms, toolchains, product macros, generated assets, packages |
+-------------------------------------------+------------------------------------+
                                            |
                                            v
+--------------------------------------------------------------------------------+
| Firmware entry binaries                                                         |
| master boards: Buddy/XBuddy/XLBuddy/XL dev kit                                  |
| auxiliary boards: Dwarf/ModularBed/xBuddy Extension                             |
+-------------------------------------------+------------------------------------+
                                            |
                                            v
+--------------------------------------------------------------------------------+
| Imperative shell and adapters                                                   |
| boot/startup, linker scripts, HAL/PAC/vendor C, FreeRTOS, LwIP, mbedTLS, FS, UI |
+-------------------------------------------+------------------------------------+
                                            |
                                            v
+--------------------------------------------------------------------------------+
| Application orchestrators                                                       |
| print controller, connect controller, transfer controller, UI controller, puppies|
+-------------------------------------------+------------------------------------+
                                            |
                                            v
+--------------------------------------------------------------------------------+
| Pure Rust domain crates                                                         |
| printer model, board features, G-code, motion intents, thermal policy, config,  |
| Connect protocol, transfer state machines, UI state, resources, puppy protocol  |
+-------------------------------------------+------------------------------------+
                                            |
                                            v
+--------------------------------------------------------------------------------+
| Retained foreign code packages and reference harnesses                          |
| explicit cc_library/vendor inventories, C ABI shims, golden artifacts, simulator|
+--------------------------------------------------------------------------------+
```

This is functional core / imperative shell adapted to embedded firmware. The core owns decisions that can be expressed as data-in/data-out transformations: printer capability modeling, G-code parsing, print state transitions, Connect command validation, transfer lifecycle, persistent configuration migrations, UI navigation state, resource manifest validation, puppy register protocol, and safety policy decisions. The shell owns things that cannot be pure: reset vectors, clocks, interrupts, FreeRTOS tasks, queues, DMA, filesystems, sockets, TLS, display/touch I/O, watchdogs, flash writes, random numbers, and logging sinks.

The important architecture rule is that build variability and hardware variability must terminate at typed boundaries. Domain crates should not be littered with `#[cfg(printer = "...")]` and `select()` equivalent logic. Bazel selects the product, generated build metadata constructs a typed `ProductProfile`, adapters implement the required capabilities, and the domain core receives explicit types that make illegal combinations unrepresentable.

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `bazel/platforms` | Model supported printers, boards, MCUs, bootloader modes, display classes, resource modes, and execution/target platforms. | `constraint_setting`, `constraint_value`, `platform`, `config_setting`, and product-specific macros. |
| `bazel/toolchains` | Register Rust, C/C++, objcopy, linker, bindgen, Python/codegen, and host test toolchains. | Bzlmod, `rules_rust`, C/C++ toolchain config, hermetic host tools where practical. |
| `bazel/firmware_rules` | Provide firmware-level rules/macros for ELF, BIN, BBF, DFU, map files, generated option crates, resource images, and parity tests. | Starlark rules over `rust_binary`, `cc_library`, `genrule` only as a short-term bridge. |
| `crates/domain/*` | Pure `no_std` printer behavior and protocol/domain modeling. | `rust_library` crates with `alloc` avoided unless a crate has an explicit bounded allocator story. |
| `crates/application/*` | Task-independent orchestration over domain services and adapter traits. | `rust_library` crates that accept trait objects or generics for time, storage, transport, UI, logging, and hardware effects. |
| `crates/adapters/*` | Boundaries to HAL, FreeRTOS, LwIP, mbedTLS, FatFs/littlefs, TinyUSB, display/touch, retained C, and generated resources. | Thin `unsafe`-containing crates with safe wrappers and explicit ownership/lifetime contracts. |
| `firmware/*` | Board/personality entrypoints and task wiring. | Small `rust_binary` targets with linker scripts, startup/runtime selection, panic handler, task graph, and adapter assembly. |
| `foreign/*` | Retained C/ASM/vendor code with explicit ownership and visibility. | `cc_library`, `filegroup`, `rust_bindgen_library` only for curated headers, and manual C shims where C++ or macro-heavy HAL headers are involved. |
| `assets/*` and `tools/*` | Source assets, code generators, packaging tools, and release metadata. | Host `rust_binary`, `py_binary`, `sh_binary`, custom Starlark rules, and deterministic generated outputs. |
| `tests/parity/*` | Prove behavioral parity against existing C/C++ reference. | Golden corpus tests, simulator comparisons, generated-asset diffs, reference artifact checks, and hardware smoke definitions. |

## Recommended Project Structure

```text
Prusa-Firmware-Buddy/
|-- MODULE.bazel                  # Bazel module root; rules_rust, rules_cc, rules_pkg, crate deps
|-- .bazelrc                      # Canonical build/test configs for host and embedded products
|-- justfile                      # Developer workflow facade over Bazel and Rust checks
|-- bazel/
|   |-- platforms/                # printer/board/MCU/display/resource constraints and platforms
|   |-- toolchains/               # Rust/C/C++/objcopy/linker/Python/bindgen toolchains
|   |-- firmware_rules/           # product macros, firmware image rules, parity rule helpers
|   |-- codegen/                  # rules for options, translations, resources, fonts, manifests
|   `-- transitions/              # only if product transitions are unavoidable
|-- crates/
|   |-- domain/
|   |   |-- printer_model/         # product profiles, capabilities, typed feature sets
|   |   |-- gcode/                 # parser, validation, canonical command model
|   |   |-- motion/                # motion/planner intents and safety envelopes
|   |   |-- thermal/               # thermal policy, heaters, sensors, safety state
|   |   |-- config_schema/         # persistent settings, journal IDs, migrations
|   |   |-- connect_protocol/      # Connect commands, telemetry/events, registration model
|   |   |-- transfer_model/        # download/partial-file/slot state machines
|   |   |-- ui_model/              # screens, dialogs, navigation state, view data
|   |   |-- resources_manifest/    # revisions, resource hashes, bootloader/resource decisions
|   |   `-- puppies_protocol/      # Modbus/register/bootstrap domain for auxiliary boards
|   |-- application/
|   |   |-- print_controller/      # serializes print requests into domain actions
|   |   |-- connect_controller/    # maps Connect protocol to printer/application state
|   |   |-- transfer_controller/   # orchestrates storage + network transfers
|   |   |-- ui_controller/         # maps input/events/domain state to UI model
|   |   `-- startup_controller/    # typed startup dependency graph and recovery decisions
|   |-- adapters/
|   |   |-- hal_stm32/             # PAC/HAL/vendor-safe wrapper, GPIO/DMA/ADC/timers/UART/SPI/I2C
|   |   |-- rtos_freertos/         # task, queue, mutex, event group wrappers
|   |   |-- net_lwip/              # network device, DNS, TCP/UDP sockets, mDNS/SNTP shell
|   |   |-- tls_mbedtls/           # TLS session, cert store, hardware RNG, custom CA path
|   |   |-- fs_fatfs/              # USB/removable media filesystem adapter
|   |   |-- fs_littlefs/           # internal/resource filesystem adapter
|   |   |-- usb_tinyusb/           # USB host/device adapter
|   |   |-- display_touch/         # display, touch, backlight, frame scheduling
|   |   |-- logging/               # component registry and sinks
|   |   `-- vendor_ffi/            # curated FFI shims for retained C/C++/ASM code
|   `-- support/
|       |-- bounded_collections/   # capacity types and heapless aliases used across firmware
|       |-- time/                  # monotonic clocks, deadlines, test clocks
|       `-- diagnostics/           # crash/error/report models shared by shell and host tests
|-- firmware/
|   |-- master/                    # Buddy/XBuddy/XLBuddy master firmware binaries
|   |-- dwarf/                     # Dwarf auxiliary firmware binary
|   |-- modularbed/                # ModularBed auxiliary firmware binary
|   `-- xbuddy_extension/          # xBuddy Extension firmware binary
|-- foreign/
|   |-- cmsis/
|   |-- stm32_hal/
|   |-- freertos/
|   |-- lwip/
|   |-- mbedtls/
|   |-- fatfs/
|   |-- littlefs/
|   |-- tinyusb/
|   |-- crashcatcher/
|   |-- marlin_reference/          # reference-only unless an explicit C ABI bridge is approved
|   `-- prusa_error_codes/
|-- assets/
|   |-- gui/
|   |-- translations/
|   |-- resources/
|   |-- web/
|   |-- esp/
|   `-- puppy_firmware/
|-- tools/
|   |-- codegen/
|   |-- packaging/
|   |-- simulator/
|   `-- parity/
`-- tests/
    |-- unit/                      # pure domain/application tests
    |-- adapter_contract/          # host stubs and adapter contract tests
    |-- parity/                    # reference-vs-Rust golden tests
    |-- simulator/                 # simulator-driven parity and integration flows
    `-- hardware/                  # documented hardware smoke/test matrix
```

### Structure Rationale

- **`bazel/` owns product composition.** The current CMake build centralizes product selection in `ProjectOptions.cmake`, generated option headers, and one global `firmware` target. Bazel should replace that with explicit packages, platforms, visibility, and product macros so board/printer decisions are visible at analysis time.
- **`crates/domain/` is the stable core.** It should compile for host tests and embedded targets, depend on `core` and fixed-capacity types, and avoid HAL/RTOS/network/UI imports.
- **`crates/application/` is the typed orchestration layer.** It can sequence operations, but it should depend on domain crates plus adapter traits, not concrete vendor APIs.
- **`crates/adapters/` contains effects and `unsafe`.** Each adapter has one reason to change and one external dependency family. This prevents the current "global include surface" problem from reappearing as a global Rust module.
- **`firmware/` entrypoints stay small.** Board binaries wire selected profiles, adapters, startup, and tasks. Long task loops belong in application crates or adapters, not in `main.rs`.
- **`foreign/` is not a dumping ground.** Every retained C, ASM, C++, or vendor component must have a named package, owner, reason for retention, replacement posture, and visibility limited to its adapter.
- **Generated outputs are Bazel outputs.** Source assets live under `assets/`; generated Rust constants, resource images, hash manifests, BBF/DFU products, and comparison reports are build/test outputs unless a tracked snapshot is explicitly required.
- **Rust modules follow `foo.rs` plus `foo/`.** Crate roots remain `lib.rs` or `main.rs`; multi-file modules should use the Bright Builds Rust layout for new/touched code.

## Architectural Patterns

### Pattern 1: Functional Core, Imperative Shell

**What:** Keep firmware decisions in pure Rust functions and state machines. Effects are passed in through narrow traits or handled after the core returns an action.

**When to use:** G-code handling, Connect command handling, transfer state, persistent migrations, UI navigation, selftest decisions, puppy bootstrap decisions, thermal safety state, and resource validation.

**Trade-offs:** This introduces more explicit types and action enums, but it makes host tests cheap and parity fixtures reusable across host, simulator, and hardware tests.

**Example:**

```rust
pub enum PrintAction {
    QueueGcode(GcodeCommand),
    StartFile(PrintFileId),
    Reject(CommandRejection),
}

pub fn decide_print_action(
    profile: &ProductProfile,
    state: &PrinterState,
    command: RemoteCommand,
) -> Result<PrintAction, CommandError> {
    let RemoteCommand::StartPrint { path } = command else {
        return Ok(PrintAction::Reject(CommandRejection::Unsupported));
    };

    let file = PrintFileId::try_from(path)?;
    if !profile.capabilities.can_print_from(&file) {
        return Ok(PrintAction::Reject(CommandRejection::UnsupportedStorage));
    }

    if !state.is_idle_for_new_print() {
        return Ok(PrintAction::Reject(CommandRejection::Busy));
    }

    Ok(PrintAction::StartFile(file))
}
```

The FreeRTOS task, Connect socket, filesystem, and Marlin-reference comparison harness should call this function; none of them should own the decision.

### Pattern 2: Typed Product Matrix Instead of Macro Drift

**What:** Represent printer, board, MCU, display, resources, translations, Connect/WUI, puppies, and bootloader modes as typed Rust values and Bazel platform constraints.

**When to use:** Anything currently modeled by `PRINTER`, `BOARD`, generated `option/*.h`, `BOARD_IS_*()`, `PRINTER_IS_*()`, `HAS_GUI()`, `HAS_PUPPIES()`, `BUDDY_ENABLE_CONNECT()`, or package-time source selection.

**Trade-offs:** Build settings must be designed upfront, but invalid combinations fail during Bazel analysis or profile construction instead of compiling into ad hoc runtime branches.

**Example:**

```rust
pub enum Printer {
    CoreOne,
    Mini,
    Mk4,
    Mk35,
    Xl,
    Ix,
    XlDevKit,
}

pub enum Board {
    Buddy,
    XBuddy,
    XlBuddy,
    Dwarf,
    ModularBed,
    XlDevKitXlb,
    XBuddyExtension,
}

pub struct ProductProfile {
    pub printer: Printer,
    pub board: Board,
    pub display: Option<DisplayProfile>,
    pub networking: NetworkingProfile,
    pub resources: ResourceProfile,
    pub puppies: PuppyProfile,
}

impl ProductProfile {
    pub fn new(printer: Printer, board: Board, features: FeatureSet) -> Result<Self, ProductError> {
        FeatureSet::validate_for(printer, board, &features)?;
        Ok(Self {
            printer,
            board,
            display: features.display_for(printer, board)?,
            networking: features.networking_for(board),
            resources: features.resources_for(printer, board),
            puppies: features.puppies_for(printer, board),
        })
    }
}
```

Bazel should generate or select the raw values; Rust constructors should enforce the semantic invariants.

### Pattern 3: Adapter Crates with Safe Facades

**What:** Put each external effect behind a tiny facade. The facade is the only code allowed to touch raw HAL handles, FreeRTOS handles, C pointers, C strings, filesystem device tables, socket descriptors, TLS contexts, or display buffers.

**When to use:** HAL, FreeRTOS, LwIP, mbedTLS, FatFs, littlefs, TinyUSB, CrashCatcher, STM32 startup/linker code, GUI rendering, hardware RNG, and retained vendor functions.

**Trade-offs:** Adapter APIs require careful design, but they localize `unsafe`, make ownership visible, and prevent domain crates from importing volatile infrastructure.

**Example:**

```rust
pub trait EventGroup {
    fn provide(&self, dependency: StartupDependency);
    fn wait_for(&self, dependency: StartupDependency, deadline: Deadline) -> Result<(), WaitError>;
}

pub struct FreeRtosEventGroup {
    raw: NonNull<freertos_sys::EventGroupHandle>,
}

impl EventGroup for FreeRtosEventGroup {
    fn provide(&self, dependency: StartupDependency) {
        unsafe {
            freertos_sys::xEventGroupSetBits(self.raw.as_ptr(), dependency.bits());
        }
    }

    fn wait_for(&self, dependency: StartupDependency, deadline: Deadline) -> Result<(), WaitError> {
        let result = unsafe {
            freertos_sys::xEventGroupWaitBits(
                self.raw.as_ptr(),
                dependency.bits(),
                false,
                true,
                deadline.ticks(),
            )
        };
        WaitResult::from_bits(result, dependency)
    }
}
```

Only the adapter owns the raw handle. Application code sees the `EventGroup` contract.

### Pattern 4: Bazel Packages Mirror Ownership Boundaries

**What:** Use Bazel packages and visibility to encode ownership. A package is not just a directory; it is an API boundary. Default to private visibility and expose only facade targets.

**When to use:** Every subsystem boundary: domain crates, adapter crates, foreign code, generated outputs, board packages, packaging tools, and parity tests.

**Trade-offs:** More `BUILD.bazel` files exist than in the current CMake model, but dependency direction becomes inspectable with `bazel query` and enforceable during analysis.

**Example:**

```starlark
package(default_visibility = ["//visibility:private"])

load("@rules_rust//rust:defs.bzl", "rust_library", "rust_test")

rust_library(
    name = "transfer_model",
    srcs = ["src/lib.rs"],
    edition = "2024",
    deps = [
        "//crates/domain/printer_model",
        "//crates/support/bounded_collections",
    ],
    visibility = ["//crates/application/transfer_controller:__pkg__"],
)

rust_test(
    name = "transfer_model_test",
    crate = ":transfer_model",
)
```

`select()` belongs in Bazel packages that assemble products or adapters. Domain packages should receive typed inputs instead of querying build flags.

### Pattern 5: Reference Firmware as Parity Oracle, Not Runtime Dependency

**What:** Keep the existing C/C++ firmware build callable from Bazel for comparison, fixture generation, simulator tests, and release artifact diffs. Do not make production Rust firmware depend on Marlin/CMake to run, except for explicitly retained vendor code behind an approved boundary.

**When to use:** Big Bang migration phases where reference behavior must be proven before replacing release outputs.

**Trade-offs:** The reference build still exists for a while, but its role is test data and oracle. This avoids incremental dual-ownership as the production architecture.

**Example parity target shape:**

```text
//reference/cmake:mk4_xbuddy_reference_bbf
//firmware/master:mk4_xbuddy_rust_bbf
//tests/parity/release:mk4_xbuddy_bbf_manifest_diff
//tests/parity/gcode:planner_corpus_test
//tests/simulator:mk4_print_flow_reference_vs_rust
```

### Pattern 6: Generated Assets as First-Class Build Outputs

**What:** Translation tables, required-char lists, font data, QOI images, resource hashes, web resources, ESP blobs, puppy firmware blobs, option metadata, BBF manifests, and DFU packages are modeled as Bazel outputs with deterministic inputs.

**When to use:** Everything currently generated by `ProjectOptions.cmake`, `src/resources/CMakeLists.txt`, `src/lang/CMakeLists.txt`, `utils/resources`, `utils/translations_and_fonts`, `utils/pack_fw.py`, and `utils/mklittlefs.py`.

**Trade-offs:** Some Python generators may be retained initially, but Bazel must declare their inputs/outputs and test drift. Over time, critical generators should become Rust host tools or well-scoped Python tools with hermetic dependencies.

**Rule:** Generated files consumed by firmware should be generated in the same Bazel package as their producing rule or exposed through a generated crate/package. Avoid generating into another package or relying on source-tree side effects.

## Data Flow

### Boot and Runtime Flow

```text
reset vector/startup ASM
    -> firmware/<personality>/main.rs
    -> board ProductProfile + linker/memory profile
    -> HAL clock/peripheral init through hal_stm32
    -> FreeRTOS scheduler/task creation through rtos_freertos
    -> startup_controller typed dependency graph
    -> application controllers
    -> pure domain decisions
    -> adapter actions
```

The boot shell may be imperative, but startup dependencies should be a typed graph, not raw event-bit arithmetic spread across tasks. Current `TaskDeps` semantics should become a domain/application model with a FreeRTOS adapter.

### Print Command Flow

```text
GUI / Connect / WUI / serial input
    -> boundary parser into GcodeCommand or RemoteCommand
    -> print_controller pure validation and state transition
    -> PrintAction enum
    -> motion/thermal/storage/queue adapters
    -> state snapshot
    -> UI/Connect/telemetry event projections
```

The replacement should preserve the current serialized Marlin server/client property: one owner serializes print operations, while GUI, Connect, transfers, and auxiliary tasks submit typed requests and receive snapshots/events. The new owner should be a Rust print controller rather than a direct copy of `marlin_server.cpp`.

### Network, Connect, WUI, and Transfer Flow

```text
LwIP socket / WUI request / Connect websocket
    -> net_lwip or tls_mbedtls adapter
    -> protocol parser into domain command/event type
    -> connect_controller or transfer_controller
    -> pure state-machine decision
    -> filesystem/print/network action
    -> telemetry/event response rendering
```

Protocol parsing, command validation, duplicate command handling, proxy/TLS policy, and partial-file transfer state must be testable without live sockets, TLS sessions, or USB media.

### UI Flow

```text
touch/buttons/timers/domain events
    -> ui_controller
    -> ui_model state transition
    -> view data / dialog action / print action
    -> display_touch adapter render
```

The GUI replacement should separate view state and workflow decisions from pixels, display buffers, and touch drivers. This enables golden UI state tests for existing screens/dialogs without requiring hardware display tests for every branch.

### Generated Asset and Release Flow

```text
source assets / translations / web files / firmware blobs / product profile
    -> Bazel codegen rules
    -> generated Rust manifest crates + resource images
    -> firmware link/package rules
    -> ELF/BIN/BBF/DFU/map products
    -> parity diff tests against reference artifacts
```

Generated asset drift should be a `bazel test` failure, not a manual review convention.

### Parity Flow

```text
reference C/C++ firmware build or simulator
    -> golden fixtures, logs, state snapshots, release artifacts
Rust firmware build or simulator
    -> comparable fixtures, logs, state snapshots, release artifacts
parity harness
    -> exact match, tolerated intentional delta, or failing report
```

Known defects from `.planning/codebase/CONCERNS.md` must be classified as either "parity preserved for now" or "intentional fixed delta". Intentional deltas need explicit tests and roadmap notes so parity failures are explainable.

## State Management

State should be partitioned by ownership, not convenience:

| State | Owner | Rule |
|-------|-------|------|
| Product profile | Generated Bazel metadata plus Rust constructor | Immutable after boot; invalid combinations fail early. |
| Startup readiness | `startup_controller` + RTOS adapter | Typed dependencies; raw event bits stay inside adapter. |
| Print/motion/thermal state | `print_controller` and domain crates | Single writer; readers receive snapshots/events. |
| UI navigation/dialog state | `ui_model` and `ui_controller` | Pure transitions; renderer is an adapter. |
| Connect/WUI command state | `connect_controller` and protocol crates | Duplicate/background command behavior modeled as a state machine. |
| Transfer state | `transfer_model` and `transfer_controller` | Single active-slot semantics represented in types. |
| Persistent config | `config_schema` and storage adapter | Hash IDs, migrations, deprecated items, and defaults covered by tests. |
| Resources | `resources_manifest` plus generated data | Revisions/hashes are deterministic build outputs. |
| Puppy/auxiliary state | `puppies_protocol` and application controller | Modbus registers and bootloader state modeled as typed states. |
| Hardware handles | Adapter crates only | No raw handles in domain/application crates. |

## Bazel Package and Platform Model

### Product Constraints

Create constraint settings for current product axes:

| Axis | Values to model |
|------|-----------------|
| Printer | `COREONE`, `MINI`, `MK4`, `MK3_5`, `XL`, `iX`, `XL_DEV_KIT` |
| Board | `BUDDY`, `XBUDDY`, `XLBUDDY`, `DWARF`, `MODULARBED`, `XL_DEV_KIT_XLB`, `XBUDDY_EXTENSION` |
| MCU | `STM32F407VG`, `STM32F429VI`, `STM32F427ZI`, `STM32G070RBT6`, `STM32H503CBU7` |
| Personality | `master`, `dwarf`, `modularbed`, `xbuddy_extension` |
| Bootloader | `no`, `empty`, `yes` |
| Display | `none`, `240x320`, `480x320` |
| Resources | `none`, `internal`, `external_flash` |
| Networking | `none`, `wui`, `connect_wui` |
| Auxiliary boards | `none`, `puppies`, `puppies_bootloader` |

Use platform targets for valid products, for example `//bazel/platforms:mk4_xbuddy`, `//bazel/platforms:mini_buddy`, `//bazel/platforms:xl_xlbuddy`, `//bazel/platforms:dwarf`, and `//bazel/platforms:modularbed`. Do not make arbitrary combinations buildable just because the individual constraints exist.

### Toolchains

Use `rules_rust` with Bzlmod as the primary Rust integration. Register explicit Rust toolchains for the embedded triples needed by the MCU families and host triples for tests/tools. The likely mapping is:

| MCU family | Likely Rust target family | Confidence |
|------------|---------------------------|------------|
| STM32F407/F427/F429 | Cortex-M4F, likely `thumbv7em-none-eabihf` | MEDIUM until linker/FPU flags are verified. |
| STM32G070 | Cortex-M0+, likely `thumbv6m-none-eabi` | MEDIUM until startup and interrupt model are verified. |
| STM32H503 | Cortex-M33 target, exact `thumbv8m.main-*` variant needs validation | LOW until silicon/FPU configuration is confirmed. |

The roadmap should include an early toolchain spike that proves: Rust target triple, panic strategy, linker script, vector table/startup, `objcopy`, map generation, debug symbols, and one minimal board binary per MCU family.

### Dependency Strategy

Because this firmware has heavy interaction with generated assets, foreign code, custom linker scripts, and target platforms, Bazel should be the dependency authority. Use `crate_universe` direct specs or a carefully controlled Cargo workspace only if it is kept subordinate to Bazel. Cargo may remain useful for IDE metadata and local crate checks, but release artifacts must be produced by Bazel.

Use `rust_library` for domain/application crates, `rust_test` for host tests, `rust_binary` for firmware entrypoints, and `cc_library`/`cc_import` for retained C/ASM/vendor code. Use `rust_static_library` only when exporting Rust to another build system or explicit C/C++ integration requires it; when building the whole firmware in Bazel, prefer ordinary Rust crates linked by the Bazel firmware target.

## Retained C, ASM, C++, and Vendor Code Policy

The Big Bang rewrite does not mean "rewrite every byte before the first boot." It means the production firmware architecture is Rust+Bazel, and any retained foreign implementation is explicit, isolated, and justified.

### Retention Inventory

Each retained component needs an entry like:

| Field | Required content |
|-------|------------------|
| Bazel package | Example: `//foreign/mbedtls` |
| Upstream/source | In-repo vendor path and upstream version/commit if known |
| Retention reason | Certification, hardware vendor support, complexity, temporary parity bridge, or no Rust replacement yet |
| Boundary | C ABI shim, manual externs, bindgen allowlist, or reference-only |
| Safe facade | Rust adapter crate exposing safe domain/application-facing API |
| Replacement posture | Retain indefinitely, replace after parity, or replace after hardware tests |
| Tests | Bindgen/header smoke, adapter contract, simulator/hardware smoke, or parity corpus |

### Explicit Recommendations

- **Startup ASM and linker scripts:** retain initially. Wrap them in board packages and validate vector table, memory regions, stack, interrupt dispatch, bootloader offsets, and map files. Rust may use `cortex-m-rt` patterns later, but existing linker scripts are part of release parity.
- **CMSIS and STM32 HAL:** retain initially behind `hal_stm32`. Expose safe Rust abstractions for only the peripherals the application needs. Do not bindgen entire HAL headers into general-purpose Rust APIs.
- **FreeRTOS:** retain initially behind `rtos_freertos`. Model tasks, queues, mutexes, semaphores, timers, and event groups as typed Rust wrappers. Do not leak raw handles outside the adapter.
- **LwIP, mbedTLS, FatFs, littlefs, TinyUSB, CrashCatcher:** retain initially behind dedicated adapters. Their C APIs are stable enough for narrow facades and parity tests.
- **Marlin:** treat as behavioral reference, not as production runtime, unless a specific phase approves a temporary C ABI bridge. Rust cannot call C++ directly without a C interface, and carrying Marlin as runtime would undermine the replacement architecture.
- **Prusa error codes, MMU firmware, ESP blobs, puppy blobs, WUI assets:** treat as data/generated/resource dependencies with Bazel packaging rules and explicit version/hash checks.
- **C++ vendor libraries:** prefer C shims over direct generated bindings. If retained, keep C++ targets reference-only or hidden behind a C ABI package.

## Parity Harness Architecture

Parity is a first-class architecture component, not an end-of-project test sweep.

| Harness | Purpose | Roadmap priority |
|---------|---------|------------------|
| Product matrix build parity | Rust Bazel builds every currently supported printer/board/bootloader/resource artifact. | Phase 1 |
| Reference artifact diff | Compare ELF metadata, BIN size bands, BBF/DFU manifests, resource revisions, map summaries, and generated assets. | Phase 1-2 |
| Pure domain corpus | Run G-code, Connect commands, transfers, config migrations, puppy messages, and UI state fixtures through Rust core. | Phase 2 |
| Reference-vs-Rust simulator | Drive the same print/network/UI scenarios through current simulator/reference and Rust simulator. | Phase 3 |
| Adapter contract tests | Stub HAL/RTOS/network/filesystem adapters on host and prove application behavior. | Phase 2-3 |
| Hardware smoke matrix | Boot, safe state, display, input, storage, network, heating/motion locks, puppy bootstrap, crash/error paths. | Phase 4+ |
| Intentional delta registry | Document known bug fixes and behavior changes surfaced from concerns audit. | Continuous |

The parity harness should compare observable behavior, not implementation details. Examples: accepted/rejected commands, state snapshots, telemetry payloads, transfer state, config migration outputs, UI dialog transitions, resource hashes, and release packaging. For known defects such as custom TLS DER loading, probe variance math, GUI freeze paths, disabled transfer progress, and MMU availability stubs, parity tests should either preserve current behavior temporarily or record an intentional fixed delta with new expected behavior.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| First boot on one master board | Minimal Rust binary, retained startup/HAL/FreeRTOS, generated `ProductProfile`, one pure domain slice, one reference parity check. |
| Full current product matrix | Bazel platforms per valid product, shared domain crates, adapter variants selected by platform, generated assets under Bazel, per-product parity artifacts. |
| All current printers plus auxiliary firmware | Separate firmware entry packages for master/Dwarf/ModularBed/xBuddy Extension, shared protocol/domain crates, explicit resource packaging for embedded auxiliary firmware blobs. |
| Future boards/printers | Add platform constraints and typed profile constructors first; only then add adapters or domain capabilities. New products should not require broad edits to unrelated crates. |

### Scaling Priorities

1. **First bottleneck: build matrix explosion.** Solve with product macros, platform constraints, and generated profile crates. Avoid copying `BUILD.bazel` targets per printer when a validated macro can express the invariant.
1. **Second bottleneck: parity data volume.** Keep fixtures structured and scoped. Use golden summaries for large outputs and full byte diffs only where release compatibility requires them.
1. **Third bottleneck: FFI sprawl.** Enforce private visibility for `foreign/*`, require adapter facades, and track unsafe blocks. Unsafe should be rare, named, and reviewable.
1. **Fourth bottleneck: generated asset churn.** Make codegen deterministic and build-owned; use drift tests for any tracked snapshots.

## Anti-Patterns

### Anti-Pattern 1: Recreating the Global `firmware` Target

**What people do:** Build one giant Bazel target with global include paths, global cfg flags, and a wide dependency list.

**Why it is wrong:** It recreates the current global target coupling and makes ownership invisible.

**Do this instead:** Use packages for domain, adapters, foreign code, generated assets, firmware entrypoints, and parity tests. Default to private visibility and expose only intentional facade targets.

### Anti-Pattern 2: `cfg` and `select()` Throughout Domain Logic

**What people do:** Replace C preprocessor macros with Rust `#[cfg]` branches in every domain module.

**Why it is wrong:** It hides the product model, makes host tests incomplete, and lets invalid combinations survive until a rarely built product fails.

**Do this instead:** Select products in Bazel, generate/construct `ProductProfile`, and pass typed capabilities to pure domain functions.

### Anti-Pattern 3: Foreign Calls from Everywhere

**What people do:** Let domain/application crates call HAL, FreeRTOS, mbedTLS, LwIP, or generated bindgen APIs directly.

**Why it is wrong:** It spreads unsafe assumptions, lifetime requirements, interrupt rules, and scheduler constraints through the codebase.

**Do this instead:** Keep foreign APIs in `foreign/*` and `crates/adapters/*`; expose safe, narrow Rust traits and facades to application/domain crates.

### Anti-Pattern 4: Treating Marlin as a Hidden Runtime Dependency

**What people do:** Keep Marlin linked into production firmware while calling the project a Rust rewrite.

**Why it is wrong:** It preserves the hardest behavior inside the old runtime and weakens the Big Bang replacement goal.

**Do this instead:** Use Marlin/current firmware as reference oracle and simulator comparison. Any temporary production bridge must be explicit, C ABI based, phase-bounded, and tracked as retained foreign code.

### Anti-Pattern 5: Manual Generated Asset Regeneration

**What people do:** Keep committing generated font/resource/translation/header changes without a single authoritative check.

**Why it is wrong:** Generated drift is already a known concern and will get worse under a product matrix.

**Do this instead:** Move generation into Bazel rules and make drift/parity checks test targets.

### Anti-Pattern 6: Mock-Heavy Tests That Miss Reference Behavior

**What people do:** Test Rust internals against new assumptions without comparing to existing firmware behavior.

**Why it is wrong:** Behavior parity is the project constraint. Clean Rust that behaves differently is a regression unless deliberately approved.

**Do this instead:** Unit test the pure core and feed it parity fixtures extracted from the reference firmware, simulator, generated assets, and current tests.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Prusa Connect | Pure protocol crate plus `connect_controller`; transport through `net_lwip` and `tls_mbedtls`. | Preserve registration, token/fingerprint headers, telemetry/events, WebSocket command behavior, proxy/TLS policy, and custom CA behavior with tests. |
| PrusaLink/WUI | Request parser/router boundary plus UI/API controller projections. | Local auth, API compatibility, file operations, and OctoPrint-compatible routes need parity harnesses. |
| HTTP download sources | `transfer_controller` over protocol parser, transport adapter, and storage adapter. | Range requests, encrypted payloads, proxy behavior, partial-file semantics, and media race behavior need explicit tests. |
| SNTP/DNS/mDNS/syslog/metrics | Network adapter plus diagnostic/domain models. | Keep metrics/log formatting pure where possible; socket emission is an adapter. |
| USB/removable storage | FatFs adapter over transfer/storage domain. | Direct-sector behavior and unplug/replug races need hardware-like parity tests. |
| Auxiliary boards | `puppies_protocol` plus bus adapter. | Dwarf, ModularBed, xBuddy Extension bootstrap and runtime state should be typed and shared between master and auxiliary firmware where appropriate. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Bazel product matrix to Rust firmware | Generated profile crate or generated data file consumed by firmware entrypoint. | Build flags stop at profile construction. |
| Domain to application | Rust types, action enums, state transition results. | No HAL/RTOS/network imports. |
| Application to RTOS | Adapter traits and typed task/event APIs. | FreeRTOS handles stay private. |
| Application to HAL | Adapter traits for hardware capabilities. | Board-specific setup belongs in firmware/adapters, not domain code. |
| Application to network/TLS | Protocol commands and transport traits. | mbedTLS/LwIP contexts stay private. |
| Application to UI | UI model/view data/events. | Renderer owns pixels and buffers; domain owns workflow. |
| Storage schema to filesystem | Typed migrations and storage commands. | Persistent IDs and deprecated items need generated drift checks and tests. |
| Rust to retained C/C++/ASM | C ABI shims, manual externs, bindgen allowlists. | Safe wrappers are mandatory; visibility prevents direct use. |
| Rust firmware to C/C++ reference | Parity fixtures, simulator comparison, artifact diffs. | Reference is an oracle, not production architecture. |

## Roadmap Implications

1. **Bazel skeleton and toolchains first.** Establish `MODULE.bazel`, platforms, toolchains, product macros, generated profile crate, minimal firmware link for one master board and one auxiliary MCU family, and `justfile` wrappers.
1. **Domain core before broad adapters.** Model printer/board capabilities, G-code/Connect/transfer/config/UI/puppy state machines with host tests and reference fixtures before hardware integration fans out.
1. **Foreign inventory and adapter facades early.** Catalog retained C/ASM/vendor code, wrap it in Bazel packages, and expose only safe adapter APIs before application code depends on it.
1. **Generated assets under Bazel before UI/resources grow.** Move option/resource/translation/font/package generation into declared rules and parity checks before replacing large GUI/resource surfaces.
1. **Parity harness is continuous.** Every phase should add or extend parity tests. Big Bang does not mean waiting until the end to compare behavior.
1. **Hardware and simulator validation gate cutover.** Release replacement requires host tests, generated/artifact parity, simulator parity, and board smoke evidence for the supported product matrix.

## Research Flags

- Exact Rust target triples and linker strategy for STM32H503/xBuddy Extension need a toolchain spike.
- Decide whether `cortex-m-rt` is useful for any firmware personality or whether existing startup/linker scripts should remain fully custom.
- Decide whether Cargo manifests are hand-maintained for IDE support or generated/checked from Bazel. Bazel must remain authoritative.
- Define the retention contract for Marlin: reference-only is recommended; any runtime bridge requires explicit approval and a sunset plan.
- Build a generated-file ownership map before moving translations/fonts/resources to Bazel to avoid accidentally changing release packaging.

## Sources

### Local Project Evidence

- `.planning/PROJECT.md` - project decisions: Big Bang migration, behavior parity, Bazel primary now, retained foreign code must be explicit.
- `.planning/codebase/ARCHITECTURE.md` - current CMake-composed firmware, FreeRTOS shell, Marlin server/client bridge, GUI, Connect/WUI, persistent stores, resources, puppy firmware, entrypoints, generated options.
- `.planning/codebase/STRUCTURE.md` - current source/build/test/resource directory ownership and naming patterns.
- `.planning/codebase/INTEGRATIONS.md` - Connect, PrusaLink/WUI, downloads, TLS, storage, CI/deployment, secrets, metrics, and hardware integrations.
- `.planning/codebase/CONCERNS.md` - global target coupling, generated asset drift, stale Connect tests, TLS DER bug, probe math coupling, GUI freeze paths, transfer fragility, MMU state gaps, and test gaps.
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` - local workflow and Bright Builds standards routing. No active local overrides were found.

### Standards and Official/Primary References

- Bright Builds architecture standard, pinned commit `05f8d7a6c9c2e157ec4f922a05273e72dab97676`: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md
- Bright Builds Rust standard, pinned commit `05f8d7a6c9c2e157ec4f922a05273e72dab97676`: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md
- Bazel repositories, workspaces, packages, and targets: https://bazel.build/concepts/build-ref
- Bazel labels: https://bazel.build/concepts/labels
- Bazel visibility: https://bazel.build/concepts/visibility
- Bazel platforms and constraints: https://bazel.build/extending/platforms
- Bazel platforms and toolchains rules: https://bazel.build/reference/be/platforms-and-toolchains
- Bazel C/C++ rules: https://bazel.build/reference/be/c-cpp
- Bazel genrule reference: https://bazel.build/reference/be/general#genrule
- rules_rust introduction and Bzlmod setup: https://bazelbuild.github.io/rules_rust/
- rules_rust Rust rules: https://bazelbuild.github.io/rules_rust/rust.html
- rules_rust Crate Universe with Bzlmod: https://bazelbuild.github.io/rules_rust/crate_universe_bzlmod.html
- rules_rust repositories and target triples: https://bazelbuild.github.io/rules_rust/rust_repositories.html
- rules_rust Rust toolchains: https://bazelbuild.github.io/rules_rust/rust_toolchains.html
- rules_rust bindgen rules: https://bazelbuild.github.io/rules_rust/rust_bindgen.html
- Rust Embedded Book `no_std`: https://docs.rust-embedded.org/book/intro/no-std.html
- Rustonomicon FFI: https://doc.rust-lang.org/nomicon/ffi.html
- Rust Reference external blocks: https://doc.rust-lang.org/reference/items/external-blocks.html
- bindgen user guide: https://rust-lang.github.io/rust-bindgen/
- embedded-hal 1.0 docs: https://docs.rs/embedded-hal/latest/embedded_hal/
- embedded-io docs: https://docs.rs/embedded-io/latest/embedded_io/
- cortex-m-rt docs: https://docs.rs/cortex-m-rt/latest/cortex_m_rt/
- heapless docs: https://docs.rs/heapless/latest/heapless/

______________________________________________________________________

*Architecture research for: behavior-parity Rust+Bazel embedded firmware rewrite*
*Researched: 2026-06-02*
