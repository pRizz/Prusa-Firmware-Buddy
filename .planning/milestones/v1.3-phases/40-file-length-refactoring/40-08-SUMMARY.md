---
phase: 40-file-length-refactoring
plan: 08
subsystem: firmware-characterization-tests
tags: [catch2, cmake, gcode, gui, mmu2, nhttp, media-prefetch, eeprom]
requires:
  - phase: 40-07
    provides: Stable Phase 31-38 evidence façades and a passing Phase 40 file-length policy
provides:
  - Fourteen sub-629-line characterization sources covering seven existing Catch targets
  - Identical discovered case inventories for G-code, GUI, MMU, HTTP, media, and EEPROM suites
  - All seven firmware-test temporary file-length exceptions retired
affects: [firmware-tests, parser-ui-protocol-wui, network-media, persistent-storage]
tech-stack:
  added: []
  patterns:
    - behavior-domain test source split within an existing Catch executable
    - before-and-after discovered-case inventory comparison
    - shared or duplicated test-only fixtures with unchanged assertions
key-files:
  created:
    - tests/unit/common/gcode/reader/gcode_reader_binary_tests.cpp
    - tests/unit/gui/rectangle_geometry_tests.cpp
    - tests/unit/gui/window/tests_layout_visibility.cpp
    - tests/unit/lib/Marlin/MMU2/mmu2_protocol_error_test.cpp
    - tests/unit/lib/WUI/nhttp/server_error_tests.cpp
    - tests/unit/media_prefetch/media_prefetch_error_tests.cpp
    - tests/unit/persistent_stores/EEPROM_journal_recovery_test.cpp
  modified:
    - .bright-builds-rules-checks.tsv
    - tests/unit/common/gcode/reader/CMakeLists.txt
    - tests/unit/gui/CMakeLists.txt
    - tests/unit/gui/window/CMakeLists.txt
    - tests/unit/lib/Marlin/MMU2/CMakeLists.txt
    - tests/unit/lib/WUI/nhttp/CMakeLists.txt
    - tests/unit/media_prefetch/CMakeLists.txt
    - tests/unit/persistent_stores/CMakeLists.txt
key-decisions:
  - "Each extracted characterization source remains in its original Catch executable so target names, fixtures, and host-test routing stay stable."
  - "Discovered case parity is proven by sorting and comparing complete Catch --list-tests output, while source order may change across translation units."
  - "HTTP digest error coverage explicitly resets the mocked clock to its asserted zero-time precondition so the moved case is independent of prior test order."
patterns-established:
  - "Split oversized characterization suites by behavior or failure domain and retire ledger rows only after exact target-level parity and execution."
