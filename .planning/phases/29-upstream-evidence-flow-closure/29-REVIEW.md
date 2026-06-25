---
phase: 29-upstream-evidence-flow-closure
reviewed: 2026-06-25T21:30:28Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json
  - tools/bazel/phase26_release_signing_upstream_evidence.py
  - tools/bazel/phase26_release_signing_upstream_evidence_test.py
  - tools/bazel/phase28_final_readiness_packet.py
  - tools/bazel/phase28_final_readiness_packet_test.py
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
status: issues_found
---

# Phase 29: Code Review Report

**Reviewed:** 2026-06-25T21:30:28Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed the Phase 26 upstream evidence contract/verifier/test and the Phase 28 final readiness verifier/test at standard depth. This review used `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the Bright Builds architecture, code-shape, testing, and verification standards.

The verifier test suites pass, but I found one Phase 26 security-scanner normalization gap and two output-reset edge cases that currently escape the intended `VerificationError` failure path.

Verification performed:

- `python3 -m py_compile tools/bazel/phase26_release_signing_upstream_evidence.py tools/bazel/phase26_release_signing_upstream_evidence_test.py tools/bazel/phase28_final_readiness_packet.py tools/bazel/phase28_final_readiness_packet_test.py`
- `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py`
- `python3 tools/bazel/phase28_final_readiness_packet_test.py`

## Critical Issues

### CR-01: Phase 26 forbidden-field scan misses camelCase names

**File:** `tools/bazel/phase26_release_signing_upstream_evidence.py:253`
**Issue:** `normalized_field_name()` only replaces `-` with `_` and compares that result to the raw `FORBIDDEN_FIELD_NAMES` set. A temporary reproduction showed `private_key` is rejected but `privateKey` is accepted. Because Phase 26 snapshots checked-in contracts/templates into retained evidence, camelCase forbidden fields such as `privateKey`, `passwordValue`, `secretValue`, or `signingKeyValue` can bypass the field-name redaction guard when the value itself does not match a text marker.
**Fix:**
```python
def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {normalized_field_name(field_name) for field_name in FORBIDDEN_FIELD_NAMES}


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(
            key for key in value if normalized_field_name(key) in FORBIDDEN_NORMALIZED_FIELD_NAMES
        )
        if forbidden:
            raise VerificationError(f"{path} contains forbidden evidence fields: {', '.join(forbidden)}")
        for key, child in value.items():
            reject_forbidden_field_names(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_field_names(child, f"{path}[{index}]")
```
Add a regression test that injects `privateKey` or `signingKeyValue` into a checked-in-style contract/template JSON and expects the Phase 26 security scan to fail.

## Warnings

### WR-01: Phase 26 output reset crashes on an existing file

**File:** `tools/bazel/phase26_release_signing_upstream_evidence.py:1146`
**Issue:** `reset_output_root()` calls `shutil.rmtree(full_output_dir)` whenever the output path exists. If the allowed output path exists as a regular file, Python raises `NotADirectoryError`, which is not caught by `main()` because it only handles `VerificationError`. The verifier then emits a traceback instead of the expected fail-closed validation error.
**Fix:**
```python
if full_output_dir.exists():
    if not full_output_dir.is_dir():
        raise VerificationError(f"--output-dir exists and is not a directory: {relative_output_dir.as_posix()}")
    shutil.rmtree(full_output_dir)
full_output_dir.mkdir(parents=True, exist_ok=True)
```
Add a test that creates `build/ci-evidence/phase26` as a file and asserts the CLI exits nonzero with the new `VerificationError` message and no traceback.

### WR-02: Phase 28 output reset crashes on an existing file

**File:** `tools/bazel/phase28_final_readiness_packet.py:298`
**Issue:** `reset_output_root()` has the same regular-file edge case as Phase 26: it checks for symlinks, then calls `shutil.rmtree(path)` for any existing non-symlink path. A regular file at `build/ci-evidence/phase28` raises `NotADirectoryError` outside the verifier's controlled error path.
**Fix:**
```python
if path.exists():
    if path.is_symlink():
        raise VerificationError(f"--output-dir symlink escape risk: {path.as_posix()}")
    if not path.is_dir():
        raise VerificationError(f"--output-dir exists and is not a directory: {path.as_posix()}")
    shutil.rmtree(path)
path.mkdir(parents=True)
```
Add a regression test mirroring the existing symlink escape test, but with the output root created as a regular file.

---

_Reviewed: 2026-06-25T21:30:28Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
