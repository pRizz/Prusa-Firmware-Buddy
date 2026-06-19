---
phase: 17-release-candidate-artifact-and-signing-gates
verified_at: 2026-06-19T15:34:20Z
verified: 2026-06-19T15:34:20Z
status: passed
score: "10/10 must-haves verified"
generated_by: gsd-verify-work
generated_at: 2026-06-19T15:34:20Z
lifecycle_mode: yolo
phase_lifecycle_id: 17-2026-06-19T13-57-17
lifecycle_validated: true
overrides_applied: 0
re_verification: false
residual_external_evidence:
  - "Approved release-run artifact outputs must be supplied later by the release environment."
  - "External release signing proof must remain key-identity and digest metadata only; private keys stay outside the repo."
  - "Archived v1.0 release comparison artifacts must be supplied as approved release evidence before final cutover review."
  - "Phase 18 still owns retained-code acceptance and final reference-demotion approval."
---

# Phase 17: Release Candidate Artifact and Signing Gates Verification Report

**Phase Goal:** Release managers can build and verify release-candidate firmware, resources, signing, provenance, and auxiliary packages through Bazel-owned workflows.
**Verified:** 2026-06-19T15:34:20Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

Phase 17 passes for the scoped goal: it creates a Bazel-owned, contract-backed release-candidate evidence gate that validates release artifact, signing, provenance, retention, redaction, and comparison evidence without overclaiming local production release proof.

The release-candidate artifact target is intentionally empty in this workspace, while the representative smoke target builds local fixture artifacts. That is not a blocker for this phase because the Phase 17 context explicitly requires production release and signing rows to remain pending until approved release-run evidence is supplied.

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | Phase 17 has one row-level release evidence contract instead of an umbrella pass. | VERIFIED | `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` has 18 rows and `id: phase17_release_candidate_evidence_contract`. |
| 2 | Required artifact families are represented. | VERIFIED | Contract surfaces include `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, Dwarf, ModularBed, xBuddy Extension, package manifest, signing, retention, and reference comparison. |
| 3 | Release artifact rows use the Bazel-owned workflow identity. | VERIFIED | Release rows carry `//tools/bazel:phase17_release_candidate_artifacts`, `bazel build //tools/bazel:phase17_release_candidate_artifacts`, artifact outputs, and `release_run_required: true`. |
| 4 | Local smoke output cannot masquerade as production release proof. | VERIFIED | `tools/bazel/BUILD.bazel` keeps `phase17_release_candidate_artifacts` empty and `phase17_representative_release_smoke` separate; verifier rejects smoke deps under the release target. |
| 5 | Quick verification writes deterministic redacted evidence under `build/ci-evidence/phase17`. | VERIFIED | `--quick` wrote run manifest, normalized results, signing/provenance summary, comparison report, source snapshot, operator template, and logs. |
| 6 | Production release and signing rows remain pending without supplied release evidence. | VERIFIED | Generated status counts are 16 `pending-release-input`, 1 `external-signing-required`, and 1 `source-contract-passed`; `release_inputs_supplied` is false. |
| 7 | Signing/provenance evidence requires metadata and rejects private key or payload material. | VERIFIED | Verifier enforces key identity, digest, refs, retention, outcome, forbidden field names, forbidden text markers, and overclaim strings; `--security-only` passed. |
| 8 | Release comparison rows cite archived reference evidence and use the allowed mismatch taxonomy. | VERIFIED | Contract refs resolve to approved Phase 11/v1.0 source manifests; mismatch classes are from `pass`, `intentional-delta`, `blocker`, and `deferred-retained-code-issue`. |
| 9 | Release evidence input validation rejects disallowed statuses, paths, workflows, and local-smoke proofs. | VERIFIED | 19 tests cover row status constraints, path guards, workflow matching, source refs, and local-smoke rejection; direct test run passed. |
| 10 | Bazel and `just` run verifier tests before the verifier. | VERIFIED | `just phase17-verify` runs `//tools/bazel:phase17_verify_tests` before `//tools/bazel:phase17_verify`; command passed. |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` | Row-level release/signing/provenance/comparison contract | VERIFIED | Exists, 1612 lines, validates with `--contract-only`, covers `REL-01`, `REL-02`, `REL-03`. |
| `tools/bazel/phase17_release_candidate_evidence.py` | Stdlib verifier, release input validator, quick writer, security scan, wiring check | VERIFIED | Exists, 1214 lines, supports planned modes, compiles, and passes contract/security/wiring/quick checks. |
| `tools/bazel/phase17_release_candidate_evidence_test.py` | Unit coverage for contract, release inputs, redaction, path guards, wiring | VERIFIED | Exists, 697 lines, 19 tests pass. |
| `tools/bazel/BUILD.bazel` | Phase 17 release identity, smoke target, source manifests, verifier labels | VERIFIED | Contains release target, separate smoke target, source-ref filegroup, and `phase17_verify` / `phase17_verify_tests`. |
| `BUILD.bazel` | Root docs filegroup and public aliases | VERIFIED | Contains `phase17_release_candidate_evidence_docs` and root aliases for artifacts and verifier targets. |
| `tools/bazel/rust_workflow.sh` | Phase 17 dispatch | VERIFIED | `phase17_verify` runs wiring then quick; `phase17_verify_tests` runs the test file. |
| `justfile` | Developer facade | VERIFIED | `phase17-verify` and `phase17-release-artifacts-smoke` exist and pass. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `phase17_release_candidate_evidence.py` | Contract manifest | `CONTRACT_MANIFEST` | VERIFIED | `--contract-only` loads and validates the checked-in JSON contract. |
| `phase17_release_candidate_evidence.py` | `build/ci-evidence/phase17` | `DEFAULT_OUTPUT_DIR` and path guards | VERIFIED | `--quick` writes only under the guarded output root. |
| `phase17_release_candidate_evidence.py` | Phase 11 reference manifests | approved source refs | VERIFIED | Source refs are restricted to approved manifests and top-level row collections. |
| Contract rows | `//tools/bazel:phase17_release_candidate_artifacts` | `bazel_label` and `release_command` | VERIFIED | Release rows require the Phase 17 label and matching build command. |
| `tools/bazel/BUILD.bazel` | `tools/bazel/rust_workflow.sh` | scoped `shell_binary` rules | VERIFIED | Manual scoped check and `--wiring-only` pass; generic helper's earlier miss was a false negative. |
| `justfile` | `//tools/bazel:phase17_verify_tests` | `phase17-verify` recipe | VERIFIED | Parsed recipe runs tests before verifier; `just phase17-verify` passed. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `phase17_release_candidate_evidence.py` | Contract rows | `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` | Yes - JSON rows are loaded, validated, and source refs resolved. | FLOWING |
| `phase17_release_candidate_evidence.py` | Release evidence rows | Optional `--release-evidence` JSON | Yes when supplied; absent input leaves release rows pending by design. | FLOWING |
| `build/ci-evidence/phase17/*.json` | Normalized results and manifests | `write_quick_artifacts()` from validated contract/release rows | Yes - generated row count/statuses match contract state. | FLOWING |
| Bazel/just wiring | Command lists and rule data | `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `rust_workflow.sh`, `justfile` | Yes - parsed by scoped wiring helpers and exercised through Bazel/just commands. | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Python syntax compiles | `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py` | exit 0 | PASS |
| Unit regression suite | `python3 tools/bazel/phase17_release_candidate_evidence_test.py` | 19 tests OK | PASS |
| Contract validation | `python3 tools/bazel/phase17_release_candidate_evidence.py --contract-only` | passed | PASS |
| Security scan | `python3 tools/bazel/phase17_release_candidate_evidence.py --security-only` | passed | PASS |
| Quick artifact generation | `python3 tools/bazel/phase17_release_candidate_evidence.py --quick` | wrote `build/ci-evidence/phase17` | PASS |
| Wiring validation | `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` | passed | PASS |
| Root/tools release labels resolve | `bazel query "//tools/bazel:phase17_release_candidate_artifacts + //:phase17_release_candidate_artifacts"` | returned both labels | PASS |
| Release identity target builds | `bazel build //tools/bazel:phase17_release_candidate_artifacts` | build successful, empty target by design | PASS |
| Bazel verifier tests | `bazel run //tools/bazel:phase17_verify_tests` | 19 tests OK | PASS |
| Bazel verifier | `bazel run //tools/bazel:phase17_verify` | wiring passed, quick evidence written | PASS |
| Developer facade | `just phase17-verify` | tests before verifier, both passed | PASS |
| Representative smoke artifacts | `just phase17-release-artifacts-smoke` | built representative `.bin`, `.bbf`, `.dfu`, map, provenance, resource, and manifest outputs | PASS |
| Diff hygiene | `git diff --check` | exit 0 | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| `REL-01` | `17-01-PLAN.md` | Build release-candidate artifact surfaces through Bazel-owned workflows. | SATISFIED | Contract enumerates artifact surfaces and workflow identity; Bazel labels resolve/build; separate smoke target builds representative local artifacts without claiming release proof. |
| `REL-02` | `17-01-PLAN.md` | Verify signing, provenance, build input identity, and retention while keeping private keys out of repo/planning artifacts. | SATISFIED | Contract requires metadata fields; verifier rejects private key, credential, and payload markers; generated signing/provenance summary is redacted and pending external signing input. |
| `REL-03` | `17-01-PLAN.md` | Compare release surfaces against archived v1.0 reference evidence and classify mismatches. | SATISFIED | Contract comparison row cites Phase 11 reference evidence, source refs resolve, mismatch vocabulary is enforced, generated comparison report exists. |

