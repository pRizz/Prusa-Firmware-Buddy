---
phase: 14-simulator-evidence-gates
verified: 2026-06-17T17:16:39Z
status: passed
score: 9/9 must-haves verified
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 14-2026-06-17T16-11-34
generated_at: 2026-06-17T17:16:39Z
lifecycle_validated: true
overrides_applied: 0
---

# Phase 14: Simulator Evidence Gates Verification Report

**Phase Goal:** Simulator Evidence Gates for startup, task readiness, watchdog-visible startup behavior, G-code, GUI, storage/resource, transfer, selected failure scenarios, and traceability, without overclaiming hardware/live/release/final cutover proof.  
**Verified:** 2026-06-17T17:16:39Z  
**Status:** passed  
**Re-verification:** No - initial verification

## Goal Achievement

Phase 14 achieved its goal. The codebase now has a Phase-14-owned simulator evidence contract, deterministic dry-run evidence generation, explicit real-simulator input gates, overclaim/secret scanning, Bazel labels, and a `just phase14-verify` facade. Real simulator execution remains external because firmware `.bin`/adjacent `.bbf` and simulator runtime inputs are required; quick/dry-run mode correctly leaves active simulator scenarios as `pending-simulator-input` and does not overclaim behavior.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Simulator flows cover startup, task readiness, watchdog-visible startup behavior, and representative G-code execution. | VERIFIED | Contract rows `sim-startup-bootstrap-ready`, `sim-task-readiness-home-wui`, `sim-watchdog-visible-startup-readiness`, and `sim-gcode-file-print-telemetry` map to `SIM-01` with active pytest node IDs. |
| 2 | Simulator flows cover GUI navigation, storage/resource access, transfers, and selected failure behavior with reference-compatible pass/fail semantics. | VERIFIED | Contract rows `sim-gui-filebrowser-navigation`, `sim-storage-resource-wui-list-delete`, `sim-transfer-negative-and-conflict`, and `sim-selected-thermal-failures` map to `SIM-02`; transfer and thermal skipped nodes are listed as residual, not pass evidence. |
| 3 | Simulator results map back to v1.0 requirement IDs and v1.1 cutover criteria. | VERIFIED | Every scenario includes `v1_requirement_ids` and `phase11_source_refs`; `--contract-only` resolves referenced Phase 11 manifest rows. |
| 4 | Hardware-only behavior remains explicitly classified outside simulator proof. | VERIFIED | Residual gates include `pending-hardware`, `pending-live-service`, `pending-release`, and `pending-review`; quick artifacts keep active simulator rows `pending-simulator-input`. |
| 5 | Maintainer can inspect a flow-by-flow simulator evidence matrix for all required scenario families. | VERIFIED | `tools/bazel/manifests/phase14_simulator_evidence_contract.json` has 9 scenario rows covering the required families. |
| 6 | Maintainer can run deterministic local Phase 14 validation without firmware, Mini404/QEMU, or active pytest simulator dependencies. | VERIFIED | `python3 tools/bazel/phase14_simulator_evidence.py --quick` and `just phase14-verify` passed locally without simulator inputs. |
| 7 | Maintainer can see exact external inputs required for real simulator execution. | VERIFIED | Contract `external_inputs` lists `firmware_bin`, adjacent `.bbf`, Mini404/QEMU, pytest environment, and OCR cache; real mode rejects missing `--firmware` and missing adjacent `.bbf`. |
| 8 | Maintainer can map every simulator result to SIM-01, SIM-02, SIM-03, v1.0 evidence rows, and cutover criteria. | VERIFIED | Generated `run-manifest.json` includes requirement coverage for `SIM-01`, `SIM-02`, and `SIM-03`; each scenario preserves Phase 11 refs and residual gates. |
| 9 | Generated evidence does not claim hardware/live/release/signing/retained-code/reference-demotion/cutover proof. | VERIFIED | `--security-only` passed; generated artifact marker scan found no forbidden secret or overclaim markers. |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tools/bazel/manifests/phase14_simulator_evidence_contract.json` | Phase 14 simulator scenario contract | VERIFIED | Exists, valid JSON, 404 lines, covers all required scenarios and `SIM-*` IDs. |
| `tools/bazel/phase14_simulator_evidence.py` | Verifier, dry-run writer, real simulator path, guards | VERIFIED | Exists, substantive, exports `main`, validates contract/security/wiring, writes quick artifacts, validates real inputs. |
| `tools/bazel/phase14_simulator_evidence_test.py` | Regression tests | VERIFIED | Exists, substantive; 20 stdlib tests passed. |
| `tools/bazel/BUILD.bazel` | `phase14_verify` and `phase14_verify_tests` labels | VERIFIED | Labels and Phase 11 source-ref manifest filegroup exist. |
| `BUILD.bazel` | Root aliases and docs filegroup | VERIFIED | Root `phase14_verify`, `phase14_verify_tests`, and `phase14_simulator_evidence_docs` exist. |
| `justfile` | Developer facade | VERIFIED | `phase14-verify` runs Bazel tests before verifier. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tools/bazel/phase14_simulator_evidence.py` | `tools/bazel/manifests/phase14_simulator_evidence_contract.json` | `CONTRACT_MANIFEST`, `read_text`, `load_json`, `check_contract` | VERIFIED | Manual grep confirmed constant and contract validation/read paths. Generic key-link helper had a literal-pattern false negative on the escaped regex. |
| `tools/bazel/phase14_simulator_evidence.py` | `build/ci-evidence/phase14` | `DEFAULT_OUTPUT_DIR` and path guard | VERIFIED | Quick mode writes under the root and rejects `../phase14`. |
| `tools/bazel/rust_workflow.sh` | `tools/bazel/phase14_simulator_evidence.py` | `phase14_verify` dispatch | VERIFIED | Dispatch runs `--wiring-only` and `--quick`; test dispatch runs `phase14_simulator_evidence_test.py`. |
| `justfile` | `//tools/bazel:phase14_verify` | `phase14-verify` recipe | VERIFIED | `just phase14-verify` passed and runs tests before verifier. |

