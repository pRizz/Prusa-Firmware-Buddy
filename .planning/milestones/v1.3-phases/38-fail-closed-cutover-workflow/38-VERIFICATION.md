---
phase: 38-fail-closed-cutover-workflow
verified: 2026-07-27T15:30:58Z
status: passed
score: "9/9 must-haves verified"
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 38-2026-07-26T16-29-23
generated_at: 2026-07-27T15:30:58Z
lifecycle_validated: true
overrides_applied: 0
re_verification:
  previous_status: "gaps_found"
  previous_score: "5/8"
  gaps_closed:
    - "Phase 34 blocked-replacement installation failure after prior authority moved no longer restores effective unblocked authority or permits Phase 35 approval."
    - "Phase 35 guard pre-creation failure leaves a durable workflow-attempt marker that blocks every canonical reader."
  gaps_remaining: []
  regressions: []
---

# Phase 38: Fail-Closed Cutover Workflow Verification Report

**Phase Goal:** The full Phase 31–35 workflow replaces stale authority for every upstream failure and reaches the correct blocked, approved, or targeted-repair route.
**Verified:** 2026-07-27T15:30:58Z
**Status:** passed
**Re-verification:** Yes — after Plan 38-03 gap closure and WR-01 review repair

## Goal Achievement

Phase 38 achieves its goal. The two prior stale-authority reproductions now remain durably blocked for the exact workflow attempt, all canonical readers reject stale approval, and the normal blocked, approved, targeted-repair, and independent-demotion routes remain green. WR-01 also preserves a nonzero Phase 35 and workflow status when a malformed source produces a valid blocked fallback.