No orphaned Phase 17 requirements were found in `.planning/REQUIREMENTS.md`; `REL-01`, `REL-02`, and `REL-03` are all claimed by `17-01-PLAN.md`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `tools/bazel/phase17_release_candidate_evidence.py` | 1 | File length is 1214 lines, above the Bright Builds refactor trigger. | Info | Same as review `IN-01`; not a phase-goal blocker because critical/warning issues were fixed and coverage/commands pass. |

Stub scan matched benign helper returns such as `return []` / `return {}` in parser and accumulator helpers. No TODO, placeholder, console-only implementation, or user-visible stub was found in Phase 17 files.

### Human Verification Required

None for Phase 17 gate acceptance. The remaining release-run, signing, and comparison inputs are external evidence constraints deliberately represented as pending rows, not local verification gaps.

### Residual External Evidence Constraints

1. The real release-candidate artifact outputs must be supplied by an approved release environment through `//tools/bazel:phase17_release_candidate_artifacts`; the current target is an empty identity target to avoid wrapping smoke fixtures.
2. External release signing proof must be supplied as key identity/fingerprint, artifact digests, verification outcome, and retained refs only.
3. Archived v1.0 release comparison evidence must be supplied as approved comparison refs before final cutover review.
4. Retained-code acceptance and final reference demotion remain Phase 18 responsibilities.

### Gaps Summary

No blocking gaps found. The Phase 17 goal is achieved for the scoped release-candidate evidence gate: contract, verifier, redaction/path guards, comparison classification, Bazel wiring, just facade, and smoke separation are present, substantive, wired, and behaviorally verified.

---

_Verified: 2026-06-19T15:34:20Z_
_Verifier: the agent (gsd-verifier)_
