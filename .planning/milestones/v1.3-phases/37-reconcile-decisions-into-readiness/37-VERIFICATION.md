---
phase: 37-reconcile-decisions-into-readiness
verified: 2026-07-26T08:32:43Z
status: passed
score: 9/9 must-haves verified
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 37-2026-07-26T06-52-46
generated_at: 2026-07-26T08:32:43Z
lifecycle_validated: true
overrides_applied: 0
---

# Phase 37: Reconcile Decisions Into Readiness Verification Report

**Phase Goal:** Phase 34 resolves the real Phase 27/28 blocker population with explicit Phase 33 decisions and can produce unblocked readiness from complete valid inputs.
**Verified:** 2026-07-26T08:32:43Z
**Status:** passed
**Verified revision:** `c1a3e1eb9bb2ddb899bdeaa0c8f798138866def4`

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Every Phase 33 target binds an explicit `row_ref`, `decision_axis`, and `decision_subject_id`. | ✓ VERIFIED | `validate_decision_targets` requires the complete typed triple, checks it against the canonical Phase 32 register, and preserves it in the normalized handoff. The 40-test Phase 33 suite covers missing fields, duplicate triples, colliding refs, projection mismatches, and trusted-input containment. |
| 2 | A decision resolves a row only when its complete typed identity matches exactly one canonical Phase 32 row. | ✓ VERIFIED | `phase34_decision_reconciliation.py` parses canonical rows and evaluates exact triple matches without path, prefix, gate, or axis fallback. Focused tests prove exact resolution, zero-match behavior, axis/subject mismatches, and duplicate canonical identities. |
| 3 | Missing, duplicate, conflicting, stale, malformed, mismatched, rejected, invalid, and hard-blocker decisions remain blocked with specific diagnostics. | ✓ VERIFIED | The pure reconciliation suite covers every listed class, including `decision-target-missing`, row/axis/subject mismatch, duplicate/conflict, stale lifecycle, invalid/rejected values, malformed targets, and hard blockers that cannot be approved away. |
| 4 | Reference-demotion authority remains independent from readiness approval. | ✓ VERIFIED | Axis-specific approving values are explicit; demotion diagnostics use `readiness_effect: independent`. Tests prove demotion approval cannot clear readiness and readiness approval cannot grant demotion authorization. |
| 5 | Phase 34's canonical ledger retains Phase 31 evidence rows and first-class Phase 32 decision-domain rows on distinct evaluation paths. | ✓ VERIFIED | Evidence rows carry `ledger_row_kind: evidence` and Phase 31 source identity. Decision-domain rows preserve canonical Phase 32 identity, axis, subject, classification, refs, coverage, and reason codes; sparse evidence overlay explicitly skips those rows. |
| 6 | Complete valid actual producer inputs reach `readiness_state: unblocked`. | ✓ VERIFIED | `test_complete_real_producer_chain_publishes_unblocked_bundle` runs the actual Phase 31, Phase 32, Phase 33, and Phase 34 producers, asserts an unblocked packet, verifies ledger/report consistency, and observes both ledger row kinds. |
| 7 | One-concern invalid mutations of the real producer chain remain blocked. | ✓ VERIFIED | Eight integration mutations cover omitted binding, row-ref mismatch, axis mismatch, subject mismatch, stale lifecycle, invalid value, duplicate binding, and conflicting binding. Each asserts `blocked` plus its specific reason code. |
| 8 | The authoritative Phase 34 gate runs boundary, reconciliation, ledger, and real-producer tests before publication. | ✓ VERIFIED | `phase34_verify_tests` executes the Phase 33 boundary suite, pure reconciliation suite, Phase 34 ledger suite, and integration suite in that order. `just phase34-verify` passed all 107 tests before running the verifier/publication target. |
| 9 | Phase 37 stops at retained Phase 34 readiness artifacts and grants no Phase 35 cutover verdict or implicit demotion. | ✓ VERIFIED | The Phase 34 workflow arm invokes only Phase 34 tests and verifier. Phase 35 has a separate workflow arm; the Phase 34 packet preserves a distinct `reference_demotion_authorization` state. |