The verification applied the repository guidance in `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` (no active exception), and the Bright Builds architecture, code-shape, testing, verification, and Rust standards.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Every invalid Phase 31/33 source publishes a durable blocked Phase 34 replacement or retains attempt-correlated blocking state before failure returns. | ✓ VERIFIED | `publish_publication_state` establishes a fixed-path blocking shell before fallback installation; `_phase34_effective_authority_is_valid` accepts a nonzero run only when the blocked state or installed blocked bundle matches the exact attempt and safe reason. The focused stage-rename regression and actual-producer blocked-install regression passed. |
| 2 | Workflow orchestration cannot exit while prior Phase 34 or Phase 35 approval remains authoritative. | ✓ VERIFIED | `coordinate_workflow` publishes the workflow-attempt marker before the Phase 35 guard. Phase 35 readers reject any present or unsafe marker. Both prior-gap reproductions seed approval and prove no production route or demotion authorization survives. |
| 3 | Real-producer end-to-end regressions cover default blocked, complete approved, targeted repair, and upstream-source failure paths. | ✓ VERIFIED | The 11-test Phase 38 integration suite executes actual Phase 31–35 producers and covers default blocked, complete approved, named targeted repair, invalid Phase 31, invalid Phase 33, invalid Phase 34 publication, both prior publication faults, and demotion separation. |
| 4 | Production-cutover planning requires a valid approved verdict, while demotion authority remains a separate explicit predicate. | ✓ VERIFIED | `evaluate_final_status` requires both producers to succeed and authority to be internally consistent before enabling production planning. Demotion additionally requires unblocked readiness, valid explicit approval, and an open gate. Unit and real-producer truth tables passed. |
| 5 | Failed staged installation restores a safe prior bundle or a validated blocked replacement without weakening fail-closed authority. | ✓ VERIFIED | Phase 35 publishes its guard before canonical mutation and retains it across rename, validation, restore, backup-cleanup, and guard-cleanup failures. Phase 34 retains its publication-state blocker across failed blocked-stage installation. |
| 6 | Phase 35 finalization runs after validated blocked Phase 34 publication even when Phase 34 returns nonzero, preserving the original status. | ✓ VERIFIED | Coordinator sequencing tests passed; exact-attempt Phase 34 validation gates Phase 35 consumption and the earliest nonzero status remains authoritative. |
| 7 | A durable blocking marker exists before Phase 35 guard creation and remains blocking through marker creation, replacement, parsing, path/type, and cleanup failures. | ✓ VERIFIED | Workflow-attempt marker security tests cover pre-create, atomic replace, missing fields, malformed/unreadable payloads, absolute/traversal/wrong-root refs, symlinks, wrong types, non-directory parents, and cleanup failure. The true guard pre-create reproduction passed with the Phase 35 guard absent and the workflow marker still blocking all readers. |
| 8 | The authoritative Phase 38 gate runs focused and integration regressions before default publication. | ✓ VERIFIED | `justfile` invokes `phase38_verify_tests` before `phase38_verify`; `just phase38-verify` passed 267 tests before publishing default blocked targeted-repair authority. |
| 9 | WR-01: `source-artifact-malformed` with a valid blocked fallback retains blocked authority while Phase 35 and overall workflow status stay nonzero. | ✓ VERIFIED | `test_phase35_source_failure_preserves_nonzero_status_and_blocked_authority` passed: the candidate is blocked, `phase35_status == 1`, overall `status == 1`, the reason remains `source-artifact-malformed`, and all positive authority booleans are false. |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Level 1–2 | Wiring / Data | Status |
| --- | --- | --- | --- | --- |
| `tools/bazel/phase34_final_readiness_demotion_dry_run.py` | Complete source-failure publication and attempt-correlated blocker | Exists; substantive | Called by the coordinator; writes and validates canonical Phase 34 output or retained blocking state | ✓ VERIFIED |
| `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` | Source-family and blocked-install fault regressions | Exists; substantive | Included in Phase 38 Bazel test gate | ✓ VERIFIED |
| `tools/bazel/phase35_cutover_decision_artifact.py` | Guarded publication, reader enforcement, and recovery | Exists; substantive | Called by the coordinator; canonical readers enforce both workflow marker and Phase 35 guard | ✓ VERIFIED |
| `tools/bazel/phase35_cutover_decision_artifact_test.py` | Guard, install, recovery, path, and true pre-create fault tests | Exists; substantive | Included in Phase 38 Bazel test gate | ✓ VERIFIED |
| `tools/bazel/phase38_cutover_workflow.py` | Single production coordinator and final authority reducer | Exists; substantive | Invokes actual Phase 34/35 entrypoints and is dispatched by `rust_workflow.sh` | ✓ VERIFIED |
| `tools/bazel/phase38_cutover_workflow_test.py` | Status, authority, marker, route, demotion, WR-01, and wiring tests | Exists; substantive | Included in `phase38_verify_tests`; checks Bazel, shell, root alias, and just wiring | ✓ VERIFIED |
| `tools/bazel/phase38_cutover_workflow_integration_test.py` | Actual-producer Phase 31–35 matrix | Exists; substantive | Uses actual producer callables, canonical paths, and retained artifacts | ✓ VERIFIED |
| `tools/bazel/rust_workflow.sh` | Thin coordinator dispatch with explicit status propagation | Exists; substantive | Calls `phase38_cutover_workflow.py --quick`; shell syntax passed | ✓ VERIFIED |
| `justfile` | Authoritative `phase38-verify` facade | Exists; substantive | Tests target runs before publication target | ✓ VERIFIED |