### Data-Flow Trace

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `phase14_simulator_evidence.py` | Contract scenarios | Checked-in JSON loaded via `CONTRACT_MANIFEST` | Yes - validates rows, source refs, statuses, artifact paths | VERIFIED |
| `phase14_simulator_evidence.py` | Quick evidence artifacts | Contract scenarios normalized into manifest/summary/log refs | Yes - writes run manifest, normalized scenarios, redacted summary, snapshot, logs | VERIFIED |
| `phase14_simulator_evidence.py` | Real simulator command | Explicit `.bin`, adjacent `.bbf`, optional simulator path, pytest node IDs | Yes - builds argument list and uses `subprocess.run` without shell execution | VERIFIED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Contract JSON parses | `python3 -m json.tool tools/bazel/manifests/phase14_simulator_evidence_contract.json >/dev/null` | exit 0 | PASS |
| Unit regression suite | `python3 tools/bazel/phase14_simulator_evidence_test.py` | 20 tests passed | PASS |
| Contract/source-ref validation | `python3 tools/bazel/phase14_simulator_evidence.py --contract-only` | exit 0 | PASS |
| Secret/overclaim scan | `python3 tools/bazel/phase14_simulator_evidence.py --security-only` | exit 0 | PASS |
| Deterministic dry-run artifacts | `python3 tools/bazel/phase14_simulator_evidence.py --quick` | exit 0; 9 scenarios, all log refs present | PASS |
| Wiring validation | `python3 tools/bazel/phase14_simulator_evidence.py --wiring-only` | exit 0 | PASS |
| Bazel labels | `bazel query "//tools/bazel:phase14_verify + //tools/bazel:phase14_verify_tests + //:phase14_verify + //:phase14_verify_tests"` | all four labels resolved | PASS |
| Developer facade | `just phase14-verify` | Bazel ran tests before verifier; exit 0 | PASS |
| Whitespace check | `git diff --check` | exit 0 | PASS |
| Phase 13 regression | `python3 tools/bazel/phase13_ci_evidence_test.py && python3 tools/bazel/phase13_ci_evidence.py --quick` | 21 tests passed; quick verifier passed | PASS |
| Real mode requires firmware | `python3 tools/bazel/phase14_simulator_evidence.py --run-simulator` | rejected missing `--firmware` | PASS |
| Real mode requires adjacent `.bbf` | `.bin` without `.bbf` probe | rejected before pytest execution | PASS |
| Output path guard | `--quick --output-dir ../phase14` | rejected path traversal | PASS |
| Pytest node references | AST probe over contract node IDs | all referenced functions exist | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| SIM-01 | `14-01-PLAN.md` | Startup, task readiness, watchdog-visible startup behavior, representative G-code execution | SATISFIED | Four `SIM-01` scenario rows with active pytest nodes and residual hardware/release boundaries. |
| SIM-02 | `14-01-PLAN.md` | GUI navigation, storage/resource access, transfers, selected failure flows | SATISFIED | Four `SIM-02` scenario rows with pass/fail semantics, skipped-node residual handling, and Phase 11 refs. |
| SIM-03 | `14-01-PLAN.md` | Map simulator evidence to v1.0 IDs/cutover criteria without marking hardware-only behavior simulator-proven | SATISFIED | Traceability boundary row plus per-scenario `v1_requirement_ids`, `phase11_source_refs`, residual gates, and unsupported claims. |