**Score:** 9/9 truths verified

## Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` | Typed target contract | ✓ VERIFIED | Declares `decision_targets` and all supported decision axes/artifacts. |
| `tools/bazel/phase33_maintainer_decision_inputs.py` | Fail-closed Phase 33 boundary | ✓ VERIFIED | Validates exact typed targets, decision metadata, lifecycle, hard blockers, safe refs, authority limits, and secret-safe outputs. `resolved_under` rejects any symlink component in the Phase 32 handoff, canonical register, or maintainer-decision input before output reset/publication. |
| `tools/bazel/phase34_decision_reconciliation.py` | Pure exact-match reconciliation core | ✓ VERIFIED | Implements canonical parsing, exact matching, axis-specific approval, stable diagnostics, and readiness derivation. |
| `tools/bazel/phase34_final_readiness_demotion_dry_run.py` | Dual-source canonical ledger and retained readiness publication | ✓ VERIFIED | Consumes Phase 31 evidence and Phase 32 decision-domain rows through separate evaluation paths, then derives packet and report from the same ledger. |
| `tools/bazel/phase34_decision_reconciliation_integration_test.py` | Actual producer-chain regression | ✓ VERIFIED | Nine tests cover the complete approved path and eight fail-closed mutations. |
| `tools/bazel/BUILD.bazel` | Hermetic Phase 34 test and verifier targets | ✓ VERIFIED | Test target includes the boundary, core, ledger, and integration modules with required producer runfiles. |
| `tools/bazel/rust_workflow.sh` | Tests-before-publication orchestration | ✓ VERIFIED | Phase 34 dispatch runs all four test suites before the verifier. |

## Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| Phase 33 decisions | Phase 32 canonical rows | Exact `row_ref + decision_axis + decision_subject_id` | ✓ WIRED | The boundary validates the triple and reconciliation requires exactly one match. |
| Phase 34 ledger | Phase 31 evidence | Evidence-row constructor and accepted final receipts | ✓ WIRED | Phase 31 remains evidence authority; decision-domain rows do not enter the sparse evidence overlay. |
| Phase 34 ledger | Phase 32 decision domain | Pure reconciliation import | ✓ WIRED | Canonical decision rows are evaluated with Phase 33 decisions and emitted as first-class ledger rows. |
| Ledger | Final readiness packet and report | Shared evaluated row set | ✓ WIRED | The packet embeds the ledger rows and the report derives from the packet/ledger rather than an independent approval path. |
| `just phase34-verify` | Tests then publication | Bazel workflow targets | ✓ WIRED | The authoritative gate passed and preserved the expected blocked default when no maintainer decisions were supplied. |

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Phase 33 typed decision boundary | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | 40 tests passed, including all three symlink-input regressions | ✓ PASS |
| Pure exact reconciliation | `python3 tools/bazel/phase34_decision_reconciliation_test.py -q` | 18 tests passed | ✓ PASS |
| Phase 34 ledger, packet, security, and authority behavior | `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` | 40 tests passed | ✓ PASS |
| Actual Phase 31→32→33→34 producer chain | `python3 tools/bazel/phase34_decision_reconciliation_integration_test.py -q` | 9 tests passed | ✓ PASS |
| Authoritative repository gate | `just phase34-verify` | Bazel build passed; all 107 tests passed; verifier and security scans passed | ✓ PASS |

The authoritative gate's default quick fixture contains zero maintainer decisions, so its published readiness and demotion states correctly remain blocked. That is a fail-closed control, not evidence against the phase goal. The separate actual-producer integration fixture supplies complete valid decisions and proves the required unblocked readiness path.

## Fail-Closed and Authority Semantics

