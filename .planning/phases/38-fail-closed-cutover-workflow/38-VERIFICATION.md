---
phase: 38-fail-closed-cutover-workflow
verified: 2026-07-26T18:49:11Z
status: gaps_found
score: "5/8 must-haves verified"
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 38-2026-07-26T16-29-23
generated_at: 2026-07-26T18:49:11Z
lifecycle_validated: true
overrides_applied: 0
gaps:
  - truth: "Every invalid Phase 31 or Phase 33 source causes Phase 34 to publish a durable blocked replacement before returning failure."
    status: failed
    reason: "A Phase 34 blocked-bundle staging rename failure restores the prior unblocked bundle. The coordinator then accepts that restored bundle as valid, Phase 35 republishes approved production-cutover authority, clears the guard, and returns nonzero with stale canonical approval still readable."
    artifacts:
      - path: "tools/bazel/phase34_final_readiness_demotion_dry_run.py"
        issue: "replace_output_with_staging restores the prior canonical bundle when the staged rename fails, without a durable Phase 34 blocking guard."
      - path: "tools/bazel/phase38_cutover_workflow.py"
        issue: "_phase34_authority_is_valid accepts the restored prior unblocked bundle after _run_phase34 reports failure, so Phase 35 runs against stale authority and can clear the Phase 35 guard."
      - path: "tools/bazel/phase38_cutover_workflow_integration_test.py"
        issue: "The matrix covers invalid sources and an invalid Phase 34 output path, but not a failure while installing the blocked Phase 34 replacement."
    missing:
      - "Make Phase 34 fallback publication authority-monotonic across staging rename, validation, rollback, and cleanup failures."
      - "After a nonzero Phase 34 result, require the persisted Phase 34 authority itself to be blocked before Phase 35 may finalize or clear its guard."
      - "Add a seeded approved real-producer regression that injects Phase 34 blocked-bundle installation failure and proves both canonical authorities remain blocked."
  - truth: "Workflow orchestration cannot exit while leaving prior Phase 34 or Phase 35 approval authoritative."
    status: failed
    reason: "If Phase 35 guard creation fails before the guard file exists, the coordinator returns nonzero but no durable blocking marker exists; ensure_canonical_authority accepts the untouched prior canonical bundle."
    artifacts:
      - path: "tools/bazel/phase35_cutover_decision_artifact.py"
        issue: "publish_authority_guard catches a pre-create touch failure, but cannot make absent guard state blocking for canonical readers."
      - path: "tools/bazel/phase35_cutover_decision_artifact_test.py"
        issue: "The guard-creation interruption test creates the guard before raising and therefore does not cover failure before guard-file creation."
      - path: "tools/bazel/phase38_cutover_workflow_test.py"
        issue: "The coordinator guard-publication-failure test asserts only returned status and skipped producers; it does not seed prior approval or prove canonical readers are blocked."
    missing:
      - "Give Phase 35 readers a durable fail-closed state that also covers guard publication failure before file creation."
      - "Seed prior approved Phase 35 authority and inject a pre-create guard failure; prove every canonical reader rejects the prior bundle."
      - "Do not report finalization complete solely through the transient coordinator result when persisted authority remains readable."
---

# Phase 38: Fail-Closed Cutover Workflow Verification Report

**Phase Goal:** The full Phase 31–35 workflow replaces stale authority for every upstream failure and reaches the correct blocked, approved, or targeted-repair route.
**Verified:** 2026-07-26T18:49:11Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

The normal-path implementation and authoritative gate are substantial, wired, and well tested. Default blocked, complete approved, targeted-repair, invalid Phase 31, and invalid Phase 33 cases all pass. However, adversarial publication-failure checks show that the durable authority invariant is not complete: stale approval can become readable after the workflow returns nonzero.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Every invalid Phase 31/33 source publishes a durable blocked Phase 34 replacement before failure returns. | ✗ FAILED | Normal invalid-source regressions pass, but injected failure of the Phase 34 blocked-bundle staging rename returned status 1 while restoring `readiness_state: unblocked`. |
| 2 | Workflow orchestration cannot exit while prior Phase 34 or Phase 35 approval remains authoritative. | ✗ FAILED | After the Phase 34 install fault, Phase 35 was `approved`, route was `production-cutover-planning`, the guard was absent, and `load_final_authority` returned `available: true`. A separate pre-create guard failure left `guard_exists: false` and the canonical reader unblocked. |
| 3 | Real-producer end-to-end regressions cover default blocked, complete approved, targeted repair, and upstream-source failure paths. | ✓ VERIFIED | `phase38_cutover_workflow_integration_test.py` ran 9 tests through actual Phase 31–35 producers; required route cases passed. |
| 4 | Production-cutover planning requires a valid approved verdict, while demotion authority remains a separate explicit predicate. | ✓ VERIFIED | `evaluate_final_status` gates both positive projections on successful producers and consistent authority; focused route/demotion tests and real-producer cases passed. |
| 5 | Failed Phase 35 staged installation restores a prior bundle or retains a validated replacement without weakening authority. | ✓ VERIFIED | Focused stage-rename, validation, restore, backup-cleanup, and guard-cleanup tests passed; all post-guard faults retain a blocking guard. |
| 6 | Phase 35 finalization runs after a validated blocked Phase 34 publication even when Phase 34 returns nonzero, preserving the original status. | ✓ VERIFIED | Coordinator call-order test passed and `evaluate_final_status` preserved the Phase 34 status after blocked Phase 35 finalization. |
| 7 | A durable Phase 35 guard is blocking before canonical mutation and through publication/recovery faults. | ✗ FAILED | It is blocking once created, but injected failure before `touch_guard` creates the file leaves no durable guard and canonical readers accept prior authority. |
| 8 | The authoritative Phase 38 gate runs focused and integration regressions before default publication. | ✓ VERIFIED | `justfile` orders `phase38_verify_tests` before `phase38_verify`; the authoritative command passed and then published default blocked targeted-repair output. |

