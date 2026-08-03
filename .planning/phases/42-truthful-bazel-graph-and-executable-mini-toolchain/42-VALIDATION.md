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
| **Framework** | Bazel analysis/toolchain tests plus focused Python subprocess assertions and pinned Arm binary inspection |
| **Config files** | `.bazelrc`, `MODULE.bazel`, `platforms/BUILD.bazel`, `tools/bazel/toolchains/BUILD.bazel` |
| **Quick run command** | `bazel test //tools/bazel/phase42:phase42_verifier_tests` |
| **Full suite command** | `just phase42-verify` on canonical Linux x86_64 |
| **Estimated runtime** | ~120 seconds excluding first hermetic tool download |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run the focused Bazel/Python test for the changed boundary and a positive MINI control when Linux is available.
- **After every plan wave:** Run `bazel test //tools/bazel/phase42:phase42_verifier_tests` plus the affected `just` facade checks.
- **Before `/gsd-verify-work`:** The repository gates and canonical Linux `just phase42-verify` must be green.
- **Max feedback latency:** 120 seconds after repositories have been populated.

Darwin development may run host/reference checks, but it cannot approve embedded qualification. Embedded authority commands must fail there with the detected host and an actionable Linux CI/container remedy.

______________________________________________________________________

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42-01-01 | 01 | 0 | TOOL-01 | T-42-01 / T-42-02 | Exact checksum-pinned versions resolve without ambient or `.dependencies` fallback | provenance | `bazel test //tools/bazel/phase42:toolchain_provenance_tests` | ❌ W0 | ⬜ pending |
| 42-01-02 | 01 | 1 | TOOL-01 | T-42-01 / T-42-02 | Resolved tools create and inspect a genuine Cortex-M4 hard-float link-smoke output | integration | `bazel build --config=mini --noskip_incompatible_explicit_targets //tools/bazel/phase42:arm_link_smoke` | ❌ W0 | ⬜ pending |
| 42-02-01 | 02 | 1 | BUILD-03 | T-42-03 / T-42-06 | Only the exact MINI/BUDDY/STM32F407VG/hard-float tuple on the supported host resolves | negative integration | `bazel test //tools/bazel/phase42:platform_rejection_tests` | ❌ W0 | ⬜ pending |
| 42-02-02 | 02 | 1 | BUILD-03, TOOL-01 | T-42-02 / T-42-04 | Positive action/provider graph excludes reference, Cargo, CMake, fixtures, archives, and undeclared tools | graph audit | `bazel test //tools/bazel/phase42:graph_isolation_tests` | ❌ W0 | ⬜ pending |
| 42-03-01 | 03 | 1 | BUILD-02 | T-42-04 | Stable authority verbs either do genuine work or fail during analysis with owner and remedy | contract | `bazel test //tools/bazel/phase42:facade_contract_tests` | ❌ W0 | ⬜ pending |
| 42-03-02 | 03 | 1 | BUILD-04 | T-42-04 | Explicit reference execution and preview names cannot satisfy Rust authority gates | contract | `bazel test //tools/bazel/phase42:reference_separation_tests` | ❌ W0 | ⬜ pending |
| 42-03-03 | 03 | 2 | BUILD-02, BUILD-03, BUILD-04, TOOL-01 | T-42-01—T-42-06 | Aggregate verifier reproduces old false positives and proves the complete fail-closed contract | phase integration | `just phase42-verify` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

- [ ] `tools/bazel/phase42/` — minimal ARM link-smoke source/link input and executable Bazel rule/target.
- [ ] Focused subprocess support preserving stdout, stderr, exit status, and exact-target behavior.
- [ ] Fixture platforms/toolchain selections for wrong tuple, triple, ABI, host, and missing-tool failures.
- [ ] Stable `cquery`/`aquery` graph isolation matcher.
- [ ] Analysis-time unavailable-capability rule and build/run contract tests.
- [ ] Aggregate `phase42-verify` Bazel target and `just` recipe.

______________________________________________________________________

## Failure Matrix

Every negative invokes an exact target with `--noskip_incompatible_explicit_targets`, asserts nonzero status, matches an actionable analysis/toolchain diagnostic, and is paired with a positive MINI control:

- missing/default target platform;
- `//platforms:host_tools`;
- every non-MINI product platform;
- wrong printer, board, MCU, target triple, and soft-float ABI;
- unsupported Darwin execution host;
- unavailable Rust, Arm, Python, or Mini404 resolution;
- generic build/test/package/simulator authority labels under both `bazel build` and `bazel run`;
- `just build`, `just test`, `just release-package`, and `just simulator-parity` false-positive regressions.

The harness must fail if Bazel skips the exact target, builds a host variant, copies the known 346-byte fixture, runs CMake/Cargo as authority, or returns zero after printing a command or warning.

______________________________________________________________________

## Threat Model

| Ref | Threat | Mitigation | Required proof |
| --- | --- | --- | --- |
| T-42-01 | Compiler or simulator archive substitution | Exact versions, checksums, and committed lock state | Checksum/lock audit and clean Linux resolution |
| T-42-02 | Ambient/local tool substitution | Toolchain-resolved declared executables only | `aquery` inputs/executables and scrubbed-environment negative |
| T-42-03 | Wrong platform silently accepted | Exact MINI allowlist and fail-closed resolution | Positive/negative platform matrix |
| T-42-04 | Reference or fixture result presented as Rust success | Separate names/providers and graph isolation | Provider/action denylist plus facade regression tests |
| T-42-05 | Tool identity or output cannot be reconstructed | Emit output path, identities, target metadata, and stable lock state | Phase verifier report and lock hash |
| T-42-06 | Unsupported host quietly selects another toolchain | Linux x86_64 execution constraint | Darwin failure with Linux remedy |

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