| Risk | Disposition | Evidence |
| --- | --- | --- |
| Forged or similar-but-not-equal target identity | Mitigated | Complete typed identity is validated and exact-matched; row, axis, subject, duplicate, and multi-match failures have stable diagnostics. |
| Lifecycle replay | Mitigated | Stale Phase 33 lifecycle IDs remain blocked in focused and integration tests. |
| Contradictory or duplicate decisions | Mitigated | Duplicate/conflicting exact bindings fail closed at the Phase 33 boundary and Phase 34 reconciliation core. |
| Hard blocker approval laundering | Mitigated | Hard-blocker problem kinds cannot be approved away; readiness approval also requires unblocked prerequisites. |
| Unsafe paths, symlink escape, or input/output overlap | Mitigated | Phase 33 rejects symlink components in the Phase 32 handoff, the canonical register it names, and maintainer decisions. Each regression exits nonzero and proves the Phase 33 output directory was never created. Phase 34 separately covers absolute paths, traversal, wrong roots, overlap, and nested symlink escapes. |
| Secret leakage or approval overclaim | Mitigated | Recursive security scans reject secret fields, unsafe refs, bearer text, and authority-overclaim markers. |
| Readiness-to-demotion authority escalation | Mitigated | Separate axes, values, projections, packet fields, and tests keep the two authorities independent. |

## Requirements Coverage

| Requirement | Source Plans | Status | Evidence |
| --- | --- | --- | --- |
| DECIDE-01 | 37-01, 37-02 | ✓ SATISFIED | Maintainers can record exact retained-code, residual-risk, exception, rejection, and owner-signed decisions; normalized targets retain exact source traceability and axis-specific semantics. |
| DECIDE-02 | 37-01, 37-02 | ✓ SATISFIED | Machine-readable readiness decisions consume canonical triaged rows and approved decisions, while missing or invalid coverage remains explicitly blocked. |
| READY-01 | 37-01, 37-02 | ✓ SATISFIED | Phase 34 generates one final packet from real Phase 31 evidence, canonical Phase 32 decision rows, Phase 33 decisions/exceptions/residual risks, blockers, and artifact references; the actual producer fixture reaches unblocked only when complete and valid. |

No Phase 37 requirement is orphaned.

## Anti-Patterns Found

| File | Size | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `tools/bazel/phase33_maintainer_decision_inputs.py` | 1,299 lines | Exceeds the Bright Builds file-size refactor trigger | ⚠ Warning | Existing boundary complexity; exact and containment validation remain covered by 40 passing tests. |
| `tools/bazel/phase34_final_readiness_demotion_dry_run.py` | 1,992 lines | Exceeds the Bright Builds file-size refactor trigger | ⚠ Warning | Existing orchestration debt; the new 381-line reconciliation core isolates the decision logic and all required behavior is wired. |
| `tools/bazel/phase34_decision_reconciliation_integration_test.py` | 504 lines | Slightly exceeds the file-size trigger | ⚠ Warning | The fixture intentionally owns a full real-producer chain; no goal-blocking stub or unwired path was found. |

No hardcoded approval, placeholder readiness result, permissive fallback match, ignored validation failure, secret-bearing output, symlink-following trusted input, or Phase 35 authority leak was found in the verified paths.

## Human Verification Required

None. Phase 37 is a deterministic command-line JSON reconciliation and publication boundary. Exact identity, real-producer data flow, invalid mutations, containment, security scanning, and authority separation are covered by automated tests and the repository-owned gate.

## Gaps Summary

No goal-blocking gaps found. Complete valid Phase 31–33 inputs now reach unblocked Phase 34 readiness, while every exercised incomplete, ambiguous, stale, malformed, invalid, unsafe, symlinked, or over-authoritative input remains blocked or rejected with specific diagnostics. The three trusted-input symlink regressions all fail before Phase 33 outputs exist. Demotion authorization stays separate and Phase 35 cutover behavior remains outside Phase 37.

***

_Verified: 2026-07-26T08:32:43Z_
_Verifier: the agent (gsd-verifier)_
