---
phase: 20-release-candidate-artifact-production
phase_number: 20
phase_name: Release Candidate Artifact Production
secured: 2026-06-21
asvs_level: 1
block_on: high
threats_total: 10
threats_closed: 10
threats_open: 0
status: secured
generated_by: gsd-security-auditor
---

# Phase 20 Security Verification

## Scope

Verified the declared STRIDE threat mitigations from:

- `20-01-PLAN.md`
- `20-02-PLAN.md`

Implementation files were read-only for this audit. Only this `20-SECURITY.md` file was created.

## Threat Verification

| Threat ID | Category | Disposition | Status | Evidence |
|-----------|----------|-------------|--------|----------|
| P20-01-T-20-01 | Spoofing / Repudiation | mitigate | CLOSED | Passed rows are limited to `APPROVED_PASS_PROOF_CLASSES` in `tools/bazel/phase20_release_candidate_artifacts.py:95`; `validate_release_row` rejects disallowed passed proof classes and requires pass metadata at `tools/bazel/phase20_release_candidate_artifacts.py:535`, `tools/bazel/phase20_release_candidate_artifacts.py:564`, and `tools/bazel/phase20_release_candidate_artifacts.py:581`. Regression coverage: `test_passed_result_rejects_local_smoke_and_template_only_proof` and metadata-required tests in `tools/bazel/phase20_release_candidate_artifacts_test.py:527` and `tools/bazel/phase20_release_candidate_artifacts_test.py:547`. |
| P20-01-T-20-02 | Information Disclosure | mitigate | CLOSED | Forbidden key, credential, payload, and crash-dump fields/text are listed at `tools/bazel/phase20_release_candidate_artifacts.py:141` and `tools/bazel/phase20_release_candidate_artifacts.py:154`; checked-in manifests, release input, and generated artifacts are scanned at `tools/bazel/phase20_release_candidate_artifacts.py:456` and `tools/bazel/phase20_release_candidate_artifacts.py:483`. Regression coverage starts at `tools/bazel/phase20_release_candidate_artifacts_test.py:573`. |
| P20-01-T-20-03 | Tampering / Information Disclosure | mitigate | CLOSED | Ref guards allow `external://phase20/` or repo-relative `build/ci-evidence/phase20` only at `tools/bazel/phase20_release_candidate_artifacts.py:21`, `tools/bazel/phase20_release_candidate_artifacts.py:258`, and `tools/bazel/phase20_release_candidate_artifacts.py:273`; output containment rejects traversal and symlink escape at `tools/bazel/phase20_release_candidate_artifacts.py:285`. Regression coverage is at `tools/bazel/phase20_release_candidate_artifacts_test.py:477`, `tools/bazel/phase20_release_candidate_artifacts_test.py:504`, and `tools/bazel/phase20_release_candidate_artifacts_test.py:600`. |
| P20-01-T-20-04 | Repudiation | mitigate | CLOSED | Quick rows default to `template-only` and contract default status at `tools/bazel/phase20_release_candidate_artifacts.py:623`; result manifests emit `release_inputs_supplied = bool(release_rows)` and include `release_inputs_supplied` at `tools/bazel/phase20_release_candidate_artifacts.py:686` and `tools/bazel/phase20_release_candidate_artifacts.py:692`. Regression coverage: `test_quick_without_release_input_writes_pending_result_manifest` at `tools/bazel/phase20_release_candidate_artifacts_test.py:459`. |
| P20-01-T-20-05 | Tampering / Process Integrity | mitigate | CLOSED | Allowed mismatch classes are defined at `tools/bazel/phase20_release_candidate_artifacts.py:111`; passed rows require contract-declared comparison metadata at `tools/bazel/phase20_release_candidate_artifacts.py:551`, and invalid classes are rejected at `tools/bazel/phase20_release_candidate_artifacts.py:561`. The contract requires `mismatch_class`, `mismatch_reason`, `owner_phase`, `affected_artifact_surface`, and `residual_risk` for every row, starting at `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json:16`. Regression coverage starts at `tools/bazel/phase20_release_candidate_artifacts_test.py:627`. |
| P20-02-T-20-01 | Spoofing / Repudiation | mitigate | CLOSED | `tools/bazel/BUILD.bazel` defines `phase20_release_environment_input_manifest` at `tools/bazel/BUILD.bazel:377` and wires `phase17_release_candidate_artifacts` to `srcs = [":phase20_release_environment_input_manifest"]` at `tools/bazel/BUILD.bazel:382`. Phase 20 rejects smoke deps at `tools/bazel/phase20_release_candidate_artifacts.py:911`; Phase 17 independently requires the same source and rejects smoke deps at `tools/bazel/phase17_release_candidate_evidence.py:966`. |
| P20-02-T-20-02 | Information Disclosure | mitigate | CLOSED | The Phase 20 input manifest is metadata-only template evidence with `template-only`, `pending-release-input`, empty digest/build/retention fields, and `external://phase20/` refs at `tools/bazel/manifests/phase20_release_environment_inputs.template.json:6` and `tools/bazel/manifests/phase20_release_environment_inputs.template.json:8`. Plan 01 redaction guards remain active at `tools/bazel/phase20_release_candidate_artifacts.py:141`, `tools/bazel/phase20_release_candidate_artifacts.py:154`, and `tools/bazel/phase20_release_candidate_artifacts.py:456`. |
| P20-02-T-20-03 | Tampering | mitigate | CLOSED | `--wiring-only` validates exact tools BUILD filegroups and data deps at `tools/bazel/phase20_release_candidate_artifacts.py:948`, root aliases/docs at `tools/bazel/phase20_release_candidate_artifacts.py:1004`, workflow dispatch at `tools/bazel/phase20_release_candidate_artifacts.py:1030`, and just recipe ordering at `tools/bazel/phase20_release_candidate_artifacts.py:1068`. Actual wiring exists in `tools/bazel/BUILD.bazel:525`, `tools/bazel/BUILD.bazel:537`, `BUILD.bazel:171`, `BUILD.bazel:387`, `tools/bazel/rust_workflow.sh:120`, and `justfile:71`. |
| P20-02-T-20-04 | Repudiation | mitigate | CLOSED | `just phase20-verify` runs `bazel run //tools/bazel:phase20_verify_tests` before `bazel run //tools/bazel:phase20_verify` at `justfile:71`; `check_just_wiring` enforces that order at `tools/bazel/phase20_release_candidate_artifacts.py:1068`. The shell dispatcher exposes separate `phase20_verify_tests` and `phase20_verify` cases at `tools/bazel/rust_workflow.sh:120` and `tools/bazel/rust_workflow.sh:124`. Regression coverage starts at `tools/bazel/phase20_release_candidate_artifacts_test.py:768`. |
| P20-02-T-20-05 | Process Integrity | mitigate | CLOSED | Phase 17 compatibility checks require the Phase 20 manifest and reject empty/smoke/phase3 deps at `tools/bazel/phase17_release_candidate_evidence.py:966`. Regression tests cover empty filegroup rejection, Phase 20 manifest acceptance, smoke wrapping rejection, and output-root symlink containment at `tools/bazel/phase17_release_candidate_evidence_test.py:545`, `tools/bazel/phase17_release_candidate_evidence_test.py:725`, `tools/bazel/phase17_release_candidate_evidence_test.py:745`, and `tools/bazel/phase17_release_candidate_evidence_test.py:758`. |

## Unregistered Flags

None. `20-01-SUMMARY.md` and `20-02-SUMMARY.md` contain no `## Threat Flags` section or threat flag entries.

## Accepted Risks

None.

## Verification Commands

Passed during this audit:

- `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` - 18 tests passed.
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` - 23 tests passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only`
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only`
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only`

`--quick` was not re-run in this security audit to keep writes limited to `20-SECURITY.md`; quick-mode behavior is verified by the source-level checks and regression tests above, and prior phase verification in `20-VERIFICATION.md` records `--quick` as passing.

## Audit Trail

| Date | Auditor | ASVS Level | Closed | Open | Notes |
|------|---------|------------|--------|------|-------|
| 2026-06-21 | gsd-security-auditor | 1 | 10 | 0 | Verified all declared Phase 20 mitigations by disposition; no unregistered threat flags found. |
