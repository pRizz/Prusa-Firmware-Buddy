---
phase: 27-retained-code-and-maintainer-acceptance-decisions
verified: 2026-06-25T03:01:45Z
status: passed
score: "7/7 must-haves verified"
requirements:
  - ACPT-02
  - ACPT-03
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 27-2026-06-25T01-06-06
generated_at: 2026-06-25T03:01:45Z
lifecycle_validated: true
overrides_applied: 0
---

# Phase 27: Retained-Code and Maintainer Acceptance Decisions Verification Report

**Phase Goal:** Maintainers can record retained-code, residual-risk, exception, and final-readiness acceptance decisions as machine-readable inputs.
**Verified:** 2026-06-25T03:01:45Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Maintainer can accept, reject, or exception each retained-code packet with residual-risk rationale and evidence refs. | VERIFIED | `phase27_retained_code_acceptance_decisions_test.py` covers approve, reject, exception, required evidence refs, ISO timestamps, packet role checks, and all 10 Phase 18 retained packet IDs. Generated `decision-row-table.json` has 10 retained rows. |
| 2 | Maintainer can approve or block final-readiness criteria through machine-readable decision inputs, not prose-only notes. | VERIFIED | Final decision validation requires Phase 18 `final_decision_schema.required_fields`, rejects duplicate `decision_id`, rejects contradictory decision/status combinations, and generated output has all 9 final-readiness rows. |
| 3 | Exception approvals identify scope, owner, expiration or revisit condition, and why replacement or demotion can proceed or must stay blocked. | VERIFIED | Contract `exception_policy` includes Phase 18 exception fields plus residual risk and owner; `normalize_exception()` fills owner from approver only when needed and tests reject missing exception evidence refs. |
| 4 | Redaction failures, overclaim failures, unsafe refs, source-ref failures, and stale lifecycle evidence hard-block before exception evaluation. | VERIFIED | `detect_hard_failure_reasons()` runs before `normalize_exception()` for retained and final rows; test `test_hard_blocker_runs_before_exception_handling` proves exception input becomes `blocked-by-hard-failure`. |
| 5 | Decision outputs distinguish evidence failures, accepted retained-code risks, unresolved residual risks, exception state, final-readiness decision state, and demotion approval state. | VERIFIED | Generated outputs include retained decisions, residual-risk register, exception register, final-readiness summary, decision row table, artifact summary, and Phase 28 handoff. Rows expose `evidence_state`, `maintainer_decision`, `exception_state`, `residual_risk_state`, `hard_failure_state`, and `demotion_authorization`. |
| 6 | Phase 27 preserves Phase 18 semantics and consumes Phase 26 upstream rows. | VERIFIED | `--contract-only` exact-matches Phase 18 packet IDs, criteria, fields, vocabularies, exception fields, and hard blockers. Phase 26 rows are loaded from `build/ci-evidence/phase26/upstream-result-row-table.json` and revalidated against Phase 18 identity fields. |
| 7 | Phase 27 never authorizes reference demotion and emits a Phase 28 handoff with demotion blocked/not approved. | VERIFIED | Contract and output set `phase27_may_authorize_demotion: false`; final-reference-demotion approval is rejected; generated handoff has `demotion_authorization: "blocked"` and no `demotion_allowed`. |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` | Phase 27 wrapper contract | VERIFIED | 143 lines; declares source contracts, decision axes, hard blockers, exception policy, Phase 26 path, 12 outputs, and blocked demotion policy. |
| `tools/bazel/phase27_retained_code_acceptance_decisions.py` | Verifier, normalizer, hard-block guard, output writer, CLI | VERIFIED | 1377 lines; implements contract checks, Phase 26 row loading, maintainer input validation, hard-failure precedence, output containment, writing, security scan, and wiring checks. |
| `tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | Regression coverage | VERIFIED | 729 lines; 27 tests passed through direct Python and Bazel wrapper. |
| `tools/bazel/BUILD.bazel` | Phase 27 Bazel targets and runfiles | VERIFIED | Contains `phase27_source_ref_manifests`, `phase27_verify`, and `phase27_verify_tests`. |
| `BUILD.bazel` | Root docs filegroup and aliases | VERIFIED | Contains `phase27_retained_code_acceptance_decisions_docs`, `phase27_verify`, and `phase27_verify_tests`. |
| `tools/bazel/rust_workflow.sh` | Workflow dispatch | VERIFIED | `phase27_verify` runs wiring check, Phase 26 quick generation, then Phase 27 quick consumption. |
| `justfile` | Developer facade | VERIFIED | `phase27-verify` runs Bazel tests before Bazel verifier. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `phase27_retained_code_acceptance_decisions.py` | Phase 18 contract | Exact-match contract loading | WIRED | `gsd-tools verify key-links` passed; code loads `PHASE18_CONTRACT` and checks canonical surfaces. |
| `phase27_retained_code_acceptance_decisions.py` | Phase 26 upstream row table | `--phase26-upstream-rows` and default path | WIRED | Quick mode consumed regenerated `build/ci-evidence/phase26/upstream-result-row-table.json`. |
| `phase27_retained_code_acceptance_decisions.py` | `build/ci-evidence/phase27` | Output writer | WIRED | Quick mode wrote all 12 expected generated artifacts under the Phase 27 output root. |
| `justfile` | `//tools/bazel:phase27_verify` | `phase27-verify` recipe | WIRED | `just phase27-verify` passed and showed test target before verifier target. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `phase27_retained_code_acceptance_decisions.py` | Phase 18 canonical surfaces | `tools/bazel/manifests/phase18_cutover_review_contract.json` | Yes | FLOWING - exact-match checks passed for 10 packets, 9 criteria, schemas, vocabularies, and hard blockers. |
| `phase27_retained_code_acceptance_decisions.py` | Phase 26 upstream rows | `build/ci-evidence/phase26/upstream-result-row-table.json` | Yes | FLOWING - Phase 26 quick generated the row table; Phase 27 validated row IDs and Phase 18 identity fields. |
| `build/ci-evidence/phase27/decision-row-table.json` | Decision rows | Normalized retained + final rows | Yes | FLOWING - 10 retained rows and 9 final-readiness rows emitted. |
| `build/ci-evidence/phase27/phase28-handoff-manifest.json` | Demotion handoff | Contract `phase28_handoff_policy` | Yes | FLOWING - output keeps demotion blocked and names Phase 28 explicit decision. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Unit/security/wiring regressions | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | 27 tests passed | PASS |
| Contract preserves Phase 18 semantics | `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --contract-only` | Passed | PASS |
| Wiring is intact | `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only` | Passed | PASS |
| Phase 26 rows can be regenerated | `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26` | Passed | PASS |
| Phase 27 consumes Phase 26 and emits outputs | `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27` | Passed | PASS |
| Generated output security scan | `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --security-only` | Passed | PASS |
| Bazel test target | `bazel run //tools/bazel:phase27_verify_tests` | Passed; 27 tests | PASS |
| Bazel verifier target | `bazel run //tools/bazel:phase27_verify` | Passed; wiring, Phase 26 quick, Phase 27 quick | PASS |
| Developer facade | `just phase27-verify` | Passed; tests before verifier | PASS |
| Whitespace/diff hygiene | `git diff --check` | Passed | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| ACPT-02 | `27-01-PLAN.md` | Maintainer can accept, reject, or exception retained-code packets with residual-risk rationale. | SATISFIED | Retained input validation covers all 10 Phase 18 packets, explicit approve/reject/exception normalization, evidence refs, residual risk, roles, timestamps, redaction summary, hard blockers, and exception metadata. |
| ACPT-03 | `27-01-PLAN.md` | Maintainer can approve or block final readiness using machine-readable decision inputs. | SATISFIED | Final-readiness input validation requires Phase 18 fields, unique decision IDs, valid status/decision combinations, sensitive-role policy, Phase 26 upstream rows, and blocked reference demotion. |

No orphaned Phase 27 requirements were found in `.planning/REQUIREMENTS.md`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `tools/bazel/phase27_retained_code_acceptance_decisions.py` | 1224, 1226 | `return []` in wiring helper guard paths | Info | Not a stub; helper returns no wiring-order issue when a command is absent and a separate missing-item check reports that case. |

### Human Verification Required

None for the Phase 27 codebase deliverable. Real maintainer approval and reference-demotion decisions remain downstream operational/Phase 28 inputs; Phase 27's machine-readable capability and blocked handoff are automatically verified.

### Gaps Summary

No gaps found. Phase 27 delivers the retained-code and maintainer acceptance decision gate, preserves Phase 18 semantics, consumes Phase 26 upstream rows, writes retained outputs under `build/ci-evidence/phase27`, and keeps reference demotion blocked for Phase 28.

---

_Verified: 2026-06-25T03:01:45Z_
_Verifier: the agent (gsd-verifier)_