`gsd-tools verify artifacts` passed all 16 declared artifact entries across Plans 38-01, 38-02, and 38-03.

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| Phase 34 source validation | `build/ci-evidence/phase34` | Blocked staged replacement or retained publication-state blocker before nonzero return | ✓ WIRED | Exact-attempt state is created before mutation and checked by coordinator/security readers. |
| Phase 35 publication | `build/ci-evidence/phase35` | Guarded staged installation and canonical-reader enforcement | ✓ WIRED | Guard precedes mutation; installed output is validated before protection clears. |
| `tools/bazel/phase38_cutover_workflow.py` | Phase 35 canonical readers | Workflow-attempt marker publication and marker rejection | ✓ WIRED | `publish_workflow_attempt_marker` precedes guard creation; `ensure_no_workflow_attempt_marker` protects Phase 35 readers. |
| Phase 34 failed run | Phase 38 coordinator | Exact attempt, blocked state, and safe-reason correlation | ✓ WIRED | `_phase34_effective_authority_is_valid` rejects stale attempts, reason mismatch, and unguarded restored authority. |
| Phase 38 coordinator | Phase 35 failed-run finalization | Validated persisted blocked Phase 34 authority | ✓ WIRED | Phase 35 cannot consume a nonzero Phase 34 run until effective authority is blocked for that attempt. |
| `tools/bazel/rust_workflow.sh` | Phase 38 coordinator | One explicit coordinator invocation with captured status | ✓ WIRED | Shell wiring assertions and `bash -n` passed. |
| Phase 38 integration suite | Actual Phase 31–35 producers | Real producer outputs and canonical publication paths | ✓ WIRED | Default, approved, targeted-repair, upstream-failure, publication-fault, and demotion cases passed. |

`gsd-tools verify key-links` passed all 7 declared links across the three plans.

### Data-Flow Trace

| Artifact | Data | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| Phase 34 readiness authority | Evidence rows, decisions, blocker register, demotion handoff, attempt correlation | Actual Phase 31–33 producer outputs | Yes | ✓ FLOWING |
| Phase 34 failure authority | Blocked state, safe reason, lifecycle, canonical ref, opaque attempt ID | Source-validation boundary before canonical replacement | Yes; private revocation metadata only | ✓ FLOWING |
| Phase 35 cutover decision and route | Validated canonical Phase 34 packet/ledger/demotion state | Actual Phase 34 output or correlated failed-run finalization | Yes | ✓ FLOWING |
| Workflow-attempt blocker | Blocked lifecycle-bound attempt state | Coordinator before Phase 35 guard creation | Yes; enforced by all canonical readers | ✓ FLOWING |
| Phase 38 workflow result | Producer statuses plus validated Phase 35 authority | Actual producer calls and canonical bundles | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Two prior gaps plus WR-01 | Six exact `python3 -m unittest ...` cases | 6 passed in 1.130s | ✓ PASS |
| Authoritative Phase 38 gate | `just phase38-verify` | 267 tests passed; default published blocked/targeted repair, production planning false, demotion false | ✓ PASS |
| Python module validity | `python3 -m py_compile` on all seven Phase 38 Python implementation/test files | Exit 0 | ✓ PASS |
| Shell dispatch syntax | `bash -n tools/bazel/rust_workflow.sh` | Exit 0 | ✓ PASS |
| Rust formatting | `cargo fmt --all` | Exit 0; no source changes | ✓ PASS |
| Rust lint | `cargo clippy --all-targets --all-features -- -D warnings` | Exit 0 | ✓ PASS |
| Rust build | `cargo build --all-targets --all-features` | Exit 0 | ✓ PASS |
| Rust tests | `cargo test --all-features` | 136 unit tests and 4 doc-test suites passed | ✓ PASS |
| Diff integrity | `git diff --check` | Exit 0 | ✓ PASS |

