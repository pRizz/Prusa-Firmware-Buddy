---
phase: "42"
slug: "truthful-bazel-graph-and-executable-mini-toolchain"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-08-03"
phase_lifecycle_id: "42-2026-08-03T19-34-09"
---

# Phase 42 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

______________________________________________________________________

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Bazel analysis/toolchain tests plus rules_python 3.12.10 `py_test`/`py_binary` subprocess assertions and pinned Arm binary inspection |
| **Config files** | `.bazelrc`, `MODULE.bazel`, `platforms/BUILD.bazel`, `tools/bazel/toolchains/BUILD.bazel` |
| **Quick run command** | `bazel test //tools/bazel/phase42:phase42_verifier_tests` |
| **Full suite command** | `just phase42-verify` on canonical Linux x86_64 |
| **Estimated runtime** | ~120 seconds excluding first hermetic tool download |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run the focused Bazel target for the changed boundary; every Phase 42 Python acceptance surface resolves rules_python 3.12.10, and a positive MINI control runs when Linux is available.
- **After every plan wave:** Run `bazel test //tools/bazel/phase42:phase42_verifier_tests` plus the affected `just` facade checks.
- **Before `/gsd-verify-work`:** The repository gates and canonical Linux `just phase42-verify` must be green.
- **Max feedback latency:** 120 seconds after repositories have been populated.

Darwin development may run host/reference checks, but it cannot approve embedded qualification. A non-qualifying `HostPolicyInfo` contract must make exact smoke, direct build/test/package/simulator labels, all four corresponding stable `just` recipes, and the aggregate fail with detected OS/architecture plus an actionable Linux CI/container remedy; it must never export `EmbeddedToolchainInfo` or enable Darwin target execution.

______________________________________________________________________

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42-01-01 | 01 | 1 | TOOL-01 | T-42-01 / T-42-02 | Exact checksum-pinned module/archive inputs, declared Python 3.12.10, and stable lock state exclude ambient fallback | provenance | `bazel test //tools/bazel/phase42:toolchain_provenance_tests` | ❌ W0 | ⬜ pending |
| 42-02-01 | 02 | 2 | TOOL-01, BUILD-03 | T-42-02 / T-42-03 / T-42-06 | Canonical hard-float platform exists before registration; executable providers are Linux-only while HostPolicyInfo provides deterministic Darwin rejection | analysis contract | `bazel test //tools/bazel/phase42:embedded_toolchain_contract_tests //tools/bazel/phase42:host_policy_contract_tests` | ❌ W0 | ⬜ pending |
| 42-03-01 | 03 | 3 | TOOL-01, BUILD-03 | T-42-02 / T-42-05 / T-42-06 | Resolved Rust and Arm tools create and inspect a genuine Cortex-M4 hard-float link-smoke output | integration | `bazel test //tools/bazel/phase42:arm_link_smoke_tests` | ❌ W0 | ⬜ pending |
| 42-04-01 | 04 | 4 | BUILD-03 | T-42-03 / T-42-06 | Only the exact MINI/BUDDY/STM32F407VG/hard-float tuple on the supported host resolves | negative integration | `bazel test //tools/bazel/phase42:platform_rejection_tests` | ❌ W0 | ⬜ pending |
| 42-04-02 | 04 | 4 | BUILD-03, TOOL-01 | T-42-02 / T-42-04 | Positive action/provider graph excludes forbidden provenance and requires rules_python Python 3.12.10 for every Phase 42 Python action | graph audit | `bazel test //tools/bazel/phase42:graph_isolation_tests` | ❌ W0 | ⬜ pending |
| 42-05-01 | 05 | 5 | BUILD-02, BUILD-03 | T-42-04 / T-42-06 | Authority verbs fail build/run during analysis; Darwin routes use exact HostPolicyInfo diagnostics | contract | `bazel test //tools/bazel/phase42:facade_contract_tests` | ❌ W0 | ⬜ pending |
| 42-05-02 | 05 | 5 | BUILD-04 | T-42-04 | Explicit reference execution and preview names cannot satisfy Rust authority gates | contract | `bazel test //tools/bazel/phase42:reference_separation_tests` | ❌ W0 | ⬜ pending |
| 42-05-03 | 05 | 5 | BUILD-02, BUILD-03, BUILD-04, TOOL-01 | T-42-01—T-42-06 | Declared-Python aggregate reproduces old false positives, proves route-specific Darwin rejection, and completes only on canonical Linux | phase integration | `bazel test //tools/bazel/phase42:phase42_verifier_tests` plus canonical-Linux `just phase42-verify` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

