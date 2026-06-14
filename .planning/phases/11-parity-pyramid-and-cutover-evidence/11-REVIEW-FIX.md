---
phase: 11-parity-pyramid-and-cutover-evidence
fixed_at: 2026-06-14T21:36:27Z
review_path: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 11: Code Review Fix Report

**Fixed at:** 2026-06-14T21:36:27Z
**Source review:** .planning/phases/11-parity-pyramid-and-cutover-evidence/11-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5
- Fixed: 5
- Skipped: 0

## Fixed Issues

### WR-01: Secret Scan Misses Common Private-Key Variants

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
**Commit:** c73176148
**Applied fix:** Replaced case-sensitive forbidden-marker checks with case-insensitive regex scans for private-key, certificate, and secret-field variants, while reporting the matched marker text. Added security-only regression tests for RSA, EC, OpenSSH private-key headers and mixed-case secret field names.

### WR-02: Rust And Python Row-ID Validators Disagree

**Files modified:** `rust/crates/domain/src/cutover.rs`, `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
**Commit:** 3b89d6990
**Applied fix:** Aligned Python and Rust row-ID validation by rejecting spaces and embedded `..` path-confusing IDs. Added paired Python and Rust regression coverage for space-containing and `..` IDs.

### WR-03: Reference Comparison Kind Is Not Validated

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
**Commit:** 8b60098e3
**Applied fix:** Added explicit allowed comparison-kind validation and byte-identity consistency checks for normalized-semantic and byte-identity-with-fixture rows. Added negative verifier tests for unknown kind values and inconsistent byte-identity claims.

### WR-04: Reference-Demotion Criterion Can Report Ready Status

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
**Commit:** d243958a1
**Applied fix:** Required `criteria-reference-demotion-blocked` to keep `status: not-cutover-ready` in addition to `demotion_allowed: false`. Added a cutover-only regression test that rejects a `passed-local` demotion-blocked status.

### WR-05: Known Concern Dispositions Are Unvalidated

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
**Commit:** 7248c3f50
**Applied fix:** Added `known_concern_dispositions` validation for exact row IDs, required fields, lifecycle ID, allowed proof scopes, allowed dispositions, redacted secret handling, and repo-relative source artifacts. Added a negative test for a source artifact path escape in known concern rows.

## Skipped Issues

None - all findings were fixed.

## Verification

- `python3 tools/bazel/phase11_verify_test.py` - passed, 26 tests
- `python3 tools/bazel/phase11_verify.py --quick` - passed
- `python3 tools/bazel/phase11_verify.py --security-only` - passed
- `cargo fmt --all -- --check` - passed
- `cargo clippy --all-targets --all-features -- -D warnings` - passed
- `cargo build --all-targets --all-features` - passed
- `cargo test --all-features` - passed

---

_Fixed: 2026-06-14T21:36:27Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
