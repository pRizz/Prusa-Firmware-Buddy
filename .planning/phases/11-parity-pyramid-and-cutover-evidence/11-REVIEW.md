---
phase: 11-parity-pyramid-and-cutover-evidence
reviewed: 2026-06-14T21:25:22Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - tools/bazel/phase11_verify.py
  - tools/bazel/phase11_verify_test.py
  - tools/bazel/manifests/phase11_parity_pyramid.json
  - tools/bazel/manifests/phase11_requirement_evidence.json
  - tools/bazel/manifests/phase11_reference_comparisons.json
  - tools/bazel/manifests/phase11_cutover_readiness.json
  - tools/bazel/manifests/phase11_retained_code_justifications.json
  - rust/crates/domain/src/cutover.rs
  - rust/crates/domain/src/lib.rs
findings:
  critical: 0
  warning: 5
  info: 0
  total: 5
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-06-14T21:25:22Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Reviewed the Phase 11 Bazel wiring, just facade, verifier, verifier tests, evidence manifests, and Rust cutover domain contract. The current Phase 11 quick verifier, Python verifier tests, and Rust cutover unit tests pass locally, but the verifier has several schema and guard gaps that could allow future malformed cutover evidence to pass.

Review context included repo `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the pinned Bright Builds architecture, code-shape, verification, testing, and Rust standards.

## Warnings

### WR-01: Secret Scan Misses Common Private-Key Variants

**File:** `tools/bazel/phase11_verify.py:60`
**Issue:** The forbidden marker list is matched with case-sensitive substring checks at `tools/bazel/phase11_verify.py:306`. It catches `BEGIN PRIVATE KEY`, but not common PEM headers such as `BEGIN RSA PRIVATE KEY`, `BEGIN EC PRIVATE KEY`, or different casing of secret-like field names. Since this verifier is the Phase 11 redaction gate, those variants could be committed in evidence files while `--security-only` still passes.
**Fix:**
```python
import re

FORBIDDEN_TEXT_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE),
    re.compile(r"(certificate[_-]?pem|password[_-]?value|token[_-]?value|private[_-]?key)", re.IGNORECASE),
]

for pattern in FORBIDDEN_TEXT_PATTERNS:
    if pattern.search(text):
        errors.append(f"{path.as_posix()} contains forbidden evidence marker: {pattern.pattern}")
```
Add regression tests for RSA/EC/OpenSSH private-key headers and mixed-case secret field names.

### WR-02: Rust And Python Row-ID Validators Disagree

**File:** `rust/crates/domain/src/cutover.rs:3`
**Issue:** The Rust validator rejects spaces via `is_ascii_graphic()` but accepts IDs containing `..` unless the whole ID is exactly `..`. The Python verifier does the opposite at `tools/bazel/phase11_verify.py:277`: it accepts spaces as printable ASCII but rejects any `..` substring. That means a future manifest row can pass one boundary and fail another, or a Rust caller can accept a path-confusing ID that the verifier would reject.
**Fix:**
```rust
fn is_path_free_printable_ascii(raw: &str) -> bool {
    raw != "."
        && raw != ".."
        && !raw.contains("..")
        && !raw.contains('/')
        && !raw.contains('\\')
        && raw.bytes().all(|byte| byte.is_ascii_graphic())
}
```
Mirror the same definition in `require_row_id_shape()` by rejecting ASCII space (`ord(char) < 33`) and add paired Python/Rust tests for `"ref artifact"` and `"ref..artifact"`.

### WR-03: Reference Comparison Kind Is Not Validated

**File:** `tools/bazel/phase11_verify.py:571`
**Issue:** `check_comparisons()` requires the `comparison_kind` field but never checks that it is one of the contract values represented by `ReferenceComparisonKind` in Rust. A typo such as `"normalized-semantics"` would pass as long as `byte_identity_claim` stays false, weakening the reference-comparison evidence contract.
**Fix:**
```python
comparison_kind = require_string(row, "comparison_kind", row_name)
if comparison_kind not in {"normalized-semantic", "byte-identity-with-fixture"}:
    raise VerificationError(f"{row_name} comparison_kind is not allowed: {comparison_kind}")
if comparison_kind == "normalized-semantic" and row.get("byte_identity_claim") is True:
    raise VerificationError(f"{row_name} normalized comparisons must not claim byte identity")
if comparison_kind == "byte-identity-with-fixture" and row.get("byte_identity_claim") is not True:
    raise VerificationError(f"{row_name} byte identity comparisons must set byte_identity_claim true")
```
Add a negative verifier test for an unknown `comparison_kind`.

### WR-04: Reference-Demotion Criterion Can Report Ready Status

**File:** `tools/bazel/phase11_verify.py:677`
**Issue:** The verifier only ensures `criteria-reference-demotion-blocked` keeps `demotion_allowed` false. It does not require the row status to remain `not-cutover-ready`, even though the manifest row at `tools/bazel/manifests/phase11_cutover_readiness.json:152` is the explicit guard preventing CMake/C++ reference demotion. A future edit could change the status to `passed-local` while keeping `demotion_allowed: false`, and `--cutover-only` would still pass despite the evidence no longer communicating the blocking state.
**Fix:** Extend the special-case check:
```python
if row.get("id") == "criteria-reference-demotion-blocked":
    if row.get("status") != "not-cutover-ready":
        raise VerificationError(f"{row_name} status must remain not-cutover-ready")
    if row.get("demotion_allowed") is not False:
        raise VerificationError(f"{row_name} must keep demotion_allowed false")
```
Add a test that flips this row to `passed-local` and expects `--cutover-only` to fail.

### WR-05: Known Concern Dispositions Are Unvalidated

**File:** `tools/bazel/manifests/phase11_cutover_readiness.json:177`
**Issue:** `known_concern_dispositions` carries source artifacts, proof scopes, secret-handling fields, and regression guards, but `check_cutover()` only loads `cutover_criteria` from this file at `tools/bazel/phase11_verify.py:620`. The extra collection can contain stale lifecycle IDs, invalid proof scopes, missing source artifacts, or path escapes without failing `--cutover-only`.
**Fix:** Either move these rows to a separately validated manifest or add a `check_known_concern_dispositions()` path that enforces exact IDs, required fields, `phase_lifecycle_id`, allowed `proof_scope`, `secret_handling == "name-only-or-redacted"`, and `require_source_artifacts()` for every row. Add a negative test for a `source_artifacts` path escape under `known_concern_dispositions`.

---

_Reviewed: 2026-06-14T21:25:22Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