- [ ] Task 42-01-01 creates the provenance test before accepting module/archive declarations.
- [ ] Task 42-02-01 creates the canonical rust-target/MINI constraint and HostPolicyInfo tests before registering executable toolchains; wrong-triple/soft-float fixtures remain absent until Plan 42-04.
- [ ] Task 42-03-01 creates the ARM link-smoke output/host tests before its rule implementation.
- [ ] Task 42-04-01 creates declared-Python status-preserving subprocess support plus wrong-triple/soft-float/tuple/toolchain fixtures without modifying the canonical platform.
- [ ] Task 42-04-02 creates stable `cquery`/`aquery` matcher mutation tests before accepting the graph audit.
- [ ] Task 42-05-01 creates analysis-time build/run contract tests before rewiring authority labels.
- [ ] Task 42-05-02 creates reference naming/provider isolation tests before changing the dispatcher and revises `tools/bazel/phase2_verify.py` expectations.
- [ ] Task 42-05-03 creates aggregate platform-injected tests before wiring `phase42-verify` and the `just` recipes.

______________________________________________________________________

## Failure Matrix

Every negative invokes an exact target with `--noskip_incompatible_explicit_targets`, asserts nonzero status, matches an actionable analysis/toolchain diagnostic, and is paired with a positive MINI control:

- missing/default target platform;
- `//platforms:host_tools`;
- every non-MINI product platform;
- wrong printer, board, MCU, target triple, and soft-float ABI;
- unsupported Darwin x86_64 and arm64 execution hosts through non-qualifying `HostPolicyInfo`, asserting detected OS/architecture and the canonical Linux x86_64 CI/container remedy for exact smoke, direct build/test/package/simulator labels, and all four corresponding stable `just` recipes;
- unavailable Rust, Arm, Python, or Mini404 resolution;
- generic build/test/package/simulator authority labels under both `bazel build` and `bazel run`;
- `just build`, `just test`, `just release-package`, and `just simulator-parity` false-positive regressions.

The harness must fail if Bazel skips the exact target, builds a host variant, copies the known 346-byte fixture, runs CMake/Cargo as authority, or returns zero after printing a command or warning.

______________________________________________________________________

## Qualification Python Contract

- Every Phase 42 `.py` test/helper/verifier that contributes acceptance evidence is declared through rules_python `py_test`, `py_binary`, or a library consumed exclusively by those targets.
- The registered interpreter is Python 3.12.10; `aquery` must positively identify that toolchain/interpreter for every Phase 42 Python action.
- Ambient `python3`, `/usr/bin/python3`, `/usr/local/bin/python3`, `/opt/homebrew`, `env python3`, and PATH interpreter lookup are forbidden in the qualification graph.
- `tools/bazel/phase2_verify.py` may remain directly runnable as a non-authoritative legacy helper, but Phase 42 tests own its revised expectations and the aggregate must not consume its standalone host-Python result.

______________________________________________________________________

## Threat Model

| Ref | Threat | Mitigation | Required proof |
| --- | --- | --- | --- |
| T-42-01 | Compiler or simulator archive substitution | Exact versions, checksums, and committed lock state | Checksum/lock audit and clean Linux resolution |
| T-42-02 | Ambient/local tool or Python interpreter substitution | Toolchain-resolved declared executables plus rules_python Python 3.12.10 only | `aquery` identities/inputs/executables and scrubbed-environment negatives |
| T-42-03 | Wrong platform silently accepted | Exact MINI allowlist and fail-closed resolution | Positive/negative platform matrix |
| T-42-04 | Reference or fixture result presented as Rust success | Separate names/providers and graph isolation | Provider/action denylist plus facade regression tests |
| T-42-05 | Tool identity or output cannot be reconstructed | Emit output path, identities, target metadata, and stable lock state | Phase verifier report and lock hash |
| T-42-06 | Unsupported host quietly selects another toolchain | Linux x86_64 executable constraint plus non-qualifying HostPolicyInfo | Route-complete Darwin OS/architecture failure with Linux remedy and no EmbeddedToolchainInfo |

______________________________________________________________________

## Manual-Only Verifications

All phase behaviors have automated verification. Reviewers still inspect the positive output path and resolved version report, but those values are emitted and asserted by the phase verifier.

______________________________________________________________________

## Repository Boundary Gates

Run in this order before the phase is accepted:

1. `git diff --check`
2. `bun scripts/bright-builds-check.ts all`
3. `cargo fmt --all`
4. `cargo clippy --all-targets --all-features -- -D warnings`
5. `cargo build --all-targets --all-features`
6. `cargo test --all-features`
7. `bazel test //tools/bazel/phase42:phase42_verifier_tests`
8. `just phase42-verify` on canonical Linux x86_64
9. Confirm ordinary verification leaves `MODULE.bazel.lock` unchanged after its intentional update.

______________________________________________________________________

## Validation Sign-Off

- [x] All planned task classes have automated verification or Wave 0 dependencies.
- [x] Sampling continuity: no three consecutive tasks lack automated verification.
- [x] Wave 0 covers every missing test surface.
- [x] No watch-mode flags.
- [x] Expected warm feedback latency is below 120 seconds.
- [x] `nyquist_compliant: true` is set in frontmatter.

**Approval:** approved for planning 2026-08-03; execution approval remains contingent on canonical Linux evidence.
