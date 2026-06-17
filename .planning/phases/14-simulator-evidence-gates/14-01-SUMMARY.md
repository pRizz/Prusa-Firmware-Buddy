---
phase: 14-simulator-evidence-gates
plan: 01
subsystem: infra
tags:
  - bazel
  - simulator
  - evidence
  - verification
requires:
  - phase: 13-ci-evidence-orchestration
    provides: CI evidence contract and Bazel/just verification pattern
provides:
  - Phase 14 simulator evidence contract
  - Deterministic quick/dry-run evidence writer
  - Explicit real simulator command path
  - Bazel and just verification wiring
affects:
  - phase15-hardware-safety
  - phase16-live-network
  - phase17-release-artifacts
  - phase18-cutover-review
tech-stack:
  added: []
  patterns:
    - stdlib Python verifier with checked-in JSON contract
    - generated evidence under ignored build/ci-evidence path
key-files:
  created:
    - tools/bazel/manifests/phase14_simulator_evidence_contract.json
    - tools/bazel/phase14_simulator_evidence.py
    - tools/bazel/phase14_simulator_evidence_test.py
  modified:
    - BUILD.bazel
    - justfile
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
key-decisions:
  - "Quick mode validates structure and writes pending simulator-input evidence; it does not mark simulator flows passed."
  - "Real simulator mode requires an explicit firmware .bin with adjacent .bbf and optional simulator binary."
  - "Secret and overclaim scanning applies to the checked-in contract and generated Phase 14 artifacts."
patterns-established:
  - "Phase evidence contracts cite source rows as file#row-id and resolve them generically across Phase 11 manifests."
  - "Generated simulator evidence includes manifest, normalized scenario rows, redacted summary, contract snapshot, and per-scenario log references."
requirements-completed:
  - SIM-01
  - SIM-02
  - SIM-03
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 14-2026-06-17T16-11-34
generated_at: 2026-06-17T17:01:18Z
duration: 23min
completed: 2026-06-17
---

# Phase 14: Simulator Evidence Gates Summary

**Phase-owned simulator evidence contract with deterministic dry-run artifacts, explicit real-run inputs, and Bazel/just gates**

## Performance

- **Duration:** 23 min
- **Started:** 2026-06-17T16:38:01Z
- **Completed:** 2026-06-17T17:01:18Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Added `phase14_simulator_evidence_contract.json` covering startup/readiness, watchdog-visible startup, G-code telemetry, GUI, storage/resource, transfer conflict, selected thermal failures, and traceability boundaries.
- Added `phase14_simulator_evidence.py` with contract validation, Phase 11 source-ref resolution, quick artifact generation, secret/overclaim scanning, wiring validation, and explicit `--run-simulator` input checks.
- Added stdlib unit tests for contract, artifact, command, redaction, and wiring semantics.
- Wired `//tools/bazel:phase14_verify`, `//tools/bazel:phase14_verify_tests`, root aliases, and `just phase14-verify`.

## Task Commits

1. **Tasks 1-2: Contract, runner, artifacts, tests** - `dfdeeee17` (`feat(14): add simulator evidence contract runner and tests`)
2. **Task 3: Bazel and just wiring** - `846a169f3` (`build(14): wire simulator evidence gate`)

## Files Created/Modified

- `tools/bazel/manifests/phase14_simulator_evidence_contract.json` - Scenario contract for `SIM-01`, `SIM-02`, and `SIM-03`.
- `tools/bazel/phase14_simulator_evidence.py` - Verifier/runner and evidence artifact writer.
- `tools/bazel/phase14_simulator_evidence_test.py` - Unit coverage for contract, artifact, command, redaction, and wiring checks.
- `tools/bazel/BUILD.bazel` - Phase 14 Bazel shell targets.
- `BUILD.bazel` - Phase 14 docs filegroup and root aliases.
- `tools/bazel/rust_workflow.sh` - Phase 14 dispatch cases.
- `justfile` - `phase14-verify` facade.

## Generated Artifacts

`python3 tools/bazel/phase14_simulator_evidence.py --quick` writes ignored evidence under `build/ci-evidence/phase14/`:

- `run-manifest.json`
- `normalized-scenarios.json`
- `redacted-summary.json`
- `contract-snapshots/phase14_simulator_evidence_contract.json`
- `logs/*.log` per scenario

These artifacts are generated evidence and were not committed.

## Verification

- `python3 -m json.tool tools/bazel/manifests/phase14_simulator_evidence_contract.json >/dev/null` - passed
- `python3 tools/bazel/phase14_simulator_evidence_test.py` - passed, 15 tests
- `python3 tools/bazel/phase14_simulator_evidence.py --contract-only` - passed
- `python3 tools/bazel/phase14_simulator_evidence.py --security-only` - passed
- `python3 tools/bazel/phase14_simulator_evidence.py --quick` - passed
- `python3 tools/bazel/phase14_simulator_evidence.py --wiring-only` - passed
- `bazel query "//tools/bazel:phase14_verify + //tools/bazel:phase14_verify_tests + //:phase14_verify + //:phase14_verify_tests"` - passed
- `just phase14-verify` - passed
- `git diff --check` - passed

## Decisions Made

- Dry-run evidence records active simulator scenarios as `pending-simulator-input`, with only the traceability boundary row passing through contract validation alone.
- Real simulator execution is available only through `--run-simulator --firmware <firmware.bin>` and requires an adjacent `.bbf`; this prevents local quick checks from becoming false pass evidence.
- Generated summaries include input names and status reasons, but not raw firmware payloads, credential values, crash dumps, or service tokens.

## Deviations from Plan

None - plan executed as written. The implementation kept the scope to Phase 14 evidence tooling and wiring.

## Issues Encountered

- The first validator draft treated explicitly empty node lists as missing fields. Fixed `require_fields` so empty lists can be valid and per-field rules decide which lists must be non-empty.
- One test initially asserted generated artifact paths after the temporary test root was cleaned up. Moved those assertions inside the temporary-root context.

## Real Simulator Status

Real simulator execution was not run in this environment because no firmware `.bin` with adjacent `.bbf` and simulator runtime inputs were provided. The implemented path validates those inputs and builds pytest argument lists without shell execution.

## Residual Boundaries

- Physical watchdog timing, thermal/motion safety, physical storage media, physical UI input, MMU, RS485, toolchanger, and hardware-only safety remain Phase 15 scope.
- Live Connect/WUI/TLS, telemetry, proxy, long-transfer, and crash-dump upload evidence remain Phase 16 scope.
- Release-candidate artifacts, signing, provenance, resources, and auxiliary packages remain Phase 17 scope.
- Retained-code acceptance and final reference-demotion approval remain Phase 18 scope.

## User Setup Required

None for contract/dry-run validation. Real simulator execution requires firmware and simulator inputs as documented by the contract and `--run-simulator` CLI.

## Next Phase Readiness

Phase 14 now gives later cutover phases a reviewable simulator evidence artifact contract and local gate. Hardware, live network, release, and retained-code acceptance phases can cite the residual boundary statuses without treating dry-run simulator evidence as hardware proof.

## Self-Check: PASSED

- All planned files exist.
- Required verification commands passed.
- No generated evidence artifacts were committed.
- `.planning/config.json` remained orchestrator-owned and unstaged.

---
*Phase: 14-simulator-evidence-gates*
*Completed: 2026-06-17*
