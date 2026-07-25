---
phase: 35-cutover-decision-artifact
verified: 2026-07-25T23:22:09Z
status: gaps_found
score: 4/5 must-haves verified
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 35-2026-07-25T21-06-10
generated_at: 2026-07-25T23:22:09Z
lifecycle_validated: true
overrides_applied: 0
gaps:
  - truth: "Maintainer can generate exactly one cutover verdict from the closed enum approved, blocked, or approved-with-exceptions, and every invalid or incomplete input fails to blocked."
    status: partial
    reason: "The reducer and valid-input generator are closed and deterministic, but a malformed or missing source artifact raises before Phase 35 replaces existing output. A stale approved decision can therefore survive a failed regeneration instead of being replaced by a minimal blocked decision and targeted-repair route."
    artifacts:
      - path: "tools/bazel/phase35_cutover_decision_artifact.py"
        issue: "run_quick loads and validates the Phase 34 bundle before write_bundle resets output; main catches VerificationError and returns nonzero without invalidating stale output or writing the PLAN-required minimal blocked manifest/decision/route."
      - path: "tools/bazel/phase35_cutover_decision_artifact_test.py"
        issue: "Lifecycle/contract drift tests assert only that validation raises; no regression proves malformed or missing sources replace a prior approved artifact with durable blocked output."
    missing:
      - "Invalidate stale Phase 35 outputs before consuming untrusted Phase 34 inputs, or atomically replace them with a minimal blocked manifest, cutover decision, and targeted-blocker-repair route on every source-validation failure."
      - "Add an end-to-end regression starting with a prior approved output and a malformed, missing, stale, lifecycle-mismatched, secret-tainted, or unsafe source; assert the command is nonzero and no approved artifact remains authoritative."
---

# Phase 35: Cutover Decision Artifact Verification Report

**Phase Goal:** Maintainers can produce an auditable go/no-go cutover artifact that routes the project to production cutover or targeted blocker repair.
**Verified:** 2026-07-25T23:22:09Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

The four roadmap success criteria and five plan truths merge into five distinct observable truths.

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Maintainer can generate exactly one closed-enum cutover verdict, and every invalid or incomplete input fails to a durable blocked artifact. | ✗ FAILED | `evaluate_verdict` is closed and fail-closed, and valid blocked input generates one blocked artifact. However, `run_quick` loads the Phase 34 bundle before `write_bundle` resets output (`phase35_cutover_decision_artifact.py:1526-1532`). A missing-manifest spot-check returned `VerificationError` while preserving a pre-existing `{"cutover_verdict":"approved"}` artifact. |
| 2 | Maintainer can audit the verdict through one canonical exact-set link index covering all nine required categories. | ✓ VERIFIED | Contract declares all nine kinds and exact row fields. The 48-test suite covers deterministic IDs/order, all nine categories, local/external digest rules, missing/extra/duplicate/dangling/lifecycle/category/digest anti-joins, resolved targets, and symlinked audit targets. Current quick output contains 47 unique links with no duplicate IDs or missing local digests; zero-count categories reflect the intentionally empty default evidence/decision fixture. |
| 3 | Approved routes only to production-cutover planning; blocked and exception-bearing verdicts route to source-backed targeted repair and require a fresh decision. | ✓ VERIFIED | `build_route` implements the exclusive truth table with `planning_only: true` and `production_actions_authorized: false`. Current output is blocked with 47 repair rows, including all 4 Phase-34-created missing-stream blockers; every row has the exact nine fields and nonempty owner, action, and exit/review criteria. |
| 4 | Cutover verdict, demotion input validation/value/source, and demotion gate state/reasons remain independent. | ✓ VERIFIED | `project_demotion` preserves missing, malformed, stale, lifecycle-mismatched, invalid, valid approve, and valid reject states and forces the gate blocked unless validation is valid, the decision is approve, readiness is unblocked, and gate reasons are empty. Current output remains missing/missing/blocked with `approval-missing` and `readiness-input-invalid`; targeted tests prove cutover approval and an open gate do not imply each other. |
| 5 | The default quick path emits blocked plus targeted repair without synthesizing evidence, approval, exceptions, or demotion authority. | ✓ VERIFIED | `just phase35-verify` regenerated Phase 31-34 fail-closed prerequisites and the exact eight-file Phase 35 bundle. Output is `blocked`, `targeted-blocker-repair`, `requires_fresh_cutover_decision: true`, `production_actions_authorized: false`, `raw_evidence_consumed: false`, and missing/blocked demotion state. |

