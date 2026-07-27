---
phase: 40-file-length-refactoring
plan: 09
subsystem: firmware-architecture
tags: [cpp, cmake, wui, gcode, gui, connect, file-length-policy]
requires:
  - phase: 40-file-length-refactoring
    provides: Plan 08 characterization inventories and host-test coverage
provides:
  - Eleven repo-owned firmware implementations split below the 629-line threshold
  - Stable WUI, parser, Connect, GUI, and printer-state interfaces backed by cohesive private modules
  - Two approved owned deep-module ledger classifications with deletion-test evidence
affects: [file-length-policy, firmware-build, host-tests, future-phase-40-campaigns]
tech-stack:
  added: []
  patterns: [stable-facade-private-module, pure-mapping-extraction, atomic-policy-ledger-removal]
key-files:
  created:
    - lib/WUI/espif_internal.hpp
    - lib/WUI/espif_lifecycle.cpp
    - lib/WUI/nhttp/server_dispatch.cpp
    - src/connect/render_json.cpp
    - src/gui/screen_printing_state.cpp
    - src/state/printer_state_mapping.cpp
  modified:
    - .bright-builds-rules-checks.tsv
    - lib/WUI/nhttp/server.cpp
    - src/common/gcode/gcode_reader_binary.cpp
    - src/connect/render.cpp
    - src/gui/MItem_tools.hpp
key-decisions:
  - "Keep public firmware surfaces stable and place extracted behavior in named private implementation modules owned by the existing targets."
  - "Retain the complete tools-menu API in MItem_tools.hpp while moving its coherent odometer/information declaration group to a directly included owned subheader."
  - "Convert only Rect16.h and screen_tools_mapping.cpp to approved owned deep modules, with their source bytes unchanged."
patterns-established:
  - "Effectful façade files retain lifecycle and public entry points; cohesive parsing, rendering, action, or mapping behavior moves to target-local sources."
  - "Temporary ledger rows are removed only after line caps, focused inventories, real firmware links, and policy gates pass."
