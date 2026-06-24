---
phase: 26-release-signing-and-upstream-result-evidence
fixed_at: 2026-06-24T14:49:47Z
review_path: .planning/phases/26-release-signing-and-upstream-result-evidence/26-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 26: Code Review Fix Report

**Fixed at:** 2026-06-24T14:49:47Z
**Source review:** .planning/phases/26-release-signing-and-upstream-result-evidence/26-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope across review iterations: 3
- Fixed: 3
- Skipped: 0

## Fixed Issues

### CR-01: Phase 20 Required Metadata Is Not Enforced For Passed Rows

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase26_release_signing_upstream_evidence.py`, `tools/bazel/phase26_release_signing_upstream_evidence_test.py`
**Commit:** 7b4773cee
**Applied fix:** Added Phase 20 row-specific metadata enforcement for passed release rows, updated the generated operator template to include row-specific metadata fields, and added a regression that rejects a passed redaction-boundary row missing `redaction_scan`.

### CR-02: Unknown Release Input Fields Are Retained Verbatim

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase26_release_signing_upstream_evidence.py`, `tools/bazel/phase26_release_signing_upstream_evidence_test.py`
**Commit:** 54908e357
**Applied fix:** Added release-row sanitization that rejects unsupported fields before retained outputs are written, stores only allowed schema fields, and added a regression proving an `apiToken` field aborts before the output root exists.

### CR-03: Nested Unsupported Digest Fields Are Retained In Release Evidence

**Status:** fixed: verified clean by re-review
**Files modified:** `tools/bazel/phase26_release_signing_upstream_evidence.py`, `tools/bazel/phase26_release_signing_upstream_evidence_test.py`
**Commit:** 6695a26f2
**Applied fix:** Added explicit `subject_digests` nested-field validation, sanitized retained digest objects down to `artifact_ref` and `sha256`, and added a regression proving `subject_digests[0].apiToken` aborts before the output root exists.

## Verification Evidence

The full required sequence passed before each code/test fix commit:

1. `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py`
1. `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --contract-only`
1. `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --security-only`
1. `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only`
1. `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26`
1. `cargo fmt --all`
1. `cargo clippy --all-targets --all-features -- -D warnings`
1. `cargo build --all-targets --all-features`
1. `cargo test --all-features`

The final standard-depth re-review reported `status: clean` with zero findings in `.planning/phases/26-release-signing-and-upstream-result-evidence/26-REVIEW.md`.

---

_Fixed: 2026-06-24T14:49:47Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
