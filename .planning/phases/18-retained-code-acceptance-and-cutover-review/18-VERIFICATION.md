---
phase: 18-retained-code-acceptance-and-cutover-review
verified: 2026-06-20T17:44:06Z
status: passed
score: "6/6 must-haves verified"
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 18-2026-06-20T14-27-15
generated_at: 2026-06-20T17:44:06Z
lifecycle_validated: true
overrides_applied: 0
---

# Phase 18: Retained-Code Acceptance and Cutover Review Verification Report

**Phase Goal:** Maintainers can approve or reject reference demotion through explicit retained-code acceptance packets, final gate evidence, and residual-risk review.
**Verified:** 2026-06-20T17:44:06Z
**Status:** passed
**Re-verification:** No - initial verification
**HEAD:** b10a06cf9f2d4bebbf53b3b83f212d4ff62e9ed5

## Goal Achievement

Material guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` with no active local override, Bright Builds `standards/core/verification.md`, `standards/core/testing.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/languages/rust.md`, GSD verification overrides, gates, thinking models, and verifier calibration examples.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Retained-code acceptance packets exist for retained C, C++, ASM, generated, vendor, HAL, RTOS, network, filesystem, signing, release-artifact, resource, MMU, auxiliary-controller, and runtime surfaces. | VERIFIED | `phase18_cutover_review_contract.json` contains 10 retained packet rows. Packet taxonomy covers `ASM`, `C`, `C++`, `HAL`, `MMU`, `RTOS`, `auxiliary-controller`, `filesystem`, `generated`, `network`, `release-artifact`, `resource`, `runtime`, `signing`, and `vendor`. `--contract-only` passed source-ref coverage checks. |
| 2 | Final reference-demotion checklist links CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence without promoting pending upstream evidence to approval. | VERIFIED | Contract contains 9 final criteria across evidence families `ci`, `simulator`, `hardware`, `live-service`, `release`, `retained-code`, `residual-risk`, and `maintainer-decision`, with source refs to Phase 11 and Phase 13-17 manifests. Generated quick output has final statuses `pending` and `blocked`, not approval. |
| 3 | Maintainers can supply approve, reject, or exception decisions with auditable metadata, rationale, evidence refs, and residual-risk handling. | VERIFIED | `final_decision_schema` requires decision id, criterion id, decision, status, approver metadata, timestamp, rationale, evidence refs, residual risk, exception metadata, and redaction summary. Tests cover approval metadata, reject/status mismatch, exception metadata, evidence refs, duplicate IDs, and phase/lifecycle checks. |
| 4 | Local quick verification keeps `demotion_allowed` false unless valid maintainer decision input is supplied and every required final criterion is passed, exception-approved, or validly not-applicable. | VERIFIED | `--quick` generated `decision_inputs_supplied=false` and `demotion_allowed=false`. `demotion_allowed()` returns false without decision input; tests verify true only for complete approving input and false for pending, failed, blocked, exception-requested, exception-rejected, redaction, and overclaim statuses. |
| 5 | Generated readiness material is redacted review output; machine-readable gate rows and decision input are authoritative. | VERIFIED | Quick mode generated the 7 expected artifacts under `build/ci-evidence/phase18`. The redacted report contains the boundary statement that it is review material only. `--security-only` passed over contract, optional input path rules, and generated artifacts; tests cover secret markers, camelCase credential fields, raw payload/crash dump text, no-decision overclaims, and retained acceptance overclaims. |
| 6 | Bazel labels and `just phase18-verify` run tests before the verifier. | VERIFIED | `tools/bazel/BUILD.bazel` defines `phase18_source_ref_manifests`, `phase18_verify`, and `phase18_verify_tests` with `src = "rust_workflow.sh"`. `rust_workflow.sh` dispatches `phase18_verify_tests` to the test file and `phase18_verify` to wiring plus quick. `justfile` runs `bazel run //tools/bazel:phase18_verify_tests` before `bazel run //tools/bazel:phase18_verify`; `just phase18-verify` passed. |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tools/bazel/manifests/phase18_cutover_review_contract.json` | Authoritative retained packet, final criterion, source-ref, and decision schema contract | VERIFIED | Exists, 981 lines, contains `phase18_cutover_review_contract`, 10 retained packets, 9 final criteria, 7 generated artifacts, and source collection map for Phase 11 and Phase 13-17 inputs. |
| `tools/bazel/phase18_cutover_review.py` | Stdlib verifier, decision-input validator, demotion evaluator, quick writer, security scan, source-ref resolver, and wiring checker | VERIFIED | Exists, 1551 lines. Exposes `--contract-only`, `--security-only`, `--quick`, `--decision-input`, `--output-dir`, and `--wiring-only`; all exercised by tests and local commands. |
| `tools/bazel/phase18_cutover_review_test.py` | Unit coverage for contract, decisions, redaction, path guards, generated artifacts, demotion, and wiring | VERIFIED | Exists, 1236 lines. `python3 tools/bazel/phase18_cutover_review_test.py` passed 49 tests. Tests use Arrange/Act/Assert structure and `subprocess.run(..., shell=False)`. |
| `tools/bazel/BUILD.bazel` | Phase 18 source manifest filegroup and verifier/test labels | VERIFIED | Defines `phase18_source_ref_manifests`, `phase18_verify`, and `phase18_verify_tests`; manual inspection confirms `src = "rust_workflow.sh"` for both Phase 18 shell binaries. |
| `BUILD.bazel` | Root docs filegroup and verifier aliases | VERIFIED | Defines `phase18_cutover_review_docs`, `phase18_verify`, and `phase18_verify_tests` root aliases. |
| `tools/bazel/rust_workflow.sh` | Phase 18 verifier and test dispatch cases | VERIFIED | Contains `phase18_verify)` running wiring and quick, plus `phase18_verify_tests)` running `phase18_cutover_review_test.py`. |
| `justfile` | Developer facade recipe | VERIFIED | Contains `phase18-verify:` with tests-before-verifier ordering. `just phase18-verify` passed. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tools/bazel/phase18_cutover_review.py` | `tools/bazel/manifests/phase18_cutover_review_contract.json` | `CONTRACT_MANIFEST` | WIRED | Constant points to the checked-in contract and `--contract-only` passed. |
| `tools/bazel/phase18_cutover_review.py` | `build/ci-evidence/phase18` | `DEFAULT_OUTPUT_DIR` and output guard | WIRED | Quick mode writes under the default output root and path guards reject invalid decision refs. |
| `phase18_cutover_review_contract.json` | `phase11_retained_code_justifications.json` | retained source refs | WIRED | Contract references retained Phase 11 rows; verifier resolves `file#row-id` refs. |
| `phase18_cutover_review_contract.json` | `phase13_ci_evidence_contract.json` | final criterion source refs | WIRED | Final CI criterion links Phase 13 rows. |
| `phase18_cutover_review_contract.json` | `phase17_release_candidate_evidence_contract.json` | release/signing final criterion source refs | WIRED | Release criterion links Phase 17 artifact/signing rows. |
| `tools/bazel/BUILD.bazel` | `tools/bazel/rust_workflow.sh` | shell_binary `src` | WIRED | Generic GSD checker reported a false negative, but manual grep shows both `phase18_verify` and `phase18_verify_tests` use `src = "rust_workflow.sh"`. `--wiring-only` and `just phase18-verify` passed. |
| `justfile` | `//tools/bazel:phase18_verify_tests` | `phase18-verify` first command | WIRED | `justfile` runs tests before verifier; test `test_just_phase18_verify_runs_tests_before_verifier` and `just phase18-verify` both passed. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `phase18_cutover_review.py` contract path | `CONTRACT_MANIFEST` | Checked-in Phase 18 JSON contract | Yes | FLOWING |
| `phase18_cutover_review.py` retained/final rows | `contract_packets`, `contract_final_criteria` | Contract rows validated by `check_contract` | Yes | FLOWING |
| `phase18_cutover_review.py` source refs | `resolve_source_ref` | Phase 11 and Phase 13-17 JSON manifests | Yes | FLOWING |
| `phase18_cutover_review.py` decisions | `load_decision_input`, `validated_decision_maps` | Optional maintainer decision JSON with phase/lifecycle/schema checks | Yes | FLOWING |
| `build/ci-evidence/phase18/*` | `run_manifest`, `final_results`, `retained_rows` | `write_quick_artifacts` from validated contract and optional decisions | Yes | FLOWING |
| Generated security scan | generated artifact JSON and Markdown | `run_security_scan` plus recomputed expected statuses | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Phase 18 unit tests pass | `python3 tools/bazel/phase18_cutover_review_test.py` | Ran 49 tests in 12.168s, OK | PASS |
| Contract validates | `python3 tools/bazel/phase18_cutover_review.py --contract-only` | `Phase 18 cutover review contract passed` | PASS |
| Wiring validates | `python3 tools/bazel/phase18_cutover_review.py --wiring-only` | `Phase 18 wiring passed` | PASS |
| Quick artifacts are generated and demotion remains blocked without decision input | `python3 tools/bazel/phase18_cutover_review.py --quick` | `Phase 18 quick artifacts written; demotion_allowed=false` | PASS |
| Security and overclaim scan passes | `python3 tools/bazel/phase18_cutover_review.py --security-only` | `Phase 18 security scan passed` | PASS |
| Bazel/just facade executes tests before verifier | `just phase18-verify` | Bazel ran `phase18_verify_tests` first, 49 tests OK, then `phase18_verify` wrote quick artifacts with `demotion_allowed=false` | PASS |
| Lifecycle provenance validates for upstream phase artifacts | `gsd-tools verify lifecycle 18 --expect-id 18-2026-06-20T14-27-15 --expect-mode yolo --require-plans` | Valid for context, plan, and summary before verification file creation | PASS |
| Whitespace diff check | `git diff --check` | No output | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| REV-01 | `18-01-PLAN.md` | Maintainer can review retained-code acceptance packets for every retained surface at cutover. | SATISFIED | 10 packet rows cover the required surface taxonomy and resolve retained source refs. |
| REV-02 | `18-01-PLAN.md` | Maintainer can approve or reject final reference-demotion criteria through an explicit evidence-linked checklist. | SATISFIED | 9 final criteria link CI, simulator, hardware, live-service, release, retained-code, residual-risk, and maintainer-decision evidence families. |
| REV-03 | `18-01-PLAN.md` | Final cutover readiness marks reference demotion allowed only when all required gates pass or have documented maintainer-approved exceptions. | SATISFIED | `demotion_allowed=false` without decision input; demotion status is computed from validated final results and tests cover allowed and blocking statuses. |