requirements-completed: [D-03, D-05, D-06, D-07, D-08, D-09, D-11, D-12, D-14, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T23:01:14Z
duration: 1h 6m
completed: 2026-07-27
---

# Phase 40 Plan 09: Parser, UI, Protocol, and WUI Refactoring Summary

**Eleven oversized firmware implementations now use cohesive private C++ modules below the line cap, with two byte-identical central abstractions retained under approved deletion-test evidence.**

## Performance

- **Duration:** 1h 6m
- **Started:** 2026-07-27T21:54:53Z
- **Completed:** 2026-07-27T23:01:14Z
- **Tasks:** 3
- **Files modified:** 36

## Accomplishments

- Split ESP lifecycle, HTTP dispatch, WUI request handling, G-code metadata/binary-block parsing, and probe math while preserving their public symbols and target ownership.
- Split Connect event/telemetry JSON, tools-menu actions/information declarations, printing-screen transitions, and external printer-state mappings without changing public behavior.
- Removed eleven temporary campaign exceptions and converted exactly `Rect16.h` and `screen_tools_mapping.cpp` to approved owned deep-module reasons.
- Preserved focused host inventories exactly and linked/package-tested real COREONE and MINI firmware images.

## Task Commits

Each task was committed atomically:

1. **Task 1: Refactor WUI and parser/probe implementations** - `62d9089c0`
2. **Task 2: Refactor Connect rendering and GUI/state implementations** - `5bb38f268`
3. **Task 3: Convert the two locked deep-module exceptions** - `49de6d3bc`

## Files Created/Modified

- `lib/WUI/espif_internal.hpp`, `lib/WUI/espif_lifecycle.cpp` - Shared private ESP state and lifecycle implementation.
- `lib/WUI/nhttp/server_dispatch.cpp` - HTTP connection-slot and callback dispatch ownership.
- `lib/WUI/wui_request.cpp` - WUI request processing separated from service state.
- `src/common/gcode/gcode_info_metadata.cpp` - Metadata parsing and validity ownership.
- `src/common/gcode/gcode_reader_binary_blocks.cpp` - Binary block traversal and header validation.
- `src/common/probe_analysis_math.cpp` - Pure probe feature calculations.
- `src/connect/render_internal.hpp`, `render_json.cpp`, `render_telemetry.cpp` - Private overload contract with event and telemetry serialization ownership.
- `src/gui/MItem_tools_actions.cpp`, `MItem_tools_info.hpp` - Tool menu actions and cohesive information declarations.
- `src/gui/screen_printing_state.cpp` - Printing button actions and state transitions.
- `src/state/printer_state_mapping.cpp` - Firmware-state and warning-to-external mappings.
- `.bright-builds-rules-checks.tsv` - Eleven temporary rows removed and two approved conversions recorded.

## Decisions Made

- Connect rendering uses one private overload header so `std::visit` retains compile-time coverage while event and telemetry implementations compile independently.
- The tools-menu public surface remains a real abstraction: `MItem_tools.hpp` owns the API and directly composes a cohesive information-declaration subheader rather than becoming an empty forwarding header.
- `Rect16.h` is retained as the single constexpr geometry value abstraction; `screen_tools_mapping.cpp` is retained as the single bidirectional mapping workflow and protocol-state authority.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added direct include and host-target dependency closure**

- **Found during:** Tasks 1 and 2
- **Issue:** Extracted translation units exposed dependencies previously supplied transitively, and a clean host reconfigure omitted the binary-reader split and its string helpers.
- **Fix:** Added direct implementation includes and registered the extracted binary reader, StringBuilder, and UTF-8 reader sources in the owning host target.
- **Files modified:** WUI split sources and `tests/unit/connect/CMakeLists.txt`
- **Verification:** All extracted translation units compiled for COREONE/MINI; focused host binary linked with the known macOS flag removed and executed 45 cases/263 assertions.
- **Committed in:** `62d9089c0`, `5bb38f268`

**2. [Rule 1 - Bug] Kept the shrink-only fixture effective after ledger removal**

- **Found during:** Task 1
- **Issue:** The policy regression test selected a path already removed by the campaign, making its unauthorized-permanence fixture a no-op.
- **Fix:** Select an owned path still present in the active temporary set.
- **Files modified:** `tools/bazel/phase40_file_length_policy_test.py`
- **Verification:** All 14 policy tests pass.
- **Committed in:** `62d9089c0`

**3. [Rule 1 - Bug] Restored internal linkage for duplicated render helpers**

- **Found during:** Task 2 firmware link
- **Issue:** The event and telemetry extractions both defined the same helper with external linkage.
- **Fix:** Made each target-local helper `static`.
- **Files modified:** `src/connect/render_json.cpp`, `src/connect/render_telemetry.cpp`
- **Verification:** COREONE and MINI firmware linked and packaged successfully.
- **Committed in:** `5bb38f268`

**Total deviations:** 3 auto-fixed (2 bugs, 1 blocking dependency closure).

**Impact on plan:** All fixes preserve the planned boundaries and verification coverage; no feature scope was added.

## Verification Evidence

- Focused host inventories remained byte-identical:
  - Connect: 45 cases / 263 assertions
  - GUI: 1 case / 23 assertions
  - GUI time: 1 case / 7 assertions
  - Rectangle: 20 cases / 786 assertions
  - Layout: 9 cases / 1,613,139 assertions
  - nHTTP: 18 cases / 432 assertions
  - Binary reader: 19 cases / 57,292,653 assertions
- Real ARM firmware linked and packaged for COREONE and MINI; Task 1 also audited boot/no-boot and language variants across COREONE, MINI, MK4, and MK4-burst configurations.
- `just phase40-verify` passed with `permanent=840`, `temporary=21`, `owned_permanent=2`, `findings=0`.
- Bright Builds all-check passed.
- Mandatory Rust sequence passed: format, clippy with warnings denied, all-target build, and all-feature tests.
- `BUDDY_BAZEL_EXECUTE_REFERENCE=1 just test` reaches the pre-existing macOS host-linker incompatibility: Apple `ld` rejects GNU `--gc-sections`. Focused binaries were linked without that unsupported platform flag and executed successfully.

## Known Stubs

None introduced. Pre-existing TODO/FIXME comments remain in moved code, but no placeholder or mock data flow was added.

## Issues Encountered

- The repository host-test reference command cannot complete on this macOS environment because its generated link flags contain GNU `--gc-sections`. This is pre-existing and outside the refactoring scope; compilation and focused execution evidence were collected separately.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The parser/UI/protocol/WUI campaign is complete: eleven temporary rows are gone and its two approved owned conversions are documented.
- Twenty-one temporary file-length exceptions remain for other Phase 40 campaigns.
- No implementation blocker remains for the next plan; the macOS host-linker portability issue remains an environment-level verification limitation.

## Self-Check: PASSED

All created files and task commits exist; locked-source hashes match their pre-conversion values.

*Phase: 40-file-length-refactoring*
*Completed: 2026-07-27*
