---
phase: 40-file-length-refactoring
verified: 2026-07-28T02:57:20Z
status: gaps_found
score: 4/5 roadmap must-haves verified
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-28T02:57:20Z
lifecycle_validated: true
overrides_applied: 0
gaps:
  - truth: "All refactored and newly created source/test files use substantive concept-oriented modules rather than shallow or checker-shaped seams."
    status: partial
    reason: "Twelve new Phase 33-35 Python test modules store 234-525 lines of executable test source in one escaped string physical line, and three public test entrypoints reconstruct the tests with exec(). This passes the physical-line checker but does not implement reviewable behavior/failure-domain test modules or the D-08 deletion-test seam."
    artifacts:
      - path: "tools/bazel/phase33_maintainer_decision_inputs_cases_test.py"
        issue: "One 19,715-byte physical line contains 438 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase33_maintainer_decision_inputs_failure_test.py"
        issue: "One 18,701-byte physical line contains 400 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase33_maintainer_decision_inputs_security_test.py"
        issue: "One 13,351-byte physical line contains 270 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase34_final_readiness_cases_test.py"
        issue: "One 22,825-byte physical line contains 525 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase34_final_readiness_demotion_failure_test.py"
        issue: "One 22,469-byte physical line contains 436 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase34_final_readiness_source_failure_test.py"
        issue: "One 16,674-byte physical line contains 419 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase34_publication_state_test.py"
        issue: "One 8,265-byte physical line contains 234 embedded source lines in TEST_CLASSES."
      - path: "tools/bazel/phase35_cutover_decision_cases_test.py"
        issue: "One 20,019-byte physical line contains 506 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase35_cutover_decision_failure_test.py"
        issue: "One 19,405-byte physical line contains 484 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase35_cutover_decision_security_test.py"
        issue: "One 10,384-byte physical line contains 247 embedded source lines in TEST_METHODS."
      - path: "tools/bazel/phase35_guarded_publication_test.py"
        issue: "One 18,393-byte physical line contains 431 embedded source lines in TEST_CLASSES."
      - path: "tools/bazel/phase35_source_failure_replacement_test.py"
        issue: "One 14,151-byte physical line contains 317 embedded source lines in TEST_CLASSES."
    missing:
      - "Materialize the escaped test methods/classes as ordinary Python test classes or behavior-focused mixins in the existing phase-local modules."
      - "Replace importlib plus exec() assembly in the Phase 33, 34, and 35 public test entrypoints with ordinary imports/inheritance while preserving public Bazel labels and test behavior."
      - "Keep every resulting physical source/test file below 629 lines and rerun the affected Phase 33-35 gates plus terminal verification."
---

# Phase 40: File Length Refactoring Verification Report

**Phase Goal:** The managed file-length checker reports zero findings with exactly 841 authorized permanent paths, while all 92 refactored repo-owned files and every new source/test file are below 629 physical lines and all external interfaces, firmware behavior, persistence, and release artifacts remain compatible.
**Verified:** 2026-07-28T02:57:20Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Roadmap truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | The initial ledger classified all 933 findings as 838 frozen permanent paths plus 95 temporary owned paths without changing the managed checker or CI workflow. | ✓ VERIFIED | Commit `0f495e069` contains the 933-row baseline; the immutable policy sets independently report 838 and 95. `git diff 0f495e069^..HEAD` is empty for `scripts/bright-builds-check.ts` and `.github/workflows/bright-builds-checks.yml`. |
| 2 | All 92 refactored originals and new source/test files are sub-629, compatible, and behind stable concept-oriented façades. | ✗ FAILED (partial) | Exact line reconciliation passes: 92 originals, maximum 628 lines; 179 new files, maximum 623 lines. Cargo, generated checks, public wiring, focused campaign evidence, and supported builds support compatibility. However, twelve Phase 33-35 “test modules” hide 234-525 logical source lines inside single-line strings and are assembled with `exec()`, so the concept-oriented/non-shallow portion of the criterion is not achieved. |
| 3 | Exactly the three approved owned paths convert to permanent deletion-test reasons. | ✓ VERIFIED | Exact-set audit reports only `src/connect/planner.cpp`, `src/gui/screen_tools_mapping.cpp`, and `src/guiapi/include/Rect16.h`; every reason contains a path-specific `deletion-test=` rationale. |
| 4 | Characterization tests split first, print/safety ran last, and `marlin_server.cpp` was the final production refactor. | ✓ VERIFIED | Ledger history reconciles each of the 95 paths exactly once in the planned 4/2/12/8/16/12/7/13/6/2/7/5/1 campaign sequence. Plan 08 commits precede Plans 09-14, and commit `7b8d4d754` removes the final `marlin_server.cpp` row. |
| 5 | Terminal reconciliation reports 841 permanent, zero temporary, zero findings, with risk-tiered evidence and hardware-aware review complete. | ✓ VERIFIED | Fresh terminal execution passed 14 policy tests with `permanent=841 temporary=0 owned_permanent=3 total=841`; standalone Bright Builds reported `exceptions=841 findings=0`. The user approved the hardware-aware checkpoint while explicitly retaining the simulator, physical-hardware, archived-artifact, and macOS-host limitations. |

