---
phase: 15-hardware-safety-and-media-qualification
plan: 01
subsystem: evidence
tags: [hardware, safety, storage-media, bazel, just, unittest]
requires:
  - phase: 14-simulator-evidence-gates
    provides: Simulator evidence contract, verifier, artifact, and Bazel/just wiring pattern.
provides:
  - Phase 15 hardware evidence contract with row-level source refs and required operator metadata.
  - Stdlib verifier for contract, security, quick artifact, operator-evidence, and wiring validation.
  - Bazel labels and just facade for repeatable Phase 15 verification.
  - Regression tests for row coverage, metadata, path guards, redaction, artifacts, operator evidence, and wiring.
affects: [phase15, phase16, phase17, phase18, cutover-evidence]
tech-stack:
  added: []
  patterns:
    - Checked-in evidence contract plus stdlib verifier.
    - Deterministic ignored evidence artifacts under build/ci-evidence.
    - Bazel shell_binary targets dispatched through tools/bazel/rust_workflow.sh.
key-files:
  created:
    - tools/bazel/manifests/phase15_hardware_evidence_contract.json
    - tools/bazel/phase15_hardware_evidence.py
    - tools/bazel/phase15_hardware_evidence_test.py
  modified:
    - BUILD.bazel
    - justfile
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
key-decisions:
  - "Phase 15 physical rows remain pending in quick mode; only operator evidence can mark hardware-observation rows passed or failed."
  - "Operator evidence must provide device, printer family, board, firmware build, operator, timestamp, scenario, result, artifact ref, and residual risk."
  - "Artifact paths and operator refs stay repo-relative under build/ci-evidence/phase15."
  - "Phase 15 uses the existing Bazel rust_workflow dispatch pattern and just runs tests before the verifier."
patterns-established:
  - "Hardware evidence rows use source_contract_refs that resolve against prior phase manifests."
  - "Security scanning covers the checked-in contract and generated Phase 15 artifacts."