**Score:** 5/8 truths verified

## Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `tools/bazel/phase34_final_readiness_demotion_dry_run.py` | Complete Phase 31/33 source-failure publication boundary | ⚠ PARTIAL | Exists, substantive, and wired. Normal source failures publish exact blocked bundles, but fallback-install failure can restore stale unblocked authority. |
| `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` | Seeded stale-approval regressions for every source boundary | ⚠ PARTIAL | 53 tests pass, including invalid UTF-8 and read errors. No blocked-bundle rename/rollback fault regression exists. |
| `tools/bazel/phase35_cutover_decision_artifact.py` | Guarded staged installation and compensating restore | ⚠ PARTIAL | Guarded mutation/recovery works after guard creation. A failure before guard creation leaves absent guard state non-blocking. |
| `tools/bazel/phase35_cutover_decision_artifact_test.py` | Guard, rename, validation, restore, cleanup, and path-substitution fault tests | ⚠ PARTIAL | 74 tests pass. The “creation interruption” fixture touches the guard before raising, so it does not cover a true pre-create failure. |
| `tools/bazel/phase38_cutover_workflow.py` | Production coordinator and final authority truth table | ⚠ PARTIAL | Pure status logic and normal orchestration are substantive. It can finalize Phase 35 from a restored stale Phase 34 bundle after a Phase 34 publication failure. |
| `tools/bazel/phase38_cutover_workflow_test.py` | Coordinator status, authority, route, and demotion regressions | ⚠ PARTIAL | 30 tests pass. Guard-publication failure is not checked against seeded canonical approval. |
| `tools/bazel/phase38_cutover_workflow_integration_test.py` | Actual-producer Phase 31–35 route matrix | ⚠ PARTIAL | Required 9-case matrix passes, but no fallback-publication fault case proves authority monotonicity. |
| `tools/bazel/rust_workflow.sh` | Thin coordinator dispatch with explicit status propagation | ✓ VERIFIED | `phase35_verify` and `phase38_verify` call one status-preserving coordinator. |
| `justfile` | Authoritative `phase38-verify` facade | ✓ VERIFIED | Tests run before publication. |

## Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| Phase 34 source validation | `build/ci-evidence/phase34` | Staged blocked source-failure bundle before nonzero return | ⚠ PARTIAL | Normal-path source failures are validated before return; staged rename failure restores stale authority. |
| Phase 35 publication | Adjacent authority guard and canonical Phase 35 output | Guard before rename, validation before guard clear | ⚠ PARTIAL | The link is sound after guard creation; a pre-create I/O failure leaves no blocking state. |
| `tools/bazel/rust_workflow.sh` | `tools/bazel/phase38_cutover_workflow.py` | Single coordinator invocation and explicit return status | ✓ WIRED | Shell dispatcher is thin and status-preserving. |
| Phase 38 integration suite | Actual Phase 31, 32, 33, 34, and 35 producers | Real retained artifacts and canonical publication paths | ✓ WIRED | Real-producer baseline and one-concern mutations execute actual producer entrypoints. |

## Data-Flow Trace