requirements-completed: [D-05, D-08, D-09, D-11, D-12, D-14, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T21:51:09Z
duration: 27m
completed: 2026-07-27
---

# Phase 40 Plan 08: Firmware Characterization Test Refactoring Summary

Seven oversized firmware characterization suites now comprise fourteen sub-629-line sources while retaining all 120 discovered Catch cases in the same seven executables.

## Performance

- **Duration:** 27 minutes
- **Started:** 2026-07-27T21:24:07Z
- **Completed:** 2026-07-27T21:51:09Z
- **Tasks:** 3
- **Files modified:** 22

## Accomplishments

- Split G-code binary reading, rectangle geometry, layout visibility, MMU protocol failures, HTTP digest failures, media file-handle recovery, and EEPROM migration/recovery into focused companion sources.
- Preserved complete discovered inventories of 19, 20, 9, 34, 18, 9, and 11 cases in the existing targets, for 120 cases total.
- Executed every owning binary successfully after the final split, including more than 66 million assertions across the seven targets.
- Reduced every original and new source below 629 physical lines; the largest is 602 lines.
- Removed all seven `campaign=firmware-tests` ledger exceptions. Phase 40 policy now reports 838 permanent, 34 temporary, 872 total exceptions, and zero findings.

## Task Commits

1. **Task 1: Split G-code and GUI characterization suites** - `391a41a22`
2. **Task 2: Split protocol and HTTP characterization suites** - `63451cd6c`
3. **Task 3: Split media and journal characterization suites** - `73d2c8972`

## Files Created/Modified

- `tests/unit/common/gcode/reader/gcode_reader_binary_tests.cpp` - binary-reader, stream, validity, CRC, and estimate characterization cases.
- `tests/unit/gui/rectangle_geometry_tests.cpp` - rectangle geometry, alignment, padding, merging, containment, and subrectangle cases.
- `tests/unit/gui/window/tests_layout_visibility.cpp` - layout visibility, registration, and capture behavior.
- `tests/unit/lib/Marlin/MMU2/mmu2_protocol_error_test.cpp` - timeout, malformed protocol, rejected command, version mismatch, and corrupt initialization cases.
- `tests/unit/lib/WUI/nhttp/server_error_tests.cpp` - digest authentication error, stale nonce, and unsafe-method connection-close cases.
- `tests/unit/media_prefetch/media_prefetch_error_tests.cpp` - file exhaustion, USB error recovery, and stop/close behavior.
- `tests/unit/persistent_stores/EEPROM_journal_recovery_test.cpp` - bank migration, item migration, and missing-end-item regression coverage.
- Owning `CMakeLists.txt` files - register each companion source in the existing executable and include the EEPROM recovery source in journal-hash generation.
- `.bright-builds-rules-checks.tsv` - removes the seven completed firmware-test exceptions.

## Decisions Made

- Kept all existing Catch executable and CTest identities; no new executable or test registration surface was introduced.
- Compared full sorted `--list-tests` output instead of count-only evidence, proving names, tags, and multiplicity remained exact.
- Kept the EEPROM recovery source in the existing journal-hash generator input set because its moved store configurations still require generated hash coverage.
- Made duplicated test helpers translation-unit-local or inline where required to retain fixture behavior without duplicate linker symbols.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Closed the extracted G-code translation unit**

- **Found during:** Task 1
- **Issue:** The first mechanical split omitted the anonymous-namespace closing brace from the new binary-reader source.
- **Fix:** Restored the namespace boundary and reformatted the extracted source.
- **Files modified:** `tests/unit/common/gcode/reader/gcode_reader_binary_tests.cpp`
- **Verification:** `gcode_reader_test` built and passed all 19 cases with an identical discovered inventory.
- **Committed in:** `391a41a22`

**2. [Rule 1 - Bug] Removed HTTP digest test order dependence**

- **Found during:** Task 2
- **Issue:** Moving digest failures exposed that `Not authenticated digest error close` inherited the stale mocked clock from a prior case despite asserting a zero-time nonce.
- **Fix:** Explicitly initialized the mocked clock to zero in that case's setup without changing its name, tags, sections, or assertions.
- **Files modified:** `tests/unit/lib/WUI/nhttp/server_error_tests.cpp`
- **Verification:** `nhttp_tests` passed all 18 cases and 432 assertions with an identical discovered inventory.
- **Committed in:** `63451cd6c`

**3. [Rule 3 - Blocking] Localized duplicated media and EEPROM helpers**

- **Found during:** Task 3
- **Issue:** Test helper definitions copied into companion translation units initially produced duplicate linker symbols.
- **Fix:** Made the media reader helper translation-unit-local and the shared EEPROM reinitializer inline in both test sources.
- **Files modified:** `tests/unit/media_prefetch/media_prefetch_tests.cpp`, `tests/unit/media_prefetch/media_prefetch_error_tests.cpp`, `tests/unit/persistent_stores/EEPROM_journal_test.cpp`, `tests/unit/persistent_stores/EEPROM_journal_recovery_test.cpp`
- **Verification:** Both executables linked; media passed 9 cases and EEPROM passed 11 cases with identical discovered inventories.
- **Committed in:** `73d2c8972`

**Total deviations:** 3 auto-fixed (1 bug, 2 blocking)
**Impact on plan:** The fixes were limited to test isolation and translation-unit correctness required by the planned splits; production firmware behavior and public test identities did not change.

## Issues Encountered

- The repository-managed clang-format binary was unavailable. The four C++ groups were formatted with Homebrew LLVM 22, while the pre-commit clang-format hook was skipped explicitly; all other applicable hooks passed.
- The native Apple linker rejects the repository's GNU `--gc-sections` option, AppleClang did not expose the expected host declarations, and macOS lacks glibc's `__GNUC_PREREQ`. Narrow temporary build-only portability edits and existing `build-tests` flags allowed the required host reference command to execute; every temporary source edit was restored before staging.
- The executed host CTest command built all targets and ran all 419 tests. It consistently reported 409 passing and 10 unrelated GCC/macOS portability failures: eight integer `from_chars_light` variants, `string_view_utf8::string_build`, and `Round fixed`. Every plan-owned target passed.
- Bazel refreshed `MODULE.bazel.lock` from format version 26 to 28 during verification. That unrelated drift was restored before every task and metadata commit.

## User Setup Required

None - no external service configuration required.

## Known Stubs

- `tests/unit/lib/WUI/nhttp/server_tests.cpp:523` retains the pre-existing list of future HTTP test ideas.
- `tests/unit/lib/Marlin/MMU2/mmu2_protocol_logic_test.cpp:350` and `:387` retain pre-existing MMU test TODO comments. These are coverage notes in otherwise executing tests, not unwired fixtures or empty data sources.

## Residual Risks

- The full host reference suite still has 10 pre-existing GCC/macOS portability failures outside these seven characterization suites; Linux/CI behavior was not changed by this plan.
- The test-only split does not itself validate firmware on hardware or a simulator. Those non-local safety claims remain outside this characterization refactor.

## Verification

- Complete before/after Catch inventory comparison: 19 G-code, 20 rectangle, 9 layout, 34 MMU, 18 HTTP, 9 media, and 11 EEPROM cases; all full sorted listings matched.
- Exact owning binaries: all seven passed after the final commit, including 57,292,653 G-code assertions, 786 rectangle assertions, 1,613,139 layout assertions, 364,011 MMU assertions, 432 HTTP assertions, over 7.35 million media assertions, and 10,407 EEPROM assertions.
- `BUDDY_BAZEL_EXECUTE_REFERENCE=1 just test` executed the underlying CMake, Make, and CTest host command; 409/419 passed with only the 10 documented unrelated portability failures.
- Required ordered Rust checks before each implementation commit: `cargo fmt --all`; `cargo clippy --all-targets --all-features -- -D warnings`; `cargo build --all-targets --all-features`; `cargo test --all-features` - passed.
- `just phase40-verify` and standalone `bun scripts/bright-builds-check.ts all` - passed with zero findings.
- Physical-line scan - all fourteen original/new sources range from 101 to 602 lines.
- Ledger scan - all seven firmware-test rows are absent.
- Applicable pre-commit hooks and `git diff --check` - passed.

## Self-Check: PASSED

- All seven companion sources exist.
- Task commits `391a41a22`, `63451cd6c`, and `73d2c8972` exist in repository history.
- All seven planned ledger rows are absent, every source is below 629 lines, and every exact target passes with identical discovered cases.
