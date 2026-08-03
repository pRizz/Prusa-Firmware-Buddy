---
phase: 42
fixed_at: "2026-08-03T23:37:27Z"
review_path: ".planning/phases/42-truthful-bazel-graph-and-executable-mini-toolchain/42-REVIEW.md"
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 42: Code Review Fix Report

**Fixed at:** 2026-08-03T23:37:27Z  
**Source review:** `.planning/phases/42-truthful-bazel-graph-and-executable-mini-toolchain/42-REVIEW.md`  
**Iteration:** 1

**Summary:**

- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: Python provenance verification omits five Phase 42 entrypoints

**Files modified:** `tools/bazel/phase42/graph_isolation_test.py`  
**Commits:** `e83c98330`, `76fd51999`  
**Applied fix:** Expanded the audit to every Phase 42 `py_test` and `py_binary`, added declaration-parity coverage, and queried each Python entrypoint independently. The executable audit now recognizes the exact Bzlmod canonical identity of the pinned Arm repository while continuing to reject unapproved external repositories. The follow-up allowlist correction was validated by the real Linux action graph before the canonical qualification passed.

### WR-02: A pinned interpreter in one action masks wrong provenance in another

**Files modified:** `tools/bazel/phase42/graph_isolation_test.py`  
**Commit:** `e83c98330`  
**Status:** fixed: requires human verification  
**Applied fix:** Replaced the batched action query with per-owner queries, narrowed executable provenance to exact approved repositories, and added a mutation test proving that a correctly pinned owner cannot mask another owner using `external/evil_python/bin/python3`.

### WR-03: The simulator reference route is not executable

**Files modified:** `justfile`, `tools/bazel/phase2_verify.py`, `tools/bazel/phase42/reference_separation_test.py`, `tools/bazel/reference_contract.sh`  
**Commit:** `2799ed190`  
**Applied fix:** Made the reference simulator recipe accept a firmware argument, validated that it names an existing file, resolved relative paths from the workspace, and invoked `pytest tests/integration --firmware "$firmware"` directly. Tests now retain the real shell, fake only `pytest`, and cover paths containing spaces plus missing and nonexistent firmware arguments.

### WR-04: Darwin x86_64 cannot run the promised host-only diagnostic

**Files modified:** `MODULE.bazel`, `tools/bazel/phase42/BUILD.bazel`, `tools/bazel/phase42/phase42_verify_test.py`, `tools/bazel/phase42/toolchain_provenance_test.py`  
**Commit:** `800dcc85e`  
**Applied fix:** Added the independently verified Python 3.12.10 Intel-Darwin checksum, mutation coverage for every pinned Python archive, and a simulated `darwin_x86_64_host` analysis contract. An explicit `aquery` reached the host-check target with `rules_python++python+python_3_12_10_x86_64-apple-darwin/bin/python3`, preserving the exact canonical-Linux remedy.

## Verification Evidence

- `bazel test //tools/bazel/phase42:phase42_verifier_tests --lockfile_mode=error --nocache_test_results --test_output=errors`: 9 of 9 tests passed on Darwin arm64.
- `just phase42-host-check`: passed all ten Darwin-arm64 rejection routes with the required `HostPolicyInfo` diagnostic.
- `just phase42-verify` on Darwin arm64: produced the expected nonzero unsupported-host result and canonical Linux x86_64 remedy.
- Canonical Linux x86_64 qualification in `gcr.io/bazel-public/bazel:9.2.0`: passed all toolchain, Arm link smoke, platform-negative, graph-isolation, facade, reference-separation, aggregate, identity, output, and lock-stability checks.
- `MODULE.bazel.lock` remained stable at SHA-256 `5b18570e4fa8283ef15c861a3d3a8d5a5d94f1e8b41baf6594e3c3bc16e3d4c9` during canonical qualification.
- Before each fix commit, `git diff --check`, `bun scripts/bright-builds-check.ts all`, `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` passed.

***

_Fixed: 2026-08-03T23:37:27Z_  
_Fixer: the agent (gsd-code-fixer)_  
_Iteration: 1_