| Artifact | Data | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| Phase 34 readiness packet | Evidence/decision ledger and demotion projection | Actual Phase 31/32/33 outputs | Yes | ✓ FLOWING on normal/default/invalid-source paths |
| Phase 35 cutover decision and route | Phase 34 canonical packet, ledger, blockers, and decision refs | Actual Phase 34 output | Yes | ✓ FLOWING on normal paths; ⚠ stale restored data can flow after Phase 34 publication failure |
| Phase 38 workflow result | Phase 34/35 statuses plus canonical Phase 35 authority | Actual producer calls and canonical bundles | Yes | ⚠ Result booleans fail closed, but persisted stale canonical approval can remain readable |
| Phase 35 authority guard | Contract-defined blocking payload | Coordinator/Phase 35 publication boundary | Yes after file creation | ✗ DISCONNECTED when file creation fails before the guard exists |

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Authoritative Phase 38 gate | `just phase38-verify` | 233 focused/integration tests passed; default output was blocked, targeted repair, no production planning, no demotion authority | ✓ PASS |
| Prior CR-01: invalid UTF-8/read errors publish blocked Phase 34 authority | Four focused Phase 34 tests | 4 passed | ✓ PASS |
| Prior CR-02: nonzero producer results revoke positive coordinator authority | Two focused final-status tests | 2 passed | ✓ PASS |
| Prior CR-03: invalid Phase 34 authority is covered by a Phase 35 guard | Focused real-producer integration test | 1 passed | ✓ PASS |
| Phase 35 guarded recovery and path substitution | Eight focused guard/restore/cleanup/path tests | 8 passed | ✓ PASS |
| Pre-create Phase 35 guard failure | Inject `touch_guard` failure before file creation in a temp root | `publication_failed=True guard_exists=False canonical_reader_blocked=False` | ✗ FAIL |
| Phase 34 blocked-bundle install failure from seeded approved real producers | Inject staging rename failure during invalid Phase 31 handling | `status=1 phase34_readiness=unblocked phase35_verdict=approved route=production-cutover-planning guard_exists=False reader_available=True` | ✗ FAIL |
| Rust verification | `cargo fmt --all -- --check`, clippy, build, test | All passed; 136 unit tests and doc tests passed | ✓ PASS |

## Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| READY-02 | 38-01, 38-02 | Readiness remains blocked for absent, failed, stale, malformed, redaction-failed, underclassified, or uncovered evidence. | ✗ BLOCKED | Normal cases pass, but invalid Phase 31 plus Phase 34 fallback-install failure leaves prior unblocked readiness canonical. |
| READY-03 | 38-01, 38-02 | Demotion stays blocked without valid explicit approval and opens only with otherwise unblocked readiness. | ✓ SATISFIED | Focused truth table and real-producer missing/rejected/blocked-readiness cases pass. |
| CUTOVER-01 | 38-01, 38-02 | Produce one explicit approved, blocked, or approved-with-exceptions verdict. | ✓ SATISFIED | Phase 35 contract and decision evaluator enforce the explicit verdict vocabulary. |
| CUTOVER-03 | 38-01, 38-02 | Approved routes to production planning; blocked/follow-up exceptions route to targeted repair. | ✗ BLOCKED | Normal routing is correct, but the Phase 34 publication fault leaves an approved production route readable after an invalid upstream source. |

No Phase 38 requirement is orphaned: both PLAN files claim READY-02, READY-03, CUTOVER-01, and CUTOVER-03, and REQUIREMENTS.md maps exactly those IDs to Phase 38.

## Threat Mitigation Assessment

| Threat | Status | Evidence |
| --- | --- | --- |
| T-38-01 stale approval replay | ✗ UNRESOLVED | Phase 34 fallback-install failure can restore and republish stale approved authority. |
| T-38-02 guard bypass | ✗ UNRESOLVED | Guard creation failure before the file exists leaves canonical readers unblocked. |
| T-38-03 path/symlink substitution | ✓ MITIGATED | Absolute, traversal, symlink, wrong-root, and non-directory substitutions pass for guard, stage, backup, and canonical targets. |
| T-38-04 partial publication/rollback failure | ✗ UNRESOLVED | Phase 35 guarded recovery is covered, but Phase 34 blocked-publication rollback is not authority-monotonic. |
| T-38-05 diagnostic leakage | ✓ MITIGATED | Safe reason vocabularies, security scans, and blocked-bundle payload checks pass. |

The PLAN contract requires no unresolved high-severity threat. T-38-01, T-38-02, and T-38-04 therefore block goal achievement.

## Anti-Patterns Found

| File | Line/Pattern | Severity | Impact |
| --- | --- | --- | --- |
| Phase 34/35 implementation files | Files exceed the 628-line Bright Builds refactor trigger | ℹ INFO | Pre-existing large verifier surfaces remain difficult to audit; the phase explicitly deferred broad cleanup. This is not the goal blocker. |
| Phase-owned files | TODO/FIXME/stub scan | ✓ NONE | `non_final_placeholder` is a domain classification, and the single `return []` is a validated empty-result error path, not a stub. |

## Human Verification Required

None. All Phase 38 behaviors are deterministic CLI, filesystem, JSON, and Markdown flows and were programmatically testable.

## Deferred-Item Check

The only later milestone phase is Phase 39, whose goal is metadata reconciliation. It does not address publication atomicity, authority guards, staged rollback, or stale approval. Neither gap is deferred.

## Gaps Summary

The normal-path work is strong and the three prior critical review findings are closed for their covered cases. The remaining root problem is broader: publication failure itself is not represented as durable blocked authority.

Phase 34 has no guard around blocked-replacement installation, so rollback can restore stale unblocked data. Phase 38 then mistakes that restored bundle for a valid outcome and lets Phase 35 republish approved authority. Separately, Phase 35 assumes guard presence can encode the failure state, but a failure before guard creation leaves absent-guard readers trusting prior canonical data. Both paths return nonzero while persisted stale authority remains readable, contradicting the phase goal.

***

_Verified: 2026-07-26T18:49:11Z_
_Verifier: the agent (gsd-verifier)_
