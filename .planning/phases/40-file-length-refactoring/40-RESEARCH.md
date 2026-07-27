---
phase: 40-file-length-refactoring
generated_by: gsd-phase-researcher-fallback
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T17:08:00.000Z
status: complete
---

# Phase 40 Research: File Length Refactoring

## Research Summary

The live managed check reports:

```text
SUMMARY file-lengths scanned=7217 exceptions=0 findings=933
```

The approved program is feasible without changing the managed checker. Its exact-path TSV interface already rejects unlisted oversized files, requires non-empty reasons, and exposes stale exceptions. Phase 40 should first seed the full current set, then use the ledger as a shrink-only ratchet while stable façades preserve every external contract.

The validated classification is:

| Class | Initial | Terminal |
| --- | ---: | ---: |
| Provenance/declarative permanent exceptions | 838 | 838 |
| Repo-owned temporary exceptions | 95 | 0 |
| Repo-owned permanent exceptions | 0 | 3 |
| Repo-owned files refactored below 629 lines | 0 | 92 |
| Checker findings | 933 | 0 |
| Total active exceptions | 0 | 841 |

The three owned permanent exceptions are fixed:

- `src/guiapi/include/Rect16.h`
- `src/connect/planner.cpp`
- `src/gui/screen_tools_mapping.cpp`

Every other repo-owned finding must be eliminated. The permanent provenance set consists of imported `lib/` findings except the three repo-owned WUI sources, upstream WUI sources, test stubs, generated fonts and configuration headers, ST CMSIS sources, and the three approved declarative registry/configuration files documented in CONTEXT.md.

## Exception Ledger Strategy

Use `.bright-builds-rules-checks.tsv` as the single source consumed by the managed checker:

```text
file-lengths<TAB>repo/relative/path<TAB>reason
```

Recommended stable reason prefixes:

- `permanent: imported/upstream; ...`
- `permanent: generated; source=...`
- `permanent: declarative registry; deletion-test=...`
- `permanent: owned deep module; deletion-test=...`
- `temporary: campaign=<id>; remove when file is below 629 lines and campaign gates pass`

The baseline change should generate candidate rows mechanically from the current checker output, classify them against explicit exact path sets, sort by path, and fail if the resulting partition is not exactly 838 permanent plus 95 temporary. The committed TSV, not a second manifest, remains canonical.

Add the smallest repo-owned policy verifier necessary to parse the TSV and assert:

1. Every row has exactly three tab-separated fields and uses an approved reason prefix.
2. The 838 provenance/declarative paths cannot be converted to temporary owned debt.
3. Only the three locked owned paths can use `permanent: owned deep module`.
4. Temporary paths are a subset of the original 95-path owned set.
5. Terminal mode requires the exact 841-path permanent set and no temporary reasons.

Do not add a generated projection or merge-base dependency. Both create a second authority or make local verification depend on branch topology.

## Exact Owned Campaign Inventory

### Rust domain modules — 4 refactors

- `rust/crates/domain/src/network.rs`
- `rust/crates/domain/src/auxiliary.rs`
- `rust/crates/domain/src/feature.rs`
- `rust/crates/domain/src/gui.rs`

Keep `network.rs` and `auxiliary.rs` as stable façades over private `network/` and `auxiliary/` concept modules. Move only colocated tests out of `feature.rs` and `gui.rs` where production implementation is already cohesive.

### Developer utilities — 2 refactors

- `utils/build.py`
- `utils/phase_stepping/phase_stepping.py`

`utils/build.py` remains the command façade over configuration, preset selection, and artifact publication modules. Phase stepping keeps its Click interface and `PhaseCorrection` import while isolating pure signal analysis, the serial-machine adapter, and the Plotly adapter.

### Python Phase 5–11 — 12 refactors

- `tools/bazel/phase5_verify.py`
- `tools/bazel/phase6_verify.py`
- `tools/bazel/phase7_verify.py`
- `tools/bazel/phase7_verify_test.py`
- `tools/bazel/phase8_verify.py`
- `tools/bazel/phase8_verify_test.py`
- `tools/bazel/phase9_verify.py`
- `tools/bazel/phase9_verify_test.py`
- `tools/bazel/phase10_verify.py`
- `tools/bazel/phase10_verify_test.py`
- `tools/bazel/phase11_verify.py`
- `tools/bazel/phase11_verify_test.py`

### Python Phase 13–17 — 8 refactors

- `tools/bazel/phase13_ci_evidence.py`
- `tools/bazel/phase14_simulator_evidence.py`
- `tools/bazel/phase15_hardware_evidence.py`
- `tools/bazel/phase15_hardware_evidence_test.py`
- `tools/bazel/phase16_live_network_evidence.py`
- `tools/bazel/phase16_live_network_evidence_test.py`
- `tools/bazel/phase17_release_candidate_evidence.py`
- `tools/bazel/phase17_release_candidate_evidence_test.py`

