---
phase: 36-normalize-evidence-and-blocker-rows
verified: 2026-07-26T03:36:24Z
status: passed
score: 14/14 must-haves verified
generated_by: gsd-verify-phase
lifecycle_mode: yolo
phase_lifecycle_id: 36-2026-07-26T00-27-52
generated_at: 2026-07-26T03:36:24Z
lifecycle_validated: true
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 6/7
  gaps_closed:
    - "Recognized malformed Phase 27/28 containers now publish visible critical proof-ineligible malformed canonical blocker rows, while unsupported envelopes publish critical unknown_unclassified rows and Phase 32 still publishes its complete bundle."
  gaps_remaining: []
  regressions: []
---

# Phase 36: Normalize Evidence and Blocker Rows Verification Report

**Phase Goal:** Phase 32 consumes the actual Phase 26 release row-table shape and emits canonical resolvable identities for Phase 27/28 decision-domain rows.
**Verified:** 2026-07-26T03:36:24Z
**Status:** passed
**Re-verification:** Yes — after gap closure
**Verified revision:** `a363d345c94ca1ce4596402919cc74e4f31f109e`

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | An accepted all-passed Phase 26 release row table remains eligible through Phase 31 into Phase 32. | ✓ VERIFIED | The real Phase 26 and Phase 31 producers run in `test_all_passed_phase26_table_crosses_phase31_without_release_blocker`; Phase 32 exits zero and emits no `release_signing` blocker. The generated full-gate register also had zero release blockers. |
| 2 | Phase 32 preserves stable source-domain and decision-resolution identities for retained-code, residual-risk, exception, readiness, and demotion rows. | ✓ VERIFIED | `canonical_row_id` hashes only the exact five-field source tuple; decision axis/subject remain separate. Focused identity tests and the real-producer test observe all five decision axes. |
| 3 | Unknown or malformed table and row shapes fail closed without collapsing a valid Phase 26 table into `unknown_unclassified`. | ✓ VERIFIED | The Phase 26 adapter validates atomically; Phase 27/28 container and row adapters publish critical `malformed` or `unknown_unclassified` rows. The valid all-passed table produces no false release blocker. |
| 4 | Focused regressions exercise actual Phase 26, Phase 27, and Phase 28 producer output shapes. | ✓ VERIFIED | `generate_producer_fixture` invokes the real Phase 26, 27, 28, and 31 production modules before Phase 32 consumes their outputs. |
| 5 | A recognized malformed Phase 26 table fails atomically as one critical proof-ineligible blocker. | ✓ VERIFIED | Seventeen normalization tests cover malformed/unsupported Phase 26 shapes; the producer-boundary malformed-table test confirms exactly one critical release blocker and no partial eligible subset. |
| 6 | Unknown Phase 26/27/28 envelopes, row kinds, statuses, and demotion values remain visible critical blockers. | ✓ VERIFIED | Producer tests cover unsupported Phase 26 envelopes/statuses, Phase 27/28 container envelopes, Phase 27 residual kinds, Phase 28 readiness statuses, and both demotion records. All remain critical and visible. |
| 7 | Decision-domain identities cannot collide or resolve by path, prefix, stream, or gate similarity. | ✓ VERIFIED | Contract policy requires exact canonical row refs plus exact decision axis/subject. Duplicate tuples, duplicate IDs, and incompatible remappings are rejected; physical path and mutable classification data are excluded from `row_id`. |
| 8 | Every recognized malformed Phase 27/28 required container publishes exactly one critical proof-ineligible `malformed` canonical blocker instead of aborting. | ✓ VERIFIED | Four real-producer tests cover missing, mistyped, and non-object-member collections across all four call sites; each command exits zero and asserts one mapped canonical row. Atomic Phase 28 residual rejection emits no ordinary subset rows. |
| 9 | Every unsupported Phase 27/28 envelope publishes exactly one critical proof-ineligible `unknown_unclassified` canonical blocker instead of aborting. | ✓ VERIFIED | Four real-producer tests cover non-object top levels and explicit incompatible discriminators across all four call sites; each publishes one exact mapped unknown row. |
| 10 | All four legitimate empty Phase 27/28 collections remain valid. | ✓ VERIFIED | Four one-concern tests set Phase 27 residual/exception and Phase 28 blocker/residual collections empty; each exits zero, publishes the complete bundle, and emits neither a container row nor an ordinary row for that empty artifact. |
| 11 | Container failures still publish the canonical register, all derived views, handoff, and redacted report. | ✓ VERIFIED | `assert_phase32_bundle` requires the register, three views, handoff, and report for every gap test and verifies handoff count/IDs against the register. |
| 12 | All four adapter call sites and accepted nested Phase 27/28 output directories work without changing canonical semantics. | ✓ VERIFIED | The same mapping-backed loader is called for both Phase 27 artifacts and both Phase 28 artifacts. Nested-bundle tests preserve every canonical field except physical provenance refs; containment probes accept descendants and reject sibling, traversal, and absolute paths. |
| 13 | Valid row/status/demotion behavior and every code-review correction remain closed. | ✓ VERIFIED | The 39-test Phase 32 suite covers exact Phase 26 receipt provenance, same-basename rejection, critical malformed policy, unknown severity preservation, unknown demotion visibility, container publication, and nested directory semantics. Active `36-REVIEW.md` is clean. |
| 14 | Containment, secret-safety, provenance, and authority boundaries remain intact. | ✓ VERIFIED | `path_under` and `repo_relative_path` preserve scoped roots; exact receipt provenance gates Phase 26 adaptation; recursive output security scan passes; every generated row is ineligible; report and handoff explicitly grant no approval, readiness, demotion, or cutover authority. |