No Phase 18 requirements were orphaned in `.planning/REQUIREMENTS.md`; REV-01, REV-02, and REV-03 all map to Phase 18 and are listed in the plan.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `tools/bazel/phase18_cutover_review.py` | 927 | `return {}, {}` | Info | Intentional no-decision path in `validated_decision_maps`; not a stub because quick output keeps `demotion_allowed=false` and tests cover no-decision behavior. |

Stub scan found no TODO/FIXME/placeholder markers, console-only handlers, or hardcoded empty user-visible data flows in the Phase 18 implementation files.

### Human Verification Required

None for phase completion. Actual maintainer sign-off, hardware runs, simulator runs, live-service proof, release signing, and reference demotion remain outside local Phase 18 verification; Phase 18 intentionally gates those through explicit decision inputs and keeps local quick output from approving cutover.

### Residual Risks

- Non-local hardware, simulator, live-service, signing, and maintainer approval evidence was not re-executed by this verification. The phase correctly models those as evidence inputs and keeps `demotion_allowed=false` without validated decision input.
- The generated `maintainer-decision-input-template.json` is a starter template with one retained review and one final decision example; the authoritative full checklist is the retained packet summary and normalized final-demotion rows.
- Wiring validation is exact-text based rather than a Bazel AST parser. This is mitigated by successful `bazel run` execution through `just phase18-verify`.
- Generated artifact security scanning detects forbidden fields, forbidden narrative markers, and local overclaims; it is not a cryptographic integrity mechanism after artifact generation.

### Gaps Summary

No blocking gaps found. The implemented Phase 18 code delivers the retained-code acceptance and cutover review gate promised by the roadmap and plan while preserving the no-overclaim boundary: local evidence can prepare review packets, but it cannot approve reference demotion without explicit maintainer decision input.

---

_Verified: 2026-06-20T17:44:06Z_
_Verifier: the agent (gsd-verifier)_
