---
phase: 11-parity-pyramid-and-cutover-evidence
fixed_at: 2026-06-14T21:57:46Z
review_path: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-REVIEW.md
iteration: 2
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 11: Code Review Fix Report

**Fixed at:** 2026-06-14T21:57:46Z
**Source review:** .planning/phases/11-parity-pyramid-and-cutover-evidence/11-REVIEW.md
**Iteration:** 2

**Summary:**
- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: Security Scan Misses Phase 11 Context And Research Docs

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`, `.planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md`, `.planning/phases/11-parity-pyramid-and-cutover-evidence/11-RESEARCH.md`
**Commit:** 2f412059b, 428576c98
**Applied fix:** Added `11-CONTEXT.md` and `11-RESEARCH.md` to the Phase 11 security scan path list, added regression coverage for both docs, and sanitized scanned phase-doc examples so real `--security-only` verification passes without embedding forbidden marker literals.

### WR-02: Non-Local Evidence Rows Can Omit Their Required Evidence List

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
**Commit:** 49f3911cf
**Applied fix:** Added a shared non-local evidence helper and required non-empty `required_non_local_evidence` lists for non-local pyramid, requirement, and comparison rows. Added negative tests for empty lists in all three validators.

### WR-03: Cutover Evidence Lists Accept Non-String Values

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
**Commit:** eee8f9489
**Applied fix:** Validated cutover `verifier_commands` and `required_evidence` as non-empty string lists, and applied the `required_evidence` check to retained-code justification rows. Added negative tests for non-string entries in cutover and retained-code evidence lists.

### WR-04: Phase 11 Manifests Still Contain Stale Plan-Prerequisite Statuses

**Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`, `tools/bazel/manifests/phase11_parity_pyramid.json`, `tools/bazel/manifests/phase11_requirement_evidence.json`
**Commit:** 8e9eb87e9
**Applied fix:** Replaced stale `requires-plan-11-03`, `requires-plan-11-04`, and "not created yet" manifest wording with source-backed pending evidence and maintainer-acceptance wording. Extended the verifier stale marker guard and added negative tests for the new stale markers.

## Verification

- `python3 tools/bazel/phase11_verify_test.py` - passed, 34 tests
- `python3 tools/bazel/phase11_verify.py --quick` - passed
- `python3 tools/bazel/phase11_verify.py --security-only` - passed
- `python3 tools/bazel/phase11_verify.py --cutover-only` - passed
- `cargo fmt --all -- --check` - passed
- `cargo clippy --all-targets --all-features -- -D warnings` - passed
- `cargo build --all-targets --all-features` - passed
- `cargo test --all-features` - passed, 136 unit tests plus doc tests

---

_Fixed: 2026-06-14T21:57:46Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 2_
