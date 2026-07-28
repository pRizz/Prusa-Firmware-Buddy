---
phase: 40-file-length-refactoring
plan: 14
subsystem: marlin-server-lifecycle
tags: [marlin, print, media, safety, state-machine, file-length]
requires:
  - phase: 40-file-length-refactoring
    provides: ordered production refactors through Plan 40-13 with one temporary exception remaining
provides:
  - sub-629 Marlin server facade and six cohesive private domain implementations
  - supported-product boot and no-boot build evidence for request, event, print, media, and safety behavior
  - terminal file-length policy with 841 permanent exceptions and no temporary entries
affects: [phase-40-verification, marlin-server, print-lifecycle, firmware-builds]
tech-stack:
  added: []
  patterns: [stable public facade with private domain contracts, concept-oriented state-machine split]
key-files:
  created:
    - src/common/marlin_server_internal.hpp
    - src/common/marlin_server_lifecycle.cpp
    - src/common/marlin_server_events.cpp
    - src/common/marlin_server_requests.cpp
    - src/common/marlin_server_media.cpp
    - src/common/marlin_server_print.cpp
    - src/common/marlin_server_safety.cpp
  modified:
    - src/common/marlin_server.cpp
    - src/common/CMakeLists.txt
    - .bright-builds-rules-checks.tsv
    - tools/bazel/phase40_file_length_policy_test.py
key-decisions:
  - "Keep marlin_server.cpp and all public headers as stable facades while private concept modules own lifecycle, request, event, media, print, and safety state knowledge."
  - "Use synthetic paths from the immutable original temporary set for shrink-only policy tests so the terminal zero-temporary ledger remains testable without weakening production policy."
patterns-established:
  - "Marlin server domains share only a private internal contract; public symbols and effect-bearing adapters remain at their established boundaries."
  - "Terminal ratchet tests construct historical temporary inputs instead of assuming active technical debt remains."