**Score:** 4/5 roadmap truths verified

### Required Artifacts

The GSD artifact verifier checked all 28 artifact declarations across Plans 40-01 through 40-15: 28 existed, were substantive under the declared checks, and passed. Key evidence includes:

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `.bright-builds-rules-checks.tsv` | Canonical terminal ledger | ✓ VERIFIED | 841 sorted unique rows; reason partition is 800 imported, 35 generated, three declarative, and three owned; zero temporary. |
| `tools/bazel/phase40_file_length_policy.py` | Shrink-only and exact-terminal policy | ✓ VERIFIED | Enforces the frozen 838, original 95, locked three, reason syntax, sorted uniqueness, and exact terminal union. |
| `tools/bazel/phase40_file_length_policy_test.py` | Fail-closed policy regressions | ✓ VERIFIED | Fresh Bazel run: 14/14 tests passed. |
| `doc/file_length_policy.md` | Stable exception and campaign policy | ✓ VERIFIED | Documents permanent/temporary syntax, deletion tests, shrink-only removal, exact terminal state, and executed-evidence requirements. |
| Campaign façades and extracted implementation files | Stable interfaces and concept-local implementations | ⚠️ PARTIAL | All plan-declared artifact paths and build links pass, but the twelve escaped-code test payloads listed in the gap are not substantive ordinary Python modules. |

### Key Link Verification

The GSD key-link verifier checked all 16 declared links across the 15 plans: 16/16 verified.

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `justfile` | Phase 40 policy | `phase40-verify` | ✓ WIRED | Runs policy tests, policy CLI, and managed Bright Builds checks. |
| Phase-local build definitions | Extracted Rust/Python/C++ modules | Existing labels/targets | ✓ WIRED | Every declared pattern was found; the relevant modules are included by their established target. |
| Phase 33-35 public test entrypoints | Escaped test payload modules | `importlib` plus `exec()` | ✗ WIRED BUT SHALLOW | Tests execute, but the connection is dynamic source reconstruction rather than an ordinary module/class interface. |

### Data-Flow Trace (Level 4)

Not applicable. Phase 40 is a structural refactor and policy campaign, not a user-facing dynamic-data rendering phase. Contract flow was instead checked through public labels, target source wiring, exact-set policy, CLI execution, and preserved campaign tests.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Exact terminal policy | `just phase40-verify --terminal` | 14 tests pass; 841 permanent, zero temporary, three owned | ✓ PASS |
| Managed file-length result | `bun scripts/bright-builds-check.ts all` | `SUMMARY file-lengths scanned=7398 exceptions=841 findings=0`; aggregate findings zero | ✓ PASS |
| Rust contract/build behavior | `cargo fmt --all` → Clippy with warnings denied → all-target/all-feature build → all-feature tests | Exact ordered sequence passes; 136 unit tests plus doc tests pass | ✓ PASS |
| Stable build CLI | `python3 utils/build.py --help` | Exit zero; 58-line help emitted | ✓ PASS |
| Generated surfaces | `just generated-check` | All configured generated-surface checks pass | ✓ PASS |
| Diff hygiene | `git diff --check` | Clean before report creation | ✓ PASS |

