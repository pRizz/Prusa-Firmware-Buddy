# Phase 1 Safety Envelope

## Requirement Coverage

- **BASE-04:** Maintainer can evaluate a safety envelope covering startup, watchdogs, thermal states, motion safe states, endstops, fans, loadcell/probe behavior, power panic, crash dumps, and emergency/error flows before Rust cutover.

## Evidence Classes

| Evidence Class | Meaning |
|----------------|---------|
| `source-audit` | Verified by source review and traceability to current reference paths. |
| `host-test` | Verified by host unit or integration test without physical hardware. |
| `simulator-flow` | Verified through Mini404/QEMU or equivalent simulator flow. |
| `hardware-smoke` | Verified on supported physical printer or board hardware. |
| `manual-hardware-required` | Requires human-controlled hardware and failure-injection evidence before cutover. |

## Board And Runtime Coverage

| Runtime Surface | Boards Or Products | Current Reference Paths | Evidence |
|-----------------|--------------------|-------------------------|----------|
| Master-board startup and task orchestration | `BUDDY`, `XBUDDY`, `XLBUDDY` | `src/buddy/main.cpp`, `src/common/appmain.cpp`, `lib/Middlewares/Third_Party/FreeRTOS/` | `source-audit`, `simulator-flow`, `hardware-smoke` |
| Auxiliary firmware personalities | `DWARF`, `MODULARBED`, `XBUDDY_EXTENSION`, `XL_DEV_KIT_XLB` | `src/puppy/dwarf/`, `src/puppy/modularbed/`, `src/puppy/xbuddy_extension/`, `src/puppies/` | `source-audit`, `manual-hardware-required` |
| STM32 device startup and interrupts | `STM32F407VG`, `STM32F429VI`, `STM32F427ZI`, `STM32G070RBT6`, `STM32H503CBU7` | `src/device/`, `include/device/`, `src/common/Pin.cpp` | `source-audit`, `hardware-smoke` |
| Persistent safety state and credentials | all supported printers | `src/persistent_stores/store_instances/config_store/store_definition.hpp`, `src/persistent_stores/store_instances/config_store/migrations.cpp` | `source-audit`, `host-test` |

## Safety Flow Matrix

| Flow | Current Reference Paths | Required Evidence | Notes |
|------|-------------------------|-------------------|-------|
| Startup safe state | `src/buddy/main.cpp`, `src/common/appmain.cpp`, `src/device/` | `source-audit`, `simulator-flow`, `hardware-smoke` | Confirm board clocks, task creation, dependency readiness, and outputs before motion/heat enablement. |
| Watchdog behavior | `src/buddy/main.cpp`, board/device runtime sources | `source-audit`, `hardware-smoke` | Preserve watchdog setup and failure response across master and auxiliary firmware. |
| Thermal safe states | `lib/Marlin/`, `src/common/marlin_server.cpp`, printer-specific feature gates | `source-audit`, `simulator-flow`, `manual-hardware-required` | Verify heating, cooldown, fault, and emergency stop behavior before cutover. |
| Motion safe states | `lib/Marlin/`, `src/common/marlin_server.cpp`, `src/marlin_stubs/` | `source-audit`, `simulator-flow`, `manual-hardware-required` | Preserve planner-visible pause/resume/cancel, homing, endstop, and safe-output behavior. |
| Probe and loadcell behavior | `src/common/probe_analysis.cpp`, loadcell/HX717 feature paths | `source-audit`, `host-test`, `manual-hardware-required` | Probe classifier bug CL-007 is preserved temporarily unless thresholds are intentionally updated. |
| Fans and outputs | board pin/config sources, Marlin thermal paths | `source-audit`, `hardware-smoke` | Verify safe defaults and fault behavior on each affected board family. |
| Power panic | power panic runtime paths, `src/common/marlin_server.cpp`, GUI recovery flows | `source-audit`, `simulator-flow`, `manual-hardware-required` | Requires hardware/failure-injection evidence before final cutover. |
| Crash dumps | `src/common/crash_dump/dump.cpp`, `src/common/crash_dump/crash_dump_distribute.cpp`, `src/gui/screen_home.cpp` | `source-audit`, `manual-hardware-required` | Crash dumps may include sensitive memory; upload must remain disabled or protected unless intentionally changed. |
| Emergency stop and fatal errors | `src/common/bsod`, fatal/redscreen paths, `src/gui/`, `tests/unit/mock/bsod.cpp` | `source-audit`, `host-test`, `simulator-flow` | Unit tests can cover fatal handler substitution; final behavior needs simulator/hardware evidence. |
| Transfer/media safe writes | `src/transfers/partial_file.cpp`, `src/transfers/transfer.cpp`, FatFs/littlefs paths | `source-audit`, `host-test`, `manual-hardware-required` | Media race risks must remain visible until Phase 9 transfer parity work. |
| Connect/TLS/network safety | `src/connect/tls/tls.cpp`, `src/connect/`, `src/common/http/`, `include/buddy/lwipopts.h` | `source-audit`, `simulator-flow` | Custom certificate bug CL-006 and legacy digest CL-013 require intentional later treatment. |
| Auxiliary-controller update and fault states | `src/puppies/`, `src/puppy/`, `lib/AddLiblightmodbus.cmake` | `source-audit`, `manual-hardware-required` | Preserve bootloader, unavailable, active, stopped, update, and fault states. |

## Manual Hardware Evidence

The following remain explicit evidence debt until later hardware qualification:

- Startup/watchdog smoke on every supported master-board family.
- Motion and thermal failure injection on representative supported printers.
- Probe/loadcell safe-state behavior on products that expose those features.
- Power panic and crash dump behavior under controlled failure.
- Auxiliary-controller bootloader/update/fault handling for puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, and toolchanger combinations.
- Transfer/media race behavior for removable USB/internal storage scenarios.

## Secret Handling

- Do not copy WiFi passwords, PrusaLink passwords, Connect tokens, private signing keys, custom certificate bytes, or crash dump memory contents into planning artifacts.
- It is acceptable to reference config keys and source paths such as `connect_token`, `connect_custom_tls_cert`, `SIGNING_KEY`, and `/internal/connect/connect.der`.
- Any future captured crash dump, network trace, or firmware artifact must be reviewed for credential-bearing content before being committed.