No orphaned Phase 14 requirements were found in `.planning/REQUIREMENTS.md`; Phase 14 maps only `SIM-01`, `SIM-02`, and `SIM-03`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `tools/bazel/phase14_simulator_evidence_test.py` | 313, 327, 414, 416 | Secret/overclaim marker strings | INFO | Intentional negative-test fixtures proving guards reject or redact sensitive and overclaiming content. |
| `tools/bazel/BUILD.bazel` | 331, 344, 357, 370 | `firmware_payload` fixture labels | INFO | Existing fixture labels outside Phase 14 security scan scope; not generated evidence or secret-bearing payloads. |

No blocker anti-patterns were found in Phase 14 implementation files.

### Generated Evidence

`python3 tools/bazel/phase14_simulator_evidence.py --quick` writes ignored runtime evidence under `build/ci-evidence/phase14`:

| Artifact | Status | Evidence |
|---|---|---|
| `run-manifest.json` | VERIFIED | Contains 9 scenarios and coverage for `SIM-01`, `SIM-02`, `SIM-03`. |
| `normalized-scenarios.json` | VERIFIED | Present and JSON-readable. |
| `redacted-summary.json` | VERIFIED | Present, lists external input names and unsupported boundaries without secret values. |
| `contract-snapshots/phase14_simulator_evidence_contract.json` | VERIFIED | Present. |
| `logs/*.log` | VERIFIED | One log reference per scenario; all manifest artifact refs exist. |

`git check-ignore -v build/ci-evidence/phase14/run-manifest.json` reports `.gitignore:2:/build*`, and `git status --short --ignored build/ci-evidence/phase14` reports `!! build/`, so generated evidence is ignored runtime output, not committed source.

### Human Verification Required

None required for Phase 14 pass/fail. Real simulator execution with firmware `.bin` plus adjacent `.bbf`, Mini404/QEMU, pytest dependencies, and OCR/cache inputs remains an external run path, not a Phase 14 gap, because quick/contract mode explicitly records active simulator rows as `pending-simulator-input` and does not claim real simulator or hardware proof.

### Residual Risks

- Phase 15 owns physical watchdog timing, thermal/motion safety, physical media/UI behavior, MMU, RS485, toolchanger, and hardware-only safety proof.
- Phase 16 owns live Connect/WUI/TLS, telemetry, proxy, long-transfer, transfer service behavior, and crash-dump upload evidence.
- Phase 17 owns release-candidate firmware/resource/signing/provenance and auxiliary artifact proof.
- Phase 18 owns retained-code acceptance and final reference-demotion/cutover review.

### Disconfirmation Pass

- **Partial requirement risk checked:** `SIM-01`/`SIM-02` say "run simulator evidence flows"; Phase 14 intentionally provides a runnable real path plus deterministic pending-input dry-run artifacts. This is acceptable for the phase goal because the prompt and validation strategy explicitly say real simulator execution remains external and must not be overclaimed.
- **Misleading test risk checked:** Passing quick tests do not prove firmware behavior. The generated manifest keeps active simulator rows `pending-simulator-input`; only the traceability boundary row is `passed`.
- **Uncovered error path checked:** Real mode input validation was probed for missing `--firmware` and missing adjacent `.bbf`; both fail before pytest invocation.

### Gaps Summary

No blocking gaps found. The implementation satisfies Phase 14 by establishing simulator evidence gates, traceability, deterministic local validation, explicit real-run prerequisites, secret/overclaim protections, and Bazel/just workflow wiring while preserving later-phase residual boundaries.

---

_Verified: 2026-06-17T17:16:39Z_  
_Verifier: the agent (gsd-verifier)_