requirements-completed: [D-05, D-07, D-08, D-09, D-11, D-12, D-14, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-28T02:23:42Z
duration: 40min
completed: 2026-07-27
---

# Phase 40 Plan 14: Marlin Server Lifecycle Summary

**The 3,651-line Marlin server is now a 266-line stable facade over six sub-629 lifecycle domains, with all temporary file-length exceptions eliminated**

## Performance

- **Duration:** 40 min
- **Started:** 2026-07-28T01:43:44Z
- **Completed:** 2026-07-28T02:23:42Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments

- Split Marlin server lifecycle, event publication, request dispatch, media recovery, print transitions, and safety recovery into cohesive private sources while retaining the existing public facade and headers.
- Preserved the exact request and event case ordering, all 90 print-state cases, one-slot request queue semantics, task ownership, persistence effects, and fatal/safety ordering across the supported-product build matrix.
- Removed the final temporary ledger row and reached the terminal policy state: 841 documented permanent exceptions, three approved owned exceptions, zero temporary entries, and zero Bright Builds findings.

## Task Commits

Each task was committed atomically:

1. **Task 1: Characterize and extract Marlin server lifecycle, requests, and events** - `70b2ccff0`
2. **Task 2: Extract print, media, and safety policy and remove the final temporary row** - `7b8d4d754`

## Files Created/Modified

- `src/common/marlin_server.cpp` - Stable public facade reduced from 3,651 to 266 lines.
- `src/common/marlin_server_internal.hpp` - Private shared state and domain contracts; 292 lines.
- `src/common/marlin_server_lifecycle.cpp` - Initialization, task loop, settings, completion, and ExtUI lifecycle; 583 lines.
- `src/common/marlin_server_events.cpp` - Event masks, client delivery, warnings, FSM responses, and fan checks; 529 lines.
- `src/common/marlin_server_requests.cpp` - One-slot queue processing, variable updates, request dispatch, and acknowledgement ordering; 434 lines.
- `src/common/marlin_server_media.cpp` - Print start, prefetch, media retry, SFN, and recovery behavior; 403 lines.
- `src/common/marlin_server_print.cpp` - Preview, start, pause, resume, and finish state transitions; 614 lines.
- `src/common/marlin_server_safety.cpp` - Pause effects, crash recovery, power-panic recovery, axis checks, and safety polling; 563 lines.
- `src/common/CMakeLists.txt` - Links all six domain implementations into master-board and XL development firmware targets.
- `.bright-builds-rules-checks.tsv` - Removes the final temporary exception.
- `tools/bazel/phase40_file_length_policy_test.py` - Exercises nonterminal shrinkage with synthetic historical entries so zero-temporary terminal policy remains valid.

## Decisions Made

- Kept every public header byte-identical and confined new cross-module knowledge to `marlin_server_internal.hpp`; no new public symbols or protocol surfaces were introduced.
- Preserved the original state-handler ordering in the facade dispatcher and kept filesystem, Marlin, GUI, persistence, HAL, and fatal effects in the same call paths.
- Used an original-temporary synthetic fixture in policy tests because terminal policy must remain independently testable after the active temporary set reaches zero.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Made shrink-only policy tests valid at the terminal zero-temporary state**

- **Found during:** Task 2 final `just phase40-verify`
- **Issue:** Two policy tests indexed or selected from the active temporary set and crashed after the plan correctly removed its final entry.
- **Fix:** Added a test-only helper that selects an unused path from `ORIGINAL_TEMPORARY_PATHS`, then constructs synthetic nonterminal inputs for shrinkage and unauthorized-conversion assertions.
- **Files modified:** `tools/bazel/phase40_file_length_policy_test.py`
- **Verification:** All 14 policy tests pass; shrink-only and terminal CLI modes both pass with `permanent=841 temporary=0 owned_permanent=3 total=841`.
- **Committed in:** `7b8d4d754`

**Total deviations:** 1 auto-fixed bug.
**Impact on plan:** The fix is test-only, preserves frozen and locked exact sets, and is required to verify the planned terminal state.

## Issues Encountered

- The initial COREONE link found a duplicate `serial_print_start` extraction and an internal-namespace mismatch for the MMU unload helper. Both extraction-boundary defects were corrected before the first task commit.
- MK4 and MK3.5 exposed an `AXIS_MEASURE` helper shared by resume and crash-recovery domains. Its enum and function declaration moved into the private internal contract; both products then linked successfully.
- The direct host CMake test command is blocked locally by pre-existing macOS host-toolchain incompatibilities: `__GNUC_PREREQ` is unavailable and Apple `ld` rejects `--gc-sections`.

## Verification

- Public contract hashes remained exact:
  - `marlin_server.hpp`: `1683b2833f37b0b281abab0b8354fa8acfb65248635cfdf6ca433a71063abe1e`
  - `marlin_server_request.hpp`: `f99300f2044b64a7ac3c75ef46d8b49166492651da04d3aa93f05fee6151b998`
  - `marlin_client_queue.hpp`: `63610d1ca3a7716c413191aa8a7112e3ebe83b018abf5ec9fc3777e1c9e75f31`
- Source characterization found exact request-case order, exact event-case order, and equal before/after multisets for all 90 `State` cases, seven `Event` cases, and 12 `Request::Type` cases.
- Release boot and no-boot builds compiled, linked, and packaged for COREONE, MINI, MK4, MK3.5, iX, and XL; XL also exercised Dwarf and Modular Bed auxiliary builds.
- `just generated-check` passed.
- `just phase40-verify` passed all 14 tests, the shrink-only policy, and Bright Builds aggregate. `bun scripts/bright-builds-check.ts all` reports `findings=0`.
- The file-length policy passes in both shrink-only and terminal modes with exactly 841 permanent entries, zero temporary entries, and three approved owned exceptions.
- The required Rust sequence passed before both task commits: `cargo fmt --all`, Clippy with warnings denied, all-target/all-feature build, and all-feature tests.
- `just test` passed its Bazel reference-contract target. The printed direct host command was executed and reached compilation before the documented macOS compiler/linker incompatibilities.
- `just phase6-verify` passed its 11-test behavior suite, then its aggregate target failed because historical Phase 6 context, research, and validation documents are archived while Bazel runfiles still name their former active paths.
- Simulator integration was executed with `build/mk4_release_noboot/firmware.bin` and `.dependencies/mini404-0.9.10/qemu-system-buddy`. Pytest collected 28 tests, skipped six, and reported 22 setup errors because Mini404 is dynamically linked to missing `/usr/local/opt/dtc/lib/libfdt.1.dylib`; no simulator parity claim is made.
- Hardware-aware review found no change to public headers, HAL calls, persistence schemas, filesystem paths, protocol ordering, fatal paths, or release packaging. Physical hardware was unavailable, and no behavior change requiring a hardware claim was introduced.
- The bundled `clang-format` hook could not start because its executable expects missing `/usr/local/opt/zstd/lib/libzstd.1.dylib`; changed C++ sources were formatted with the installed Homebrew LLVM `clang-format`, CMake formatting passed, and `git diff --check` passed.

## Known Stubs

No stubs were introduced. Existing TODO and FIXME comments were moved unchanged with their owning behavior.

## Threat Surface

No new network endpoint, authentication path, file-access boundary, persistence schema, hardware trust boundary, or externally visible protocol surface was introduced.

## Next Phase Readiness

- Plan 40-15 can perform terminal phase verification against a stable ledger with no temporary exceptions.
- The final supported-product build matrix is green; only environment-owned host, simulator, and archived-document wiring limitations remain documented.

## Self-Check: PASSED

- All seven extracted private implementation/header files and this summary exist.
- Task commits `70b2ccff0` and `7b8d4d754` exist in repository history.
- The terminal policy reports 841 permanent entries, zero temporary entries, and three approved owned exceptions.
- The facade, private header, and all six implementation sources are below 629 lines.
