---
phase: 20-release-candidate-artifact-production
verified: 2026-06-21T14:52:50Z
status: passed
score: "10/10 must-haves verified"
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 20-2026-06-21T12-40-17
generated_at: 2026-06-21T14:52:50Z
lifecycle_validated: true
overrides_applied: 0
---

# Phase 20: Release Candidate Artifact Production Verification Report

**Phase Goal:** Release managers can produce release-candidate firmware, resource, signing, provenance, and comparison outputs through the Bazel-owned release artifact identity target instead of an empty placeholder.
**Verified:** 2026-06-21T14:52:50Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `//tools/bazel:phase17_release_candidate_artifacts` resolves to real release outputs or explicit release-environment inputs. | VERIFIED | `tools/bazel/BUILD.bazel` defines `phase17_release_candidate_artifacts` with `srcs = [":phase20_release_environment_input_manifest"]`; `bazel query` resolves both root and package labels. |
| 2 | Representative smoke fixtures remain separate from production release proof. | VERIFIED | `phase17_representative_release_smoke` still wraps `:representative_release_artifacts`; Phase 20 and Phase 17 verifiers reject `:phase17_representative_release_smoke`, `:representative_release_artifacts`, and `//tools/bazel:phase3_verify` as release identity deps. |
| 3 | Signing/provenance evidence records key/build/digest/retention/verification metadata without private keys or payload leakage. | VERIFIED | Contract rows require `key_identity_ref`, `signing_mode`, `subject_digests`, `build_input_identity`, `retention_refs`, and `verification_outcome`; `--security-only` passed and secret/payload marker scan over checked-in Phase 20 manifests plus generated artifacts returned no matches. |
| 4 | Release-candidate comparison outputs classify archived-reference mismatches with allowed classes and metadata. | VERIFIED | Contract vocabulary is exactly `pass`, `intentional-delta`, `blocker`, `deferred-retained-code-issue`; generated `comparison-classification-report.json` has 18 rows, allowed `blocker` class in quick mode, and no missing reason/owner/surface/risk metadata. |
| 5 | Release managers can inspect a Phase 20 release-result manifest with REL-01/REL-02/REL-03 row statuses. | VERIFIED | `python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` wrote `build/ci-evidence/phase20/release-result-manifest.json` with 18 rows and requirement coverage from the contract. |
| 6 | Local quick verification writes pending release evidence without marking rows passed when no approved release input is supplied. | VERIFIED | Generated manifest has `release_inputs_supplied: false`, status counts `pending-release-input: 17` and `external-signing-required: 1`, and `rg '"status": "passed"'` returned no matches. |
| 7 | `just phase20-verify` runs Bazel verifier tests before the Phase 20 verifier. | VERIFIED | `just phase20-verify` output ran `bazel run //tools/bazel:phase20_verify_tests` first, then `bazel run //tools/bazel:phase20_verify`; both passed. |
| 8 | Phase 17 wiring checks reject empty release identity targets and representative smoke wrapping after Phase 20. | VERIFIED | `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` passed; Phase 17 tests include empty-target, Phase20-manifest acceptance, and smoke wrapping rejection cases. |
| 9 | Phase 20 output-root containment prevents symlink escape/deletion before artifact generation. | VERIFIED | `phase20_release_candidate_artifacts.py` resolves output dirs under `build/ci-evidence/phase20` before `shutil.rmtree`; tests include symlinked output-root and relative symlink escape regressions and passed. |
| 10 | Phase 20 code review is clean after review fixes. | VERIFIED | `20-REVIEW-FIX.md` records 2/2 fixes for Phase 17/20 output-root symlink issues; `20-REVIEW.md` final status is clean with 0 findings. Current py_compile, Phase 17/20 tests, Phase 20 verifiers, `just phase20-verify`, and `git diff --check` passed. |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` | Phase 20 release identity, proof class, status, signing/provenance, retention, and comparison contract | VERIFIED | Exists, substantive, `--contract-only` passed; includes 18 release rows and required outputs for `.bin`, `.bbf`, `.dfu`, map/provenance, resources, language, WUI, ESP, MMU, Dwarf, ModularBed, xBuddy Extension, package, signing, retention, and comparison surfaces. |
| `tools/bazel/manifests/phase20_release_environment_inputs.template.json` | Source-backed release-environment evidence input template | VERIFIED | Exists and is wired into `phase20_release_environment_input_manifest`; rows are `template-only` and `pending-release-input` using `external://phase20/` refs. |
| `tools/bazel/phase20_release_candidate_artifacts.py` | Stdlib verifier/result writer | VERIFIED | Exposes `--contract-only`, `--security-only`, `--quick`, `--release-input`, `--output-dir`, and `--wiring-only`; writes Phase 20 generated artifacts. |
| `tools/bazel/phase20_release_candidate_artifacts_test.py` | Regression tests for contract, no-overclaim, redaction, path, comparison, and wiring behavior | VERIFIED | 18 tests passed. Includes symlink containment and smoke/empty target rejection cases. |
| `tools/bazel/BUILD.bazel` | Phase 20 Bazel labels and non-empty Phase 17 release artifact identity | VERIFIED | Defines `phase20_release_environment_input_manifest`, non-empty `phase17_release_candidate_artifacts`, `phase20_source_ref_manifests`, `phase20_verify`, and `phase20_verify_tests`. |
| `BUILD.bazel` | Root Phase 20 docs filegroup and verifier aliases | VERIFIED | Defines `phase20_release_candidate_artifacts_docs`, `phase20_verify`, and `phase20_verify_tests`; root release identity alias resolves. |
| `tools/bazel/rust_workflow.sh` | Phase 20 verifier dispatch | VERIFIED | `phase20_verify` dispatch runs `--wiring-only` then `--quick`; `phase20_verify_tests` dispatch runs the test file. |
| `justfile` | Developer facade for Phase 20 verification | VERIFIED | `phase20-verify` runs Bazel test target before verifier target; command passed. |
| `tools/bazel/phase17_release_candidate_evidence.py` | Phase 17 compatibility guard for non-empty production-safe release identity | VERIFIED | Requires `:phase20_release_environment_input_manifest` and rejects empty/smoke/phase3 release identity sources. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tools/bazel/phase20_release_candidate_artifacts.py` | `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` | `CONTRACT_MANIFEST` constant | WIRED | `CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json")`; `--contract-only` passed. |
| `tools/bazel/phase20_release_candidate_artifacts.py` | `build/ci-evidence/phase20/release-result-manifest.json` | quick artifact writer | WIRED | `write_quick_artifacts` writes `release-result-manifest.json`; quick command created the file. |
| `tools/bazel/phase20_release_candidate_artifacts.py` | `external://phase20/` | release input ref guard | WIRED | `ALLOWED_EXTERNAL_REF_ROOT = "external://phase20/"`; path/ref rejection tests passed. |
| `tools/bazel/BUILD.bazel` | `tools/bazel/manifests/phase20_release_environment_inputs.template.json` | `phase20_release_environment_input_manifest` | WIRED | Filegroup `srcs = ["manifests/phase20_release_environment_inputs.template.json"]`; release identity depends on that filegroup. |
| `tools/bazel/rust_workflow.sh` | `tools/bazel/phase20_release_candidate_artifacts.py` | `phase20_verify` dispatch | WIRED | Dispatch runs `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only` then `--quick`; `just phase20-verify` passed. |
| `justfile` | `//tools/bazel:phase20_verify_tests` | `phase20-verify` recipe | WIRED | Recipe runs tests before verifier; observed in `just phase20-verify` output. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `tools/bazel/phase20_release_candidate_artifacts.py` | `contract` / `rows` | `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` loaded by `check_contract()` and `contract_rows()` | Yes | FLOWING - quick output rows are generated from checked-in contract rows. |
| `tools/bazel/phase20_release_candidate_artifacts.py` | `release_rows` | Optional `--release-input` parsed by `validated_release_rows()` | Yes when supplied; absent rows remain pending | FLOWING - no input produces pending statuses, and tests cover approved/invalid input behavior. |
| `tools/bazel/BUILD.bazel` | `phase17_release_candidate_artifacts.srcs` | `:phase20_release_environment_input_manifest` filegroup | Yes | FLOWING - Bazel query resolves the non-empty identity and verifier wiring enforces exact source. |
| `tools/bazel/phase17_release_candidate_evidence.py` | `srcs` parsed from `tools/bazel/BUILD.bazel` | `check_release_candidate_artifact_target()` | Yes | FLOWING - Phase 17 wiring accepts Phase 20 manifest source and rejects empty/smoke sources. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Python files compile | `python3 -m py_compile ...phase17... ...phase20...` | Exit 0 | PASS |
| Phase 17 compatibility tests | `python3 tools/bazel/phase17_release_candidate_evidence_test.py` | 23 tests passed | PASS |
| Phase 20 verifier tests | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` | 18 tests passed | PASS |
| Phase 17 release identity wiring | `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` | Passed | PASS |
| Phase 20 contract validation | `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` | Passed | PASS |
| Phase 20 redaction/security scan | `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only` | Passed | PASS |
| Phase 20 wiring validation | `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only` | Passed | PASS |
| Phase 20 quick artifact generation | `python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` | Wrote `build/ci-evidence/phase20` | PASS |
| Generated no-overclaim manifest | `jq` and `rg` over `release-result-manifest.json` | 18 rows, no `passed`, `release_inputs_supplied: false` | PASS |
| Bazel aliases resolve | `bazel query "//tools/bazel:phase20_verify + //tools/bazel:phase20_verify_tests + //:phase20_verify + //:phase20_verify_tests + //tools/bazel:phase17_release_candidate_artifacts + //:phase17_release_candidate_artifacts"` | All 6 labels resolved | PASS |
| Public facade works | `just phase20-verify` | Bazel test target then verifier target passed | PASS |
| Whitespace hygiene | `git diff --check` | Exit 0 | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| REL-01 | 20-01, 20-02 | Release manager can build release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, and auxiliary firmware artifacts through Bazel-owned workflows. | SATISFIED | Contract covers required artifact outputs; release identity is non-empty and points to explicit release-environment input manifest; Bazel query and `just phase20-verify` pass. |
| REL-02 | 20-01, 20-02 | Release manager can verify signing, provenance, build input identity, and artifact retention without private keys in repo/planning artifacts. | SATISFIED | Contract requires signing/provenance/retention fields; verifier rejects forbidden key/payload/credential markers; security scan and generated summary checks pass. |
| REL-03 | 20-01, 20-02 | Maintainer can compare release-candidate surfaces against archived v1.0 reference evidence and classify every mismatch. | SATISFIED | Contract enforces mismatch vocabulary and metadata; generated comparison report has 18 classified rows with no missing reason/owner/surface/risk metadata. |

No orphaned Phase 20 requirements were found in `.planning/REQUIREMENTS.md`; REL-01, REL-02, and REL-03 are mapped to Phase 20.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| None | - | - | - | Anti-pattern scan found no TODO/FIXME/placeholders/console-only implementations. Empty `return []` / `return {}` matches are helper fallbacks in validation logic, not user-visible stubs. |

### Human Verification Required

None. Full private-key release signing remains an external release-environment activity by design; Phase 20 verifies the machine-readable contract, explicit release-environment input path, no-overclaim behavior, redaction, retention/provenance metadata shape, and Bazel-owned identity needed for that activity.

### Gaps Summary

No gaps found. Phase 20 closes the empty release identity gap without promoting smoke fixtures, writes the Phase 20 release-result manifest, keeps quick evidence pending until approved release input is supplied, and exposes passing Bazel/just verification.

---

_Verified: 2026-06-21T14:52:50Z_
_Verifier: the agent (gsd-verifier)_