### Requirements Coverage

Phase 40 is decision-driven and has no new milestone requirement IDs. Plans claim D-01 through D-15 from `40-CONTEXT.md`.

| Requirements | Status | Evidence |
| --- | --- | --- |
| D-01–D-04 | ✓ SATISFIED | Exact baseline/terminal partitions, locked conversions, and managed-file immutability verified. |
| D-05–D-07 | ✓ SATISFIED | Public façades, phase-local implementations, existing labels, and effect adapters are present and wired. |
| D-08 | ✗ BLOCKED | The twelve escaped-code payloads and three `exec()` assemblers are checker-shaped/shallow seams rather than ordinary concept-oriented modules. |
| D-09–D-11 | ✓ SATISFIED | Git/ledger history proves fixed serial order and exact same-campaign row removal/conversion. |
| D-12–D-13 | ✓ SATISFIED | Campaign summaries retain command/delta/contract/risk evidence; fresh exact Cargo sequence passes. |
| D-14–D-15 | ✓ SATISFIED WITH RECORDED LIMITS | Underlying commands and supported builds were executed. Hardware-aware approval was explicit; no simulator or physical-hardware coverage is claimed. |

### Anti-Patterns Found

| File(s) | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| Twelve Phase 33-35 payload modules listed in frontmatter | 1 | Hundreds of logical Python source lines encoded in one `TEST_METHODS`/`TEST_CLASSES` string | 🛑 Blocker | Evades the physical-line signal and prevents ordinary formatting, semantic navigation, diagnostics, and review. |
| `phase33_maintainer_decision_inputs_test.py`, `phase34_final_readiness_demotion_dry_run_test.py`, `phase35_cutover_decision_artifact_test.py` | dynamic loader blocks | `exec()` reconstructs test methods/classes from strings | 🛑 Blocker | Creates a shallow, implicit test seam that fails D-08 despite passing runtime tests. |
| Extracted C++ files | various | Existing TODO/FIXME/null-return paths moved with their owning behavior | ℹ️ Info | No new placeholder was identified; campaign summaries and diffs indicate these are retained behavior, not Phase 40 stubs. |

### Confirmation-Bias Countercheck

- **Partially met requirement:** D-08 passes the numeric line limit but fails the substantive module/deletion-test requirement for the twelve escaped-code files.
- **Misleading green test:** Phase 33-35 tests pass because the entrypoints dynamically execute the strings; those tests do not establish that the extracted files are maintainable Python modules.
- **Uncovered guard:** The Phase 40 policy checks physical lines and exact paths but has no regression that rejects oversized escaped source blobs or dynamic source assembly. This is the mechanism that allowed the structural gap.

### Human Verification and Accepted Evidence Limits

The blocking hardware-aware review has already been approved by the user. That approval is recorded without inflating the evidence:

- Explicit Mini404 attempts collected tests but reached no test bodies because of runtime/profile incompatibilities.
- No physical printer hardware was available, so no physical-hardware coverage is claimed.
- Historical Phase 8-10 aggregate verifiers retain archived/missing-artifact wiring limitations.
- Aggregate macOS host execution retains GNU-linker/runtime incompatibilities; focused host tests and supported ARM product builds are the available evidence.

These accepted environment limitations are not the cause of the implementation gap above.

### Gaps Summary

The ledger, physical line counts, campaign reconciliation, managed-checker result, public wiring, Rust verification, generated checks, ordering, and approved evidence checkpoint all pass. One architectural gap blocks the phase goal: Plan 40-07 converted twelve large Python test regions into single physical-line source strings and dynamically executes them from three public test entrypoints. Materializing those strings as normal phase-local test classes or mixins should preserve behavior while satisfying the intended code-shape and deep-module contract.

***

_Verified: 2026-07-28T02:57:20Z_
_Verifier: the agent (gsd-verifier)_
