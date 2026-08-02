---
phase: 40-file-length-refactoring
plan: 03
subsystem: developer-utilities
tags: [python, click, cmake, plotly, serial, file-lengths]
requires:
  - phase: 40-02
    provides: Stable Rust-domain façades and shrink-aware Phase 40 verification
provides:
  - Stable build CLI façade over configuration, preset, and product-publication modules
  - Pure phase-stepping signal analysis with isolated serial and Plotly adapters
  - Preserved Click commands, public imports, generated presets, and product metadata
  - Two retired developer-utility exceptions with 89 temporary paths remaining
affects: [40-04, developer-workflow, phase-stepping, file-length-verification]
tech-stack:
  added: []
  patterns:
    - stable Python entrypoint façade over cohesive concept modules
    - pure numerical core with serial and Plotly adapters
    - byte-for-byte CLI and generated-output compatibility evidence
key-files:
  created:
    - utils/build_config.py
    - utils/build_presets.py
    - utils/build_products.py
    - utils/phase_stepping/signal_analysis.py
    - utils/phase_stepping/serial_machine.py
    - utils/phase_stepping/plotting.py
  modified:
    - .bright-builds-rules-checks.tsv
    - utils/build.py
    - utils/phase_stepping/phase_stepping.py
    - utils/phase_stepping/test_phase_stepping.py
key-decisions:
  - "Build configuration, preset generation, and artifact publication live behind a stable utils/build.py CLI and import façade."
  - "Phase-stepping numerical transforms remain pure; direct Serial and Plotly imports are confined to their adapters while phase_stepping.py re-exports every original public definition."
  - "CLI help, generated presets, product metadata, invalid-option behavior, and deterministic numerical results are compared byte-for-byte before retiring exceptions."
patterns-established:
  - "Keep executable utility entrypoints thin while preserving direct-script and package-import compatibility."
  - "Capture deterministic pre/post evidence before removing a temporary file-length exception."
requirements-completed: [D-05, D-08, D-09, D-11, D-12, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T19:04:30Z
duration: 20m
completed: 2026-07-27
---

# Phase 40 Plan 03: Developer Utility Refactoring Summary

Stable build and phase-stepping entrypoints now front seven cohesive modules, with byte-identical command contracts, generated data, and deterministic numerical behavior and no developer-utility length exceptions.

## Performance

- **Duration:** 20 minutes
- **Started:** 2026-07-27T18:44:42Z
- **Completed:** 2026-07-27T19:04:30Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Reduced `utils/build.py` from 1,122 lines to a 277-line executable façade over 309-line configuration, 225-line preset, and 32-line product-publication modules.
- Reduced `utils/phase_stepping/phase_stepping.py` from 1,452 lines to a 443-line Click façade over 460-line pure analysis, 163-line serial, and 471-line plotting modules.
- Preserved all 30 original phase-stepping top-level imports, six Click subcommands, root/subcommand help, deterministic phase-current and rolling-energy results, build help, invalid-option behavior, generated CMake presets, and product metadata.
- Executed a representative build through `utils/build.py`; the host `png2font` target compiled and both reported host products completed successfully.
- Removed both developer-utility temporary ledger rows, leaving the policy at 838 permanent and 89 temporary paths with zero findings.

## Task Commits

1. **Task 1: Split build command into cohesive modules** - `569c3d77a`
2. **Task 2: Separate phase-stepping analysis and adapters** - `eb4358358`

## Files Created/Modified

- `utils/build.py`, `utils/build_config.py`, `utils/build_presets.py`, and `utils/build_products.py` - Stable CLI/import façade over configuration, CMake-preset generation, and artifact publication.
- `utils/phase_stepping/phase_stepping.py` - Stable Click command and public-import façade supporting package and direct-script execution.
- `utils/phase_stepping/signal_analysis.py` - Pure phase correction, sweep parsing, transforms, peak detection, and harmonic analysis.
- `utils/phase_stepping/serial_machine.py` - Serial discovery, connection lifetime, machine commands, and LUT transfer.
- `utils/phase_stepping/plotting.py` - Plotly graph construction, output, and calibration rendering.
- `utils/phase_stepping/test_phase_stepping.py` - Focused unit coverage for pure numerical behavior, parsing, CLI discovery, and import stability.
- `.bright-builds-rules-checks.tsv` - Removed the two completed developer-utility temporary exceptions.

## Decisions Made

- Existing utility filenames remain the executable and import façades; callers do not need to know the new module layout.
- Plot construction belongs to the plotting adapter even when a Click command owns the surrounding measurement workflow.
- The unused `if False` Plotly debug branch in marker location was omitted from the pure analysis module because it was unreachable and violated the adapter boundary.

## Deviations from Plan

None - the plan executed as written.

## Issues Encountered

- The local virtual environment initially lacked declared phase-stepping packages. `utils/phase_stepping/requirements.txt` was installed into `.venv`; no dependency manifests changed.
- The pinned CMake and Ninja bootstrap payloads were absent locally. Exact ignored tool symlinks plus a temporary CMake wrapper allowed `utils/build.py` to execute and compile the host `png2font` target without changing repository sources; all temporary symlinks were removed afterward.
- Bazel refreshed `MODULE.bazel.lock` metadata during verification. The unrelated lockfile delta was restored before each commit.

## Known Stubs

None. The created and modified utility modules contain no placeholder or unwired data paths.

## Residual Risks

- No printer was attached, so live serial transport and hardware calibration remain unexercised. The serial implementation was moved without behavioral edits, raw device payloads were not captured, and pure analysis plus CLI/import behavior are covered automatically.

## Threat Flags

None. The refactor added no endpoint, authentication path, schema boundary, or new trust-boundary file access; serial and artifact behavior remain behind their existing entrypoints.

## Verification

- Exact ordered Cargo sequence before each task commit: `cargo fmt --all`; `cargo clippy --all-targets --all-features -- -D warnings`; `cargo build --all-targets --all-features`; `cargo test --all-features` - passed.
- Build compatibility: pre/post `--help`, invalid-option exit/stdout/stderr, generated `CMakePresets.json`, and serialized product metadata comparisons were byte-identical.
- Representative execution through `utils/build.py` compiled `png2font` and reported two successful host products with zero failures.
- Phase-stepping compatibility: root and all six subcommand help outputs were byte-identical; all 30 original top-level definitions remain exported; deterministic phase-current and rolling-energy outputs matched.
- `python3 -m unittest utils.phase_stepping.test_phase_stepping` - 5 tests passed.
- `python3 utils/build.py --help` and `just generated-check` - passed.
- `just phase40-verify` - 14 policy regressions passed; active policy reports 838 permanent, 89 temporary, and 927 total paths.
- `bun scripts/bright-builds-check.ts all` - zero findings across 7,232 scanned files with 927 exceptions.
- Targeted `.venv/bin/pre-commit run --files ...` - passed for both tasks.
- Physical line checks - both façades and every new module are below 629 lines.
- `git diff --check` - passed.

## Self-Check: PASSED

- All 10 implementation, test, and ledger files and this summary exist.
- Task commits `569c3d77a` and `eb4358358` exist in repository history.
- Both planned developer-utility temporary exception rows are absent, with the immutable permanent policy boundary unchanged.
