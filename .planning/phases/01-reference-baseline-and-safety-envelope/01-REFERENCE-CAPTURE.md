# Phase 1 Reference Capture Catalog

## Requirement Coverage

- **BASE-02:** Maintainer can run reference-capture targets that preserve existing C/C++ firmware behavior fixtures for builds, generated assets, protocol traces, simulator flows, persistent config migrations, and release artifacts.

## Evidence Classes

| Evidence Class | Meaning |
|----------------|---------|
| `local-smoke` | Reasonable to run locally after bootstrap on a developer workstation. |
| `ci-only` | Expected to run in Jenkins/Holly or another CI environment because it is expensive or matrix-wide. |
| `simulator-flow` | Requires Mini404/QEMU simulator or integration-test harness. |
| `hardware-smoke` | Requires physical printer hardware or board-specific setup. |
| `manual-hardware-required` | Requires human-controlled hardware/failure-injection evidence. |
| `reference-contract` | Captures command/input/output contract without executing every heavy case in Phase 1. |

## Capture Catalog

| Capture | Command Or Procedure | Inputs | Outputs | Evidence | Requirement |
|---------|----------------------|--------|---------|----------|-------------|
| CMake preset generation | `python3 utils/build.py --generate-cmake-presets` | `utils/presets/presets.json`, `utils/build.py` | `CMakePresets.json` | `local-smoke` | BASE-02 |
| Full product firmware build | `python3 utils/build.py` with selected supported preset | `ProjectOptions.cmake`, `CMakePresets.json`, source tree | `build/products/` firmware products | `reference-contract` | BASE-02 |
| Jenkins/Holly firmware matrix | `utils/holly/build-pr.jenkins` pipeline | CI image, bootstrap dependencies, build presets | CI build logs and archived artifacts | `ci-only` | BASE-02 |
| DFU packaging | `python3 utils/build.py --generate-dfu` | Built firmware, `utils/dfu.py` | `.dfu` files under product output | `ci-only` | BASE-02 |
| BBF packaging | CMake/package target using `utils/pack_fw.py` | Built binary, signing key path, metadata | `.bbf` package | `reference-contract` | BASE-02 |
| LittleFS/resource packaging | CMake resource image target via `cmake/Littlefs.cmake` | `src/resources/`, `utils/mklittlefs.py` | LittleFS/resource image | `reference-contract` | BASE-02 |
| Logging component overview | pre-commit hook or `utils/logging/generate_overview.py` | logging component definitions | `doc/logging_components.md` | `local-smoke` | BASE-02 |
| Translation POT generation | `utils/translations_and_fonts/generate_pot.sh` | source strings and translation tooling | `src/lang/po/Prusa-Firmware-Buddy.pot` | `reference-contract` | BASE-02 |
| Font/resource generation | `utils/translations_and_fonts/generate_all_fonts.sh` | translation/font assets | `src/gui/res/cc/*.hpp`, `src/guiapi/include/*.ipp` | `reference-contract` | BASE-02 |
| Host C++ unit tests | native CMake build, `ninja tests`, `ctest .` | `tests/unit/`, Catch2, stubs | CTest output | `local-smoke` | BASE-02 |
| Simulator integration tests | `pytest tests/integration --firmware <firmware.bin>` | firmware binary, simulator dependencies | pytest logs and protocol traces | `simulator-flow` | BASE-02 |
| Block-device tests | `pytest tests/blockdevice --device <block-device-path>` | physical or simulated block device | pytest logs | `manual-hardware-required` | BASE-02 |
| Connect/WUI protocol traces | simulator or hardware run of PrusaLink/Connect flows | `src/connect/`, `lib/WUI/`, network config | HTTP/WebSocket trace log | `simulator-flow` | BASE-02 |
| Persistent-store migration fixtures | host/unit tests for config store and generated hashes | `src/persistent_stores/`, migration sources | migration test logs | `local-smoke` | BASE-02 |
| Release artifact metadata capture | archive `.bin`, `.bbf`, `.dfu`, `.map`, resource image metadata | product outputs | checksums, sizes, provenance notes | `ci-only` | BASE-02 |
| Hardware safety smoke | controlled startup/watchdog/motion/thermal/power-panic procedures | supported printer hardware | manual test report | `manual-hardware-required` | BASE-02 |

## Output Ownership

- Build products, logs, traces, and large generated outputs belong under ignored build or evidence directories unless a later plan intentionally commits a small fixture.
- This phase commits the capture catalog, not the full captured firmware matrix.
- Any captured secret-bearing outputs must be redacted before storage. This includes crash dumps, WiFi credentials, PrusaLink passwords, Connect tokens, private signing key paths beyond the configured path string, and custom certificate bytes.

## Deferred Heavy Runs

The following are declared as reference contracts in Phase 1 and should be executed in later phases or CI when the matching subsystem gate is built:

- Full supported product build matrix.
- Full simulator integration suite across product profiles.
- Hardware smoke for startup, watchdog, motion safe state, thermal state, power panic, crash dump, and auxiliary-controller flows.
- Release artifact checksum comparison once Bazel owns artifact generation in Phase 3.