Bazel rewrote `MODULE.bazel.lock` from format 26 to 28 and added `factsVersions`; only that incidental generated change was restored. Its SHA-256 returned to `21587df8a47a42952e5301f59f4809b23eba5f336780847d0c3bc02422275a03`.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| READY-02 | 38-01, 38-02, 38-03 | Readiness stays blocked for absent, failed, stale, malformed, redaction-failed, underclassified, or uncovered evidence. | ✓ SATISFIED | Source families and malformed/read-error cases publish blocked authority; failed blocked installation retains exact-attempt blocking state and cannot revive unblocked readiness. |
| READY-03 | 38-01, 38-02, 38-03 | Demotion remains blocked without valid explicit approval and opens only with otherwise unblocked readiness. | ✓ SATISFIED | Unit and real-producer cases cover missing/rejected demotion, valid demotion with blocked readiness, and the sole valid open predicate. |
| CUTOVER-01 | 38-01, 38-02, 38-03 | Produce one explicit approved, blocked, or approved-with-exceptions verdict. | ✓ SATISFIED | Phase 35 contract and reducer enforce the closed verdict vocabulary; WR-01 proves malformed source failure remains nonzero while retaining blocked candidate authority. |
| CUTOVER-03 | 38-01, 38-02, 38-03 | Approved routes to production planning; blocked/follow-up exceptions route to targeted repair. | ✓ SATISFIED | Actual-producer approved, default blocked, and named targeted-repair cases pass; both stale-authority fault reproductions deny production planning. |

No requirement is orphaned. All three plans claim all four Phase 38 requirements, and REQUIREMENTS.md maps exactly these IDs to Phase 38. Their checklist fields remain pending by design because Phase 39 owns milestone metadata reconciliation; this is not an implementation gap.

### Threat Mitigation Assessment

| Threat | Status | Evidence |
| --- | --- | --- |
| T-38-01 stale approval replay | ✓ MITIGATED | Both seeded-approval publication-fault reproductions pass through focused and actual-producer paths. |
| T-38-02 guard bypass | ✓ MITIGATED | A true Phase 35 guard pre-create failure leaves the earlier workflow marker blocking every reader. |
| T-38-03 path/symlink substitution | ✓ MITIGATED | Both private marker surfaces have absolute, traversal, wrong-root, symlink, wrong-type, unreadable, malformed, and non-directory coverage. |
| T-38-04 partial publication/rollback failure | ✓ MITIGATED | Blocking shells precede payloads; Phase 34 state persists through failed staged installation; Phase 35 guard persists through recovery faults. |
| T-38-05 diagnostic leakage | ✓ MITIGATED | Marker payloads are limited to lifecycle, opaque attempt ID, blocked state, fixed ref, and safe reason; focused tests reject malformed/unsafe values. |

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
| --- | --- | --- | --- |
| Phase 34/35 implementation and test modules | Several files exceed the Bright Builds 628-line refactor trigger | ℹ INFO | These are pre-existing large verification surfaces. Phase 38 kept changes scoped and used focused helpers/tests; no goal-blocking defect was found. |
| Phase-owned files | TODO/FIXME/stub scan | ✓ NONE | `non_final_placeholder` is a domain classification. `return []` is a validated malformed-reference error path that records `route-scope-incomplete`, not a stub. |

### Disconfirmation Pass

- **Potential partial requirement:** CUTOVER-01 could have been only vocabulary-complete while malformed Phase 35 source handling incorrectly returned success. WR-01 directly disproves that failure mode: blocked authority remains while both statuses are nonzero.
- **Previously misleading test:** The earlier Phase 35 “creation interruption” test created the guard before raising. The replacement true pre-create tests assert the guard is absent and the earlier workflow marker blocks `ensure_canonical_authority`, `run_security_scan`, and `load_final_authority`.
- **Previously uncovered error path:** Phase 34 blocked-stage rename failure after moving prior authority is now covered in focused and actual-producer tests and retains exact-attempt blocked publication state.

### Human Verification Required

None. Phase 38 consists of deterministic CLI, filesystem, JSON, Markdown, Bazel, shell, and Rust behavior that was verified programmatically.

### Deferred-Item Check

Phase 39 only reconciles milestone requirement and roadmap metadata. It does not own any remaining Phase 38 authority, publication, routing, or guard behavior. No implementation gap was deferred.

### Gaps Summary

No gaps remain. The previous two root gaps are closed without overrides, no regressions were detected in the five previously passing truths, and WR-01 is verified.

***

_Verified: 2026-07-27T15:30:58Z_
_Verifier: the agent (gsd-verifier)_