### Python Phase 18–28 — 16 refactors

- `tools/bazel/phase18_cutover_review.py`
- `tools/bazel/phase18_cutover_review_test.py`
- `tools/bazel/phase19_aggregate_ci_evidence.py`
- `tools/bazel/phase20_release_candidate_artifacts.py`
- `tools/bazel/phase20_release_candidate_artifacts_test.py`
- `tools/bazel/phase22_metadata_reconciliation.py`
- `tools/bazel/phase23_simulator_evidence_execution.py`
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`
- `tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py`
- `tools/bazel/phase25_live_service_evidence_execution.py`
- `tools/bazel/phase26_release_signing_upstream_evidence.py`
- `tools/bazel/phase26_release_signing_upstream_evidence_test.py`
- `tools/bazel/phase27_retained_code_acceptance_decisions.py`
- `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
- `tools/bazel/phase28_final_readiness_packet.py`
- `tools/bazel/phase28_final_readiness_packet_test.py`

### Python Phase 31–38 — 12 refactors

- `tools/bazel/phase31_final_evidence_intake.py`
- `tools/bazel/phase31_final_evidence_intake_test.py`
- `tools/bazel/phase32_blocker_register_triage.py`
- `tools/bazel/phase32_blocker_register_triage_test.py`
- `tools/bazel/phase33_maintainer_decision_inputs.py`
- `tools/bazel/phase33_maintainer_decision_inputs_test.py`
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py`
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
- `tools/bazel/phase35_cutover_decision_artifact.py`
- `tools/bazel/phase35_cutover_decision_artifact_test.py`
- `tools/bazel/phase38_cutover_workflow.py`
- `tools/bazel/phase38_cutover_workflow_test.py`

For every Python group, preserve the original script as the external interface. Extract phase-prefixed contract parsing, pure decision policy, publication/security, and orchestration implementation. Do not introduce a shared evidence framework. Split tests by interface and failure domain; keep shared fixtures small and phase-local.

### Firmware characterization tests — 7 refactors

- `tests/unit/common/gcode/reader/gcode_reader.cpp`
- `tests/unit/gui/rectangle_tests.cpp`
- `tests/unit/gui/window/tests_layout.cpp`
- `tests/unit/lib/Marlin/MMU2/mmu2_protocol_logic_test.cpp`
- `tests/unit/lib/WUI/nhttp/server_tests.cpp`
- `tests/unit/media_prefetch/media_prefetch_tests.cpp`
- `tests/unit/persistent_stores/EEPROM_journal_test.cpp`

Split these before production firmware campaigns. Register new test files in their existing CMake targets without changing test behavior.

### Parser, UI, protocol, and WUI — 13 owned findings

Refactor these 11:

- `lib/WUI/espif.cpp`
- `lib/WUI/nhttp/server.cpp`
- `lib/WUI/wui.cpp`
- `src/common/gcode/gcode_info.cpp`
- `src/common/gcode/gcode_reader_binary.cpp`
- `src/common/probe_analysis.cpp`
- `src/connect/render.cpp`
- `src/gui/MItem_tools.cpp`
- `src/gui/MItem_tools.hpp`
- `src/gui/screen_printing.cpp`
- `src/state/printer_state.cpp`

Convert these two to the locked permanent-owned reason:

- `src/guiapi/include/Rect16.h`
- `src/gui/screen_tools_mapping.cpp`

### Network and media — 6 owned findings

Refactor these five:

- `src/buddy/filesystem_fatfs.cpp`
- `src/common/media_prefetch/media_prefetch.cpp`
- `src/connect/connect.cpp`
- `src/connect/marlin_printer.cpp`
- `src/transfers/transfer.cpp`

Convert `src/connect/planner.cpp` to the locked permanent-owned reason.

### Persistent storage — 2 refactors

- `src/persistent_stores/journal/backend.cpp`
- `src/persistent_stores/store_instances/config_store/store_definition.cpp`

Keep journal state policy separate from flash/storage effects. Preserve generated hashes, persisted layout, migration behavior, and defaults.

### Hardware and auxiliary controllers — 7 refactors

- `src/device/stm32f4/hal_msp.cpp`
- `src/device/stm32f4/peripherals.cpp`
- `src/guiapi/src/ili9488.cpp`
- `src/guiapi/src/st7789v.cpp`
- `src/puppies/Dwarf.cpp`
- `src/puppy/shared/modbus/ModbusProtocol.cpp`
- `src/puppy/xbuddy_extension/hal.cpp`

Keep HAL calls and wire I/O in adapters. Move register tables, state transitions, and protocol decisions into private implementation modules only when the deletion test proves a real seam.

### Print and safety lifecycle — 6 refactors

- `src/buddy/main.cpp`
- `src/common/marlin_print_preview.cpp`
- `src/common/marlin_server.cpp`
- `src/common/power_panic.cpp`
- `src/marlin_stubs/G425.cpp`
- `src/marlin_stubs/pause/pause.cpp`

Perform `marlin_server.cpp` last. Preserve `marlin_server.hpp`, queue/event ordering, task ownership, public symbols, and fatal/safety behavior. Extract pure lifecycle and request-state policy while leaving FreeRTOS, Marlin, filesystem, and hardware effects in adapters.

## Build and Interface Integration

- Rust: declare private child modules from the stable façade; update no public crate exports unless the export is a like-for-like re-export.
- Bazel Python: add phase-prefixed source files to the existing `py_library`, `py_binary`, and `py_test` `srcs`/`deps`; keep labels and main modules unchanged.
- Utilities: preserve `utils/build.py` invocation, argument parser, product paths, and `PhaseCorrection` imports.
- C++ firmware: register extracted `.cpp` files in the owning subsystem `CMakeLists.txt`; preserve option guards, include ordering, and public headers.
- Tests: add split test sources to existing Catch targets. Do not create a new test executable when the current target can own the behavior.
- Generated sources: change neither generated outputs nor their checked-in ownership merely to satisfy length.

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| A façade becomes a shallow forwarding layer | Keep one stable interface but move coherent policy behind it; apply the deletion test before accepting each seam. |
| Python artifact or exit behavior drifts | Snapshot emitted files, JSON/Markdown schemas, status vocabularies, stderr, and exit codes before extraction. |
| C++ static initialization or link ordering changes | Preserve target ownership and option guards; run representative builds after each production campaign. |
| Generated or upstream code is accidentally refactored | Freeze the exact provenance set and require an explicit plan revision for reclassification. |
| Tests are merely moved and lose coverage | Split by behavior/failure domain and run the original target before and after each split. |
| `just build`, `just test`, or simulator façades only print commands | Capture and run the underlying command when execution is not enabled; do not treat print-only success as evidence. |
| High-risk work grows too large | Keep campaign gates serial and split within a campaign by non-overlapping subsystem ownership. |

## Validation Architecture

### Fast campaign gate

Every task or atomic campaign change runs:

```text
bun scripts/bright-builds-check.ts all
git diff --check
affected formatter/pre-commit checks
focused unit or contract test
```

The checker output must show no new finding. After a temporary row is removed, it must show no stale exception for that path.

### Rust gate

Run in this exact order before every commit touching the Rust project:

```text
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