requirements-completed: [HARD-01, HARD-02, HARD-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 15-2026-06-17T22-53-45
generated_at: 2026-06-18T00:19:57Z
duration: 23m31s
completed: 2026-06-18
---

# Phase 15 Plan 01: Hardware Safety and Media Qualification Summary

**Row-level hardware safety and media evidence contract with operator-gated results, sanitized local artifacts, and Bazel/just verification.**

## Performance

- **Duration:** 23m31s
- **Started:** 2026-06-17T23:56:26Z
- **Completed:** 2026-06-18T00:19:57Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Created a Phase 15 hardware evidence contract covering supported printer smoke, board startup readiness, storage media, physical UI input, safety/fault handling, MMU, RS485/Modbus, toolchanger, auxiliary-controller combinations, and contract traceability.
- Implemented a stdlib verifier with `--contract-only`, `--security-only`, `--quick`, `--operator-evidence`, `--output-dir`, and `--wiring-only` modes.
- Added deterministic ignored artifacts under `build/ci-evidence/phase15`: run manifest, normalized scenario results, redacted summary, contract snapshot, operator input echo, and scenario logs.
- Wired Phase 15 through Bazel labels, root aliases, `rust_workflow.sh`, and `just phase15-verify`.

## Task Commits

1. **Task 1 RED: Contract tests** - `e711c96c8` (test)
2. **Task 1 GREEN: Contract and verifier helpers** - `c068b5f65` (feat)
3. **Task 2 RED: Collection/security tests** - `b0fd985c1` (test)
4. **Task 2 GREEN: Collection/security implementation** - `09624860d` (feat)
5. **Task 3 RED: Wiring tests** - `8cbff5719` (test)
6. **Task 3 GREEN: Bazel/just wiring** - `ce53c7d74` (feat)
7. **Rule 2 fix: Complete guard coverage** - `7916c8de6` (fix)

## Files Created/Modified

- `tools/bazel/manifests/phase15_hardware_evidence_contract.json` - Phase 15 row-level hardware evidence contract.
- `tools/bazel/phase15_hardware_evidence.py` - Contract, security, quick artifact, operator evidence, and wiring verifier.
- `tools/bazel/phase15_hardware_evidence_test.py` - Stdlib unittest coverage for the Phase 15 verifier and wiring.
- `tools/bazel/BUILD.bazel` - Phase 15 source-ref manifest filegroup and verifier/test labels.
- `BUILD.bazel` - Phase 15 docs filegroup and root aliases.
- `tools/bazel/rust_workflow.sh` - Phase 15 workflow dispatch.
- `justfile` - `phase15-verify` facade.

## Verification

- `python3 -m json.tool tools/bazel/manifests/phase15_hardware_evidence_contract.json >/dev/null`
- `python3 tools/bazel/phase15_hardware_evidence_test.py`
- `python3 tools/bazel/phase15_hardware_evidence.py --contract-only`
- `python3 tools/bazel/phase15_hardware_evidence.py --security-only`
- `python3 tools/bazel/phase15_hardware_evidence.py --quick`
- `python3 tools/bazel/phase15_hardware_evidence.py --wiring-only`
- `bazel run //tools/bazel:phase15_verify_tests`
- `bazel run //tools/bazel:phase15_verify`
- `bazel query "//tools/bazel:phase15_verify + //tools/bazel:phase15_verify_tests + //:phase15_verify + //:phase15_verify_tests"`
- `just phase15-verify`
- `git diff --check`

All commands passed.

## Decisions Made

- Quick mode produces truthful local evidence by leaving physical hardware-observation rows as `pending-hardware-input`; the source-contract row can pass by structural validation.
- Operator evidence is the only path that can mark physical scenarios `passed`, `failed`, or `blocked-hardware-unavailable`.
- Contract, operator, output-dir, and artifact-ref paths are guarded as repo-relative paths under `build/ci-evidence/phase15`.
- Phase 15 follows the Phase 14 Bazel/just wiring model and enforces the tests-before-verifier ordering.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Completed plan-required guard vocabulary and artifact fields**
- **Found during:** Summary self-check against the Phase 15 plan.
- **Issue:** The verifier covered the security and overclaim categories, but not every exact marker phrase and generated-artifact field required by the plan. The Phase 15 Bazel target also needed the Phase 11 cutover docs runfile named in the plan.
- **Fix:** Expanded the denied marker/wording vocabulary, renamed the security tests to the planned test names, added normalized artifact fields and run-manifest metadata, and added the Phase 11 docs runfile.
- **Files modified:** `tools/bazel/phase15_hardware_evidence.py`, `tools/bazel/phase15_hardware_evidence_test.py`, `tools/bazel/BUILD.bazel`
- **Verification:** `python3 tools/bazel/phase15_hardware_evidence_test.py`, direct verifier modes, generated artifact `jq` checks, Bazel verifier labels, `just phase15-verify`, and `git diff --check`.
- **Committed in:** `7916c8de6`

**Total deviations:** 1 auto-fixed (Rule 2 missing critical functionality)
**Impact on plan:** The fix tightened compliance with the original plan and threat model; it did not add new scope.

## Auth Gates

None.

## Known Stubs

None. The quick-mode pending hardware rows are intentional qualification states, not stubs.

## Threat Mitigations

- Implemented the planned information-disclosure controls through contract and generated-artifact scans.
- Implemented planned tampering controls with repo-relative path checks for contract output paths, `--output-dir`, and operator `artifact_ref`.
- Implemented planned repudiation controls by requiring complete operator metadata before physical rows can leave pending state.
- Implemented planned source-ref controls by resolving every `source_contract_refs` value as `file#row-id`.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 16 can now depend on the same evidence pattern for live network and transfer qualification: checked-in contract rows, secret-safe operator inputs, deterministic local artifact generation, and Bazel/just workflow gates.

## Self-Check: PASSED

- Confirmed all created/modified plan files exist.
- Confirmed task and Rule 2 fix commits exist: `e711c96c8`, `c068b5f65`, `b0fd985c1`, `09624860d`, `8cbff5719`, `ce53c7d74`, `7916c8de6`.
- Confirmed `.planning/config.json` remains unstaged and uncommitted.

---
*Phase: 15-hardware-safety-and-media-qualification*
*Completed: 2026-06-18*