**Score:** 4/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json` | Closed verdict/route, audit-link, lifecycle, security, output, and demotion-separation contract | ✓ VERIFIED | Exists, 345 lines, exact identity/lifecycle/requirements, exact eight generated artifacts, nine link kinds, reason codes, truth tables, and prohibited-authority semantics; `--contract-only` passed. |
| `tools/bazel/phase35_cutover_decision_artifact_test.py` | Focused truth-table, security, routing, audit, projection, containment, and wiring regressions | ⚠️ PARTIAL | Exists, 1,465 lines, and all 48 tests pass. It includes the iteration 1-3 regressions, but does not test durable blocked replacement when source loading fails before output generation. |
| `tools/bazel/phase35_cutover_decision_artifact.py` | Standard-library verifier and deterministic artifact generator | ⚠️ PARTIAL | Exists, 1,699 lines, substantive, wired, and passes normal contract/security/wiring/quick flows. The source-error output-preservation path is not fail-closed at the artifact boundary. |
| `tools/bazel/BUILD.bazel` | Phase 35 source manifests and verifier/test targets | ✓ VERIFIED | `phase35_source_ref_manifests`, `phase35_verify`, and `phase35_verify_tests` exist and both Bazel targets passed through `just phase35-verify`. |
| `BUILD.bazel` | Phase 35 docs filegroup and root aliases | ✓ VERIFIED | Docs filegroup plus `phase35_verify` and `phase35_verify_tests` aliases exist; Bazel analysis and execution passed. |
| `tools/bazel/rust_workflow.sh` | Ordered prerequisite regeneration and Phase 35 dispatch | ✓ VERIFIED | Exact case arms and command order are present; `bash -n`, `--wiring-only`, and the full workflow passed. |
| `justfile` | Developer-facing verification facade | ✓ VERIFIED | `phase35-verify` runs tests before generation; the recipe passed. |
| `build/ci-evidence/phase35/*` | Exact deterministic decision bundle | ✓ VERIFIED for valid blocked input | Exactly eight contract-defined files exist. JSON fields, report projection, link counts, route scope, lifecycle, and raw-evidence flag validate. |

### Key Link Verification

The generic key-link checker reported 2/5 because three plan regexes contain escaped-dot patterns that do not match the implementation's `Path` constants or exact workflow command text. Manual source and behavioral verification confirms all five links.

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| Phase 35 verifier | Phase 34 run manifest | Exact immediate source path, identity, lifecycle, output root, artifact set, snapshot refs, and security validation | ✓ WIRED | `load_bundle` begins from `final-readiness-run-manifest.json`; no alternate filesystem search or caller verdict input exists. |
| Phase 35 verifier | Canonical audit-link index | Independently derived source rows, deterministic projection, exact-set comparison, resolved-target validation, and digest recomputation | ✓ WIRED | Unit tests mutate every anti-join axis and resolve local fragments; current index has 47 unique links and valid local digests. |
| Audit-link index | Cutover decision and Markdown | Shared canonical link rows and counts | ✓ WIRED | `write_bundle` derives index, counts, decision ref, and report from the same in-memory links; generated-output validation recomputes report equality. |
| Cutover decision | Next-milestone route | Closed verdict-to-route truth table | ✓ WIRED | All three route cases are tested; current decision and route agree on blocked/targeted repair. |
| `rust_workflow.sh` | Phase 35 verifier | Ordered Phase 31-34 quick regeneration, Phase 34/35 wiring checks, then Phase 35 quick generation | ✓ WIRED | `just phase35-verify` executed both Bazel targets and the complete prerequisite chain successfully. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `phase35_cutover_decision_artifact.py` | `source` bundle | Validated Phase 34 run manifest, ledger, packet, blocker summary, dry run, Phase 31/32 snapshots, and digest-bound Phase 33 registers | Yes | ✓ FLOWING |
| `cutover-audit-link-index.json` | `links` | Canonical Phase 31-34 evidence, blocker, decision, readiness, and demotion sources | Yes; categories may be empty when the default upstream fixture has no accepted evidence or maintainer decisions | ✓ FLOWING |
| `cutover-decision.json` | verdict, reasons, blockers, demotion projection | Readiness packet/ledger, active canonical exceptions, audit validation, repair-scope validation, and Phase 33/34 demotion inputs | Yes | ✓ FLOWING for valid inputs; ✗ stale output can survive source-load failure |
| `next-milestone-route.json` | route and follow-up scope | Closed route table plus all blocked or exception-covered Phase 34 ledger rows | Yes; current bundle has 47 traceable scope rows | ✓ FLOWING |
| `redacted-cutover-decision-report.md` | report projection | The same in-memory decision, route, and canonical link index as JSON | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Focused Phase 35 regression suite | `env PYTHONDONTWRITEBYTECODE=1 python3 -B tools/bazel/phase35_cutover_decision_artifact_test.py -q` | 48 tests in 3.895s, OK | ✓ PASS |
| Contract, wiring, security, shell syntax, and whitespace | Phase 35 `--contract-only`, `--wiring-only`, `--security-only`; `bash -n`; `git diff --check` | All exit 0 | ✓ PASS |
| Repository verification facade | `just phase35-verify` | Both Bazel targets passed; Phase 31-35 quick chain regenerated and validated | ✓ PASS |
| Default generated projection | Direct JSON audit | Blocked; targeted repair; 47 blockers/scopes; missing demotion decision; blocked demotion gate; no production authority | ✓ PASS |
| Invalid-source durable fail-closed behavior | Temporary root with missing Phase 34 manifest and pre-existing approved Phase 35 decision | Command raised `source artifact missing`; stale approved JSON remained unchanged | ✗ FAIL |
| Bazel lockfile hygiene | SHA-256 before/after restoration | Bazel changed lock version 26→28; restored to original SHA-256 `21587df8a47a42952e5301f59f4809b23eba5f336780847d0c3bc02422275a03` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| CUTOVER-01 | 35-01 | Produce one explicit approved, blocked, or approved-with-exceptions artifact | ✗ BLOCKED | The closed reducer and valid-input artifact path work, but invalid source loading can leave an earlier approved artifact intact rather than publishing or preserving an authoritative blocked result. |
| CUTOVER-02 | 35-01 | Link every blocker, exception, residual risk, evidence packet, retained-code decision, readiness result, and demotion decision needed to audit the verdict | ✓ SATISFIED | Nine-kind schema, canonical link derivation, lifecycle/category checks, safe refs, digests, exact anti-joins, resolved targets, and shared projections are implemented and tested. |
| CUTOVER-03 | 35-01 | Route approved to production planning and blocked/exception-bearing to named targeted repair | ✓ SATISFIED | Exclusive route table, planning-only boundary, fresh-decision requirement, 47 source-backed current scopes, and exception/residual criteria are implemented and tested. |

All three requirement IDs declared in PLAN frontmatter are present in `.planning/REQUIREMENTS.md`, map only to Phase 35, and are accounted for. No orphaned Phase 35 requirements exist.

### Review-Fix Lineage

| Review iteration | Fixes confirmed in reachable code/tests | Status |
| --- | --- | --- |
| Iteration 1 | `715620b63` snapshot scanning; `e02a0bb61` Phase 33 digest/projection binding; `296ff7420` resolved canonical audit links; `0b89d013c` all Phase 34 blocker routing; `63376eb19` stale demotion gate blocking; `47cfc7dac` external URI validation | ✓ VERIFIED |
| Iteration 2 | `28b5e2ee9` legacy exception-field rejection; `a508f7ab3` decoded external-ref validation; `bdb5632e1` exception-covered route preservation | ✓ VERIFIED |
| Capped final review | `9410e9d13` adds shared nested source-file containment plus file, parent-directory, and local-audit-target symlink regressions | ✓ VERIFIED |
| Final fix report | `35-REVIEW-FIX.md` iteration 3, one finding in scope, one fixed, zero skipped | ✓ `status: all_fixed` |

The current 48-test suite exercises all of these repairs. The new gap is an untested output-state error path after source validation fails; it is not a regression of the closed review findings above.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `tools/bazel/phase35_cutover_decision_artifact.py` | 1526-1532, 1693-1695 | Validation exception returns before output invalidation or minimal blocked replacement | 🛑 Blocker | A prior approved artifact can remain present after a failed regeneration, violating the durable fail-closed contract. |
| `tools/bazel/phase35_cutover_decision_artifact.py` | file length 1,699 lines | Mixed-responsibility module exceeds the Bright Builds ~628-line refactor trigger | ℹ️ Info | Boundary validation, reducers, audit resolution, output mutation, CLI, and wiring remain concentrated; this is the final review's non-blocking maintainability note. |
| `tools/bazel/phase35_cutover_decision_artifact_test.py` | file length 1,465 lines | Test module exceeds the same advisory trigger | ℹ️ Info | Focused test methods remain identifiable and all pass, but future separation would improve navigation. |

No TODO/FIXME/placeholder implementations, console-only handlers, or user-visible hardcoded empty-data stubs were found. Empty lists/dictionaries in the verifier are accumulators, explicit defaults, or fail-closed sentinels.

### Human Verification Required

None. Phase 35 is deterministic CLI/data-transformation/artifact-generation logic and can be verified programmatically. Real external evidence and maintainer approvals are upstream inputs; the Phase 35 capability and safety boundaries are testable with sanitized fixtures.

### Gaps Summary

One root-cause gap blocks full goal achievement. Normal valid blocked inputs, all verdict/route truth tables, audit completeness, demotion separation, security/containment repairs, and repository wiring pass. But `run_quick` does not establish a blocked output state before consuming untrusted Phase 34 sources, and its exception handler writes no fallback artifact. If a prior run produced `approved`, a later malformed or missing source can make regeneration fail while leaving that approval on disk. The phase needs atomic output-state handling plus an end-to-end stale-approval regression before CUTOVER-01 and the combined fail-closed truth can be verified.

No later phase in the current milestone explicitly owns this gap, so it is not deferred. No verification overrides apply.

***

_Verified: 2026-07-25T23:22:09Z_
_Verifier: the agent (gsd-verifier)_