Then run `just rust-format`, `just rust-lint`, `just rust-build`, `just rust-test`, and affected Phase 8–10 gates.

### Python and utilities gate

- Run each affected `just phaseN-verify`.
- Run focused Python test targets through their Bazel labels or direct standard-library test commands used by the existing gate.
- For utilities, run `python3 utils/build.py --help`, phase-stepping tests, `just generated-check`, and the underlying build command.
- Compare pre/post artifact bytes or parsed structures where timestamps or staging paths are expected to vary.

### Firmware gate

- Firmware test split: original and split Catch targets must pass with identical cases.
- Low/mid-risk source campaigns: focused host tests, underlying `just test` command, representative firmware build, and checker.
- Network, persistence, hardware, print, and safety campaigns: add simulator parity and generated checks where applicable.
- Final print/safety campaign: representative supported-product build matrix plus simulator integration using explicit firmware and simulator paths.
- Require hardware-aware review. Add physical hardware only for changed behavior or simulator coverage gaps.

### Terminal reconciliation

From a clean checkout, require:

```text
SUMMARY file-lengths ... exceptions=841 findings=0
```

Also prove:

- zero `temporary:` reasons;
- exact match to the 838 frozen provenance/declarative paths plus the three locked owned paths;
- all 92 refactored owned files have fewer than 629 physical lines;
- all newly created source and test files have fewer than 629 physical lines;
- external interface snapshots and build labels are unchanged;
- all required campaign gates and final cross-stack gates passed.

## Planning Recommendation

Use one baseline plan, six low-risk language/tooling plans, one firmware-test plan, and five production-firmware plans. Encode strict dependencies so later campaigns cannot begin before earlier campaign summaries exist. Within a plan, tasks may cover several files only when they share one stable interface, one build target, and one focused verification gate. Keep `marlin_server.cpp` in its own final task or plan.
