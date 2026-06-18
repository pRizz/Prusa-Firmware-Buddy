---
phase: 16-live-network-and-transfer-qualification
reviewed: 2026-06-18T02:17:52Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/manifests/phase16_live_network_evidence_contract.json
  - tools/bazel/phase16_live_network_evidence.py
  - tools/bazel/phase16_live_network_evidence_test.py
  - tools/bazel/rust_workflow.sh
findings:
  critical: 2
  warning: 1
  info: 0
  total: 3
status: issues_found
---

# Phase 16: Code Review Report

**Reviewed:** 2026-06-18T02:17:52Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the Phase 16 live-network evidence contract, verifier, tests, Bazel labels, just recipe, and Rust workflow dispatch. This review used `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the Bright Builds architecture, code-shape, verification, and testing standards. No project skill directories were present under `.claude/skills/` or `.agents/skills/`.

The checked-in contract and current wiring pass the verifier, but the verifier has three guard defects: generated output can escape through symlinked build parents, the secret scanner misses common API-key assignment/header forms, and live operator rows can be accepted as `passed` with non-live evidence metadata.

Verification run:

- `python3 tools/bazel/phase16_live_network_evidence.py --contract-only` passed.
- `python3 tools/bazel/phase16_live_network_evidence.py --wiring-only` passed.
- `python3 tools/bazel/phase16_live_network_evidence.py --security-only` passed.
- `python3 tools/bazel/phase16_live_network_evidence_test.py` passed, 21 tests.
- Temporary negative repros showed `api-key: super-secret-value` passed the security scan, `local-dry-run` operator evidence produced `passed`, and a symlinked `build/ci-evidence` parent caused `--quick` output outside the temp repo.

## Critical Issues

### CR-01: Quick Output Can Escape Through Symlinked Evidence Parents

**File:** `tools/bazel/phase16_live_network_evidence.py:779-783`
**Issue:** `require_repo_relative_under()` is lexical only. After that check, `write_quick_artifacts()` uses `root / output_dir`, `shutil.rmtree()`, `mkdir()`, and later writes through that path. If an existing parent such as `build/ci-evidence` is a symlink outside the repository, `--quick` still returns success and writes `phase16` artifacts outside the intended `build/ci-evidence/phase16` tree. This violates the artifact containment contract and can delete outside directories through `rmtree()`.
**Fix:**
```python
def contained_output_dir(root: Path, output_dir: Path) -> Path:
    relative_path = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    expected_root = root.resolve() / DEFAULT_OUTPUT_DIR
    full_output_dir = (root / relative_path).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return full_output_dir
```
Use the resolved, contained path for `write_quick_artifacts()` and `iter_security_files()`, and add a regression test with a symlinked `build/ci-evidence` parent that proves no outside artifact is created or deleted.

### CR-02: Secret Scanner Misses API-Key Assignment Forms

**File:** `tools/bazel/phase16_live_network_evidence.py:162-179`
**Issue:** The scanner rejects `api_key`, `API key`, and `x-api-key`, but it does not reject common secret-bearing forms such as `api-key: value`, `token=value`, `password: value`, or `Authorization = Bearer ...`. A temporary Phase 16 evidence artifact containing `api-key: super-secret-value` passed `--security-only`, so generated evidence can retain credential material while the verifier reports success.
**Fix:**
```python
FORBIDDEN_TEXT_PATTERNS = (
    # existing patterns...
    re.compile(r"\b(api[-_]?key|token|password|secret)\b\s*[:=]\s*['\"]?[^'\"\s,}]+", re.IGNORECASE),
    re.compile(r"\bAuthorization\s*[:=]\s*\S+", re.IGNORECASE),
)
```
Keep the pattern assignment/header-shaped so contract text like `wui-api-key-auth` remains valid, and add negative tests for `api-key:`, `token=`, `password:`, and `Authorization =`.

## Warnings

### WR-01: Passed Live Rows Accept Non-Live Operator Evidence

**File:** `tools/bazel/phase16_live_network_evidence.py:654-676`
**Issue:** Operator rows only need non-empty metadata plus matching `scenario_id`, `result`, `service_surface`, `mode`, and artifact refs. The verifier does not parse `timestamp` or constrain `evidence_type` for `passed` live-service rows. A row with `result: "passed"`, `evidence_type: "local-dry-run"`, and `timestamp: "not-a-timestamp"` was accepted and emitted as a passed live scenario, which defeats the no-overclaim boundary.
**Fix:**
```python
LIVE_PASS_EVIDENCE_TYPES = {"live-service-observation", "controlled-service-observation"}

timestamp_text = require_string(row, "timestamp", row_name)
try:
    datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
except ValueError as error:
    raise VerificationError(f"{row_name} timestamp must be ISO-8601 UTC") from error

evidence_type = require_string(row, "evidence_type", row_name)
if scenario["proof_scope"] == "live-service-observation" and result == "passed":
    if evidence_type not in LIVE_PASS_EVIDENCE_TYPES:
        raise VerificationError(f"{row_name} passed live evidence must be live or controlled-service evidence")
```
Add tests proving local dry-run evidence and malformed timestamps are rejected before artifacts are written.

---

_Reviewed: 2026-06-18T02:17:52Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
