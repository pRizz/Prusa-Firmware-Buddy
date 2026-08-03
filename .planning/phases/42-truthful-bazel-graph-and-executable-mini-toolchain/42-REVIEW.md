---
phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
reviewed: 2026-08-03T23:11:56Z
depth: standard
files_reviewed: 30
files_reviewed_list:
  - .bazelrc
  - .bazelversion
  - MODULE.bazel
  - MODULE.bazel.lock
  - justfile
  - platforms/BUILD.bazel
  - tools/bazel/BUILD.bazel
  - tools/bazel/phase2_verify.py
  - tools/bazel/phase42/BUILD.bazel
  - tools/bazel/phase42/arm_link_smoke.bzl
  - tools/bazel/phase42/arm_link_smoke.ld
  - tools/bazel/phase42/arm_link_smoke.rs
  - tools/bazel/phase42/arm_link_smoke_test.py
  - tools/bazel/phase42/capability_gate.bzl
  - tools/bazel/phase42/embedded_toolchain_contract_test.py
  - tools/bazel/phase42/facade_contract_test.py
  - tools/bazel/phase42/graph_isolation_test.py
  - tools/bazel/phase42/host_policy.bzl
  - tools/bazel/phase42/host_policy_contract_test.py
  - tools/bazel/phase42/phase42_test_support.py
  - tools/bazel/phase42/phase42_verify.py
  - tools/bazel/phase42/phase42_verify_test.py
  - tools/bazel/phase42/platform_contract.bzl
  - tools/bazel/phase42/platform_rejection_test.py
  - tools/bazel/phase42/reference_separation_test.py
  - tools/bazel/phase42/toolchain_provenance_test.py
  - tools/bazel/reference_contract.sh
  - tools/bazel/toolchains/BUILD.bazel
  - tools/bazel/toolchains/embedded_repositories.bzl
  - tools/bazel/toolchains/embedded_toolchain.bzl
findings:
  critical: 0
  warning: 4
  info: 0
  total: 4
status: issues_found
---

# Phase 42: Code Review Report

**Reviewed:** 2026-08-03T23:11:56Z
**Depth:** standard
**Files Reviewed:** 30
**Status:** issues_found

## Summary

The Phase 42 Bazel graph, declared toolchain repositories, host policy, ARM link smoke, authority facades, reference routes, and verification tests were reviewed against the repository's Bright Builds architecture, code-shape, testing, and verification standards. The main toolchain declarations and fail-closed embedded qualification path are coherent, but four correctness and verification-coverage gaps remain: the Python provenance audit does not cover all Phase 42 Python entrypoints, its batched result can attribute one valid interpreter to unrelated actions, the simulator reference command is invalid shell syntax, and the advertised Darwin x86_64 host-check path lacks a matching pinned Python toolchain.

The scoped verifier suite passed on Darwin arm64:

```text
bazel test //tools/bazel/phase42:phase42_verifier_tests --nocache_test_results --test_output=errors
Executed 9 out of 9 tests: 9 tests pass.
```

Focused adversarial checks also confirmed that the current Python provenance matcher accepts an unrelated external interpreter when a pinned marker appears elsewhere, and that the exact simulator command exits with shell syntax status 2.

## Warnings

### WR-01: Python provenance verification omits five Phase 42 entrypoints

**File:** `tools/bazel/phase42/graph_isolation_test.py:58-65`

**Issue:** `PYTHON_TEST_TARGETS` contains only six of the Phase 42 Python targets. It omits `facade_contract_tests`, `reference_separation_tests`, `phase42_verify_contract_tests`, `phase42_host_check`, and `phase42_verify`, even though the verifier runs the omitted tests and the two binaries are the user-facing acceptance entrypoints. Those actions can drift to an ambient or differently pinned interpreter without the graph-isolation test noticing, so the claimed Python 3.12.10 provenance guarantee is incomplete.

**Fix:** Include every Phase 42 `py_test` and `py_binary` acceptance target in the audited target set, and add a contract test that compares the audited labels with the Python rules declared in `tools/bazel/phase42/BUILD.bazel` so newly added entrypoints cannot silently escape the audit.

### WR-02: A pinned interpreter in one action masks wrong provenance in another

**File:** `tools/bazel/phase42/graph_isolation_test.py:135-142`

**Issue:** The test runs one batched `aquery` for all targets and passes the entire text to `audit_python_action` for each label. The audit only checks that the target label and the pinned repository marker appear somewhere in that shared text; it never proves they belong to the same action. In addition, `_forbidden_provenance_errors` permits any executable path containing `/external/` or `/execroot/`. A synthetic action graph containing one correctly pinned target and another target using `external/evil_python/bin/python3` returns no errors. This can produce false positive provenance evidence.

**Fix:** Query or parse actions per owner and require every Python action's executable, launcher inputs, and runfiles to reference the exact `rules_python++python+python_3_12_10` repository. Replace the broad `/external/` and `/execroot/` exemption with an allowlist of exact approved repository identities. Add a mutation test where one owner uses a different external Python repository while another owner remains correctly pinned.

### WR-03: The simulator reference route is not executable

**File:** `tools/bazel/reference_contract.sh:47-51`

**Issue:** The execution route invokes `sh -c 'pytest tests/integration --firmware <firmware.bin>'`. The shell parses `<firmware.bin>` as redirection syntax, so the exact command fails with status 2 before pytest starts. The `just reference-simulator` recipe accepts no firmware argument, and the test replaces `sh` with a fake executable, which verifies status propagation but masks the malformed real command. The advertised explicit comparison route therefore cannot perform simulator comparison work.

**Fix:** Make the recipe and Bazel route accept a firmware path, validate that it is non-empty and exists, and pass it as a quoted argument without a placeholder shell expression. For example, route `just reference-simulator path/to/firmware.bin` through `bazel run //tools/bazel:reference_simulator -- "$firmware"`, then execute `pytest tests/integration --firmware "$firmware"`. Keep the placeholder only in the non-executing plan output, and add a test using a fake `pytest` while retaining the real shell.

### WR-04: Darwin x86_64 cannot run the promised host-only diagnostic

**File:** `MODULE.bazel:28-31`

**Issue:** The Python 3.12.10 override provides archives only for Darwin arm64 and Linux x86_64. However, the Phase 42 host policy explicitly registers and tests a Darwin x86_64 qualification toolchain, and `phase42_host_check` is itself a `py_binary`. `rules_python` registers repositories only for platforms present in the override's SHA map, so an Intel Mac has no matching pinned Python toolchain with which to start the host check. Analysis fails before the intended `detected Darwin-x86_64; use canonical Linux x86_64 CI/container` diagnostic can run.

**Fix:** Add the verified `x86_64-apple-darwin` Python 3.12.10 archive checksum to the override and keep it under the same locked URL policy. Add an Intel-Darwin or simulated-platform check that analyzes/runs `//tools/bazel/phase42:phase42_host_check` and asserts the exact unsupported-host remedy.

***

_Reviewed: 2026-08-03T23:11:56Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