**Score:** 14/14 truths verified

## Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` | Canonical identity, producer adapter, fail-closed, and output policy | ✓ VERIFIED | Valid JSON; requires all canonical fields, exact five-field row identity, exact decision pair, critical malformed/unknown policies, and the complete output artifact set. |
| `tools/bazel/phase32_blocker_normalization.py` | Pure Phase 26 adapter and canonical identity core | ✓ VERIFIED | Substantive 281-line pure core; table validation is atomic and source-only IDs are deterministic and collision checked. |
| `tools/bazel/phase32_blocker_normalization_test.py` | Focused adapter and identity regressions | ✓ VERIFIED | Seventeen tests pass, including atomic table failures, unsupported shapes/statuses, identity stability, duplicates, and incompatible remapping. |
| `tools/bazel/phase32_blocker_register_triage.py` | Phase 31/26 and Phase 27/28 integration shell | ✓ VERIFIED | All producer adapters are wired; four container call sites use the mapping-backed helper; register validation, views, handoff, report, containment, and security scan execute before success. |
| `tools/bazel/phase32_blocker_register_triage_test.py` | Real-producer and output-publication regressions | ✓ VERIFIED | Thirty-nine tests pass, including 22 focused producer boundary/review cases, all four empty collections, and nested Phase 27/28 bundles. |
| `tools/bazel/BUILD.bazel` | Hermetic producer/test runfiles | ✓ VERIFIED | Bazel Phase 32 test/verifier targets include the normalization module/tests and exact Phase 26/27/28/31 producer dependencies. |
| `tools/bazel/rust_workflow.sh` | Tests-before-verifier Phase 32 workflow | ✓ VERIFIED | Shell syntax passes and the Phase 32 test case runs normalization before integration tests. |

## Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| Phase 31 accepted receipt | Phase 26 table | Exact receipt provenance and contracted table path | ✓ WIRED | Requires `accepted-final`, release stream, passed redaction/source refs, exact sole consumed ref, and validator-output inclusion. |
| Phase 32 shell | Normalization core | Imported source/decision identity and table adapter functions | ✓ WIRED | Canonical source identity, row ID, decision identity, binding validation, and Phase 26 adaptation are all invoked. |
| Four Phase 27/28 producer containers | Canonical blocker register | `load_phase27_28_container` with fixed logical adapter key plus validated physical path | ✓ WIRED | All four call sites use the same atomic helper; nested physical paths retain provenance without becoming identity inputs. |
| Canonical register | Derived views and handoff | Exact canonical `row_id` projection | ✓ WIRED | Derived rows are checked against register IDs; handoff count and identity count match the register. |
| `just phase32-verify` | Bazel tests and verifier | Tests-before-verifier recipes | ✓ WIRED | The repo-native gate ran both test modules, then generated and security-scanned the Phase 32 bundle. |

## Data-Flow Trace (Level 4)

| Artifact | Data | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| Phase 26 adapter | Nine release/signing criteria | Real Phase 26 producer → real Phase 31 accepted receipt → exact table ref | Yes | ✓ FLOWING |
| Phase 27 adapters | Retained-code, residual-risk, exception, readiness, and demotion identities | Real Phase 27 producer files, including nested-root variant | Yes | ✓ FLOWING |
| Phase 28 adapters | Readiness, residual-risk, and demotion identities | Real Phase 28 producer files, including nested-root variant | Yes | ✓ FLOWING |
| Container problem path | One atomic mapped blocker | Recognized malformed or unsupported producer container | Yes | ✓ FLOWING |
| Phase 32 handoff | Canonical identity projection | Validated register | Yes; generated 43 rows, 43 unique IDs, and 43 handoff identities | ✓ FLOWING |

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Focused Phase 32 core and integration | Direct normalization and Phase 32 Python suites | 17 + 39 tests passed | ✓ PASS |
| Actual producer/intake compatibility | Direct Phase 26, 27, 28, and 31 suites | 31 + 27 + 28 + 20 tests passed; 162 direct tests total with Phase 32 | ✓ PASS |
| Gap and review regression subset | 22 named `Phase32ProducerShapeTest` cases | 22/22 passed | ✓ PASS |
| Contract, wiring, shell, and security | `--contract-only`, `--wiring-only`, `bash -n`, `--security-only` | All passed | ✓ PASS |
| Hermetic Bazel tests | `bazel run //tools/bazel:phase32_verify_tests` | 17 + 39 tests passed | ✓ PASS |
| Hermetic verifier and repo-native gate | `bazel run //tools/bazel:phase32_verify`; `just phase32-verify` | Both passed; each wrote 43 blockers after upstream quick validation | ✓ PASS |
| Generated bundle integrity | JSON/report inspection | 43 rows, 43 unique IDs, 43 handoff identities, all ineligible, zero release blockers, explicit no-authority disclaimer | ✓ PASS |
| Root Rust regression gate | `cargo fmt --all -- --check`; clippy; build; test | Format, clippy, build passed; 136 tests plus doc tests passed | ✓ PASS |
| Commit and diff integrity | `verify commits`; `git diff --check 71c28444f^..HEAD` | All 10 Phase 36 commits valid; diff check passed | ✓ PASS |

## Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| INTAKE-04 | 36-01 | Secret-safe final release/signing/provenance evidence can cross intake and triage | ✓ SATISFIED | Real Phase 26 output crosses real Phase 31 accepted-final validation by exact provenance; all-passed input creates no release blocker; recursive output security scan passes. |
| TRIAGE-01 | 36-01, 36-02 | All consumed evidence and decision-domain rows aggregate into one register | ✓ SATISFIED | Valid producer rows, malformed/unsupported container rows, unknown row/status/demotion rows, and nested-root rows all reach the canonical register and handoff. |
| TRIAGE-02 | 36-01, 36-02 | Every problematic row has owner, severity, gate, next action, and decision impact | ✓ SATISFIED | Register validation requires each field; all malformed/unknown tests assert critical severity, explicit owner/action/gate/impact, proof ineligibility, and exact identity. |

No Phase 36 requirements are orphaned.

## Anti-Patterns Found

| File | Line/Size | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `tools/bazel/phase32_blocker_register_triage.py` | 1,960 lines | Exceeds the Bright Builds file-size refactor trigger | ⚠ Warning | Existing technical debt; the new pure normalization core and shared container helper limit further duplication. No goal-blocking stub or unwired path found. |
| `tools/bazel/phase32_blocker_register_triage_test.py` | 1,812 lines | Exceeds the test-file refactor trigger | ⚠ Warning | Existing inventory cost; all required behaviors are nevertheless explicit and runnable. |

No TODO/FIXME implementation, placeholder output, empty handler, hardcoded approval, ignored response, secret-bearing output, or orphaned Phase 36 artifact was found. Matches for “placeholder” are intentional fail-closed taxonomy and tests. Empty collections are typed accumulators or explicit valid/negative test inputs.

## Human Verification Required

None. Phase 36 is a deterministic command-line JSON normalization/publication boundary, and all observable behavior is covered by automated real-producer fixtures, containment checks, security scans, and generated-artifact inspection.

## Gaps Summary

The previous gap is closed. Recognized malformed Phase 27/28 containers no longer abort before publication: all four call sites emit one critical proof-ineligible `malformed` row. Unsupported envelopes emit one critical `unknown_unclassified` row. Legitimate empty collections remain valid, nested output roots preserve canonical semantics, and every fail-closed case publishes the register, views, handoff, and report.

The disconfirmation pass found no blocking regression. The default 43-row `just phase32-verify` output does not by itself exercise the exception axis or malformed containers, so it is not treated as sufficient evidence; the separate real-producer regression matrix supplies those checks. Invalid JSON, unsafe path, identity-collision, security-scan, and output-write failures intentionally remain hard failures rather than ordinary blocker rows.

***

_Verified: 2026-07-26T03:36:24Z_
_Verifier: the agent (gsd-verifier)_
