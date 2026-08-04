---
phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
verified: 2026-08-04T00:05:24Z
status: passed
score: 17/17 must-haves verified
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 42-2026-08-03T19-34-09
generated_at: 2026-08-04T00:05:24Z
lifecycle_validated: true
overrides_applied: 0
---

# Phase 42: Truthful Bazel Graph and Executable MINI Toolchain Verification Report

**Phase Goal:** Developers can select the explicit MINI/BUDDY/STM32F407VG target and trust Bazel and `just` to execute hermetic target work or fail visibly.
**Verified:** 2026-08-04T00:05:24Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

The four roadmap success criteria were merged with the five plans' frontmatter truths. Clear restatements were deduplicated, leaving 17 distinct observable must-haves.

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | All locked Bazel, rules, Rust, Python, Arm GNU, Mini404, and target-triple versions are exact declarations. | ✓ VERIFIED | `.bazelversion`, `MODULE.bazel`, and `embedded_toolchain.bzl` declare Bazel 9.2.0, rules_rust 0.71.3, Rust 1.85.0, rules_cc 0.2.22, rules_python 2.2.0, Python 3.12.10, Arm GNU 13.2.Rel1, Mini404 0.9.10, and `thumbv7em-none-eabihf`; provenance tests passed. |
| 2 | Arm GNU and Mini404 archives have real SHA-256 values and no Darwin, PATH, local-repository, `.dependencies`, Cargo, CMake, fixture, or archive fallback. | ✓ VERIFIED | `embedded_repositories.bzl` contains exact Linux x86_64 URLs, strip prefixes, and 64-hex digests; mutation and action-graph audits passed. |
| 3 | Phase 42 Python evidence uses rules_python Python 3.12.10 and ordinary verification leaves the module lock unchanged. | ✓ VERIFIED | Native Darwin 9-target suite and clean Linux aggregate resolved declared Python 3.12.10. Lock stayed `5b18570e4fa8283ef15c861a3d3a8d5a5d94f1e8b41baf6594e3c3bc16e3d4c9`. |
| 4 | The canonical MINI platform contains exactly embedded + MINI + BUDDY + STM32F407VG + hard-float Rust target constraints. | ✓ VERIFIED | `platforms/BUILD.bazel` and `PHASE42_MINI_CONSTRAINTS` contain the exact five-value allowlist. |
| 5 | Linux x86_64 receives declared embedded executables; Darwin receives non-qualifying host policy only and creates no embedded actions. | ✓ VERIFIED | Toolchain registrations bind Linux executable providers and Darwin policy-only providers. Native Darwin rejection and Darwin x86_64 aquery passed. |
| 6 | Reference metadata, partial constraints, missing executable fields, and unsupported hosts cannot satisfy the qualification provider contract. | ✓ VERIFIED | Embedded/host contract mutation suites passed; reference provider closure contains no `EmbeddedToolchainInfo`. |
| 7 | Canonical Linux builds non-empty Cortex-M4 hard-float ELF, GNU map, and JSON report outputs through resolved Rust and Arm tools. | ✓ VERIFIED | Clean Linux/x86_64 `just phase42-verify` emitted genuine `arm_link_smoke.elf`, `.map`, and `.report.json` paths after two successful smoke builds. |
| 8 | Pinned inspections prove ARM/Cortex-M4, EABI hard-float, FPv4-SP-D16-compatible attributes, and `_phase42_smoke_entry`; metadata alone cannot pass. | ✓ VERIFIED | `arm_link_smoke.bzl` gates the report on readelf, objdump, nm, and size actions; smoke tests and clean Linux aggregate passed. |
| 9 | Darwin exact smoke invocation fails during analysis with detected host/remedy and creates no smoke output. | ✓ VERIFIED | Native Darwin arm64 route exited nonzero with `detected Darwin-arm64; use canonical Linux x86_64 CI/container`; host-policy tests passed. |
| 10 | Only the exact hard-float MINI tuple resolves the positive ARM smoke on canonical Linux x86_64. | ✓ VERIFIED | Exact positive controls passed before and after negative groups in the clean Linux aggregate. |
| 11 | Missing/default, host_tools, all non-MINI products, wrong tuple/triple/ABI, unsupported host, and missing tool selections fail exact targets without skip or fallback. | ✓ VERIFIED | `platform_rejection_tests` exercises 17 nonzero negative cases with `--noskip_incompatible_explicit_targets`; clean Linux aggregate passed. |
| 12 | The successful configured/action graph excludes reference scripts, host Cargo, CMake products, fixtures, archives, `.dependencies`, undeclared tools, and ambient Python. | ✓ VERIFIED | Per-target cquery/aquery graph audit passed on clean Linux, including adversarial interpreter-owner checks. |
| 13 | Stable build/test/package/simulator authority labels fail both `bazel build` and `bazel run` during analysis with owner and working Phase 42 remedy. | ✓ VERIFIED | Public labels are `unavailable_capability` rules with no actions or outputs; facade suite passed on Darwin and in clean Linux aggregate. |
| 14 | CMake/C++ execution and previews use eight explicit reference labels/recipes with fixed semantics unaffected by environment. | ✓ VERIFIED | Four execution plus four `_plan` routes are basename-dispatched; execution/preview status, unknown-name, simulator-argument, closure, and retired-switch tests passed. |
| 15 | The aggregate verifies provenance, lock, smoke, negative matrix, graph, facade, and reference isolation and succeeds only on canonical Linux x86_64. | ✓ VERIFIED | Exact clean `just phase42-verify` exited 0 in Linux/x86_64; native Darwin aggregate exited 1 before positive work. |
| 16 | Darwin smoke, direct authority labels, stable recipes, and aggregate expose one detected-host/Linux-remedy contract without qualification output. | ✓ VERIFIED | `just phase42-host-check` passed all 10 expected-rejection routes on Darwin arm64. |
| 17 | Every Phase 42 Python acceptance entrypoint uses pinned rules_python; direct ambient `phase2_verify.py` cannot qualify. | ✓ VERIFIED | All 11 declared Phase 42 py_test/py_binary targets are audited individually; Darwin x86_64 aquery selected `python_3_12_10_x86_64-apple-darwin`; adversarial owner matcher passed 11 tests. |

**Score:** 17/17 truths verified

### Decision Coverage

| Decision | Status | Verified implementation/evidence |
| --- | --- | --- |
| D-01 | ✓ VERIFIED | Exact version declarations and committed Bzlmod lock. |
| D-02 | ✓ VERIFIED | SHA-backed repositories and forbidden-fallback mutation/action audits. |
| D-03 | ✓ VERIFIED | Linux x86_64 positive boundary; route-complete Darwin expected rejection. |
| D-04 | ✓ VERIFIED | Genuine Rust object → Arm GCC ELF/map → four inspections → report. |
| D-05 | ✓ VERIFIED | `host_tools` remains distinct; canonical embedded allowlist is exactly five constraints. |
| D-06 | ✓ VERIFIED | Every Phase 42 embedded registration/target uses the canonical constraint list. |
| D-07 | ✓ VERIFIED | Exact negative matrix covers missing/default/host/non-MINI/wrong tuple/wrong ABI/missing tools. |
| D-08 | ✓ VERIFIED | Skip-disabled exact targets plus configured/action/provider provenance audits. |
| D-09 | ✓ VERIFIED | Analysis-time public capability gates fail build and run with owner/remedy. |
| D-10 | ✓ VERIFIED | Five focused Phase 42 recipes perform tool resolution, smoke, negative, host, or aggregate work. |
| D-11 | ✓ VERIFIED | Active sources contain no environment-controlled reference semantics; the verifier alone names the retired switch as a forbidden marker. |
| D-12 | ✓ VERIFIED | Explicit reference execution and plan labels/recipes remain usable and non-qualifying. |
| D-13 | ✓ VERIFIED | Historical fixtures are explicitly named and excluded from authority/aggregate provider chains. |
| D-14 | ✓ VERIFIED | Old print-only, fixture, host-Cargo/CMake, ambient-Python, and zero-exit mutations are regression-tested. |
| D-15 | ✓ VERIFIED | Canonical aggregate covers resolution, checksums/lock, real output inspection, negative selection, status propagation, and graph/reference isolation. |

### Required Artifacts

All 22 unique artifacts declared across the five PLAN frontmatter blocks exist and are substantive.

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `.bazelversion` | Exact Bazel pin | ✓ VERIFIED | Exactly `9.2.0` plus newline. |
| `MODULE.bazel` | Rules, Rust target, Python, repository, and registration declarations | ✓ VERIFIED | Exact versions, checksums, use_extension/use_repo, and toolchain registrations. |
| `tools/bazel/toolchains/embedded_repositories.bzl` | Checksum-backed Arm GNU/Mini404 repositories | ✓ VERIFIED | Linux x86_64 only; exact hashes and URLs. |
| `tools/bazel/phase42/toolchain_provenance_test.py` | Version/checksum/fallback/interpreter/lock audit | ✓ VERIFIED | Declared target passed; mutation cases present. |
| `platforms/BUILD.bazel` | Canonical MINI target tuple | ✓ VERIFIED | Five required constraints. |
| `tools/bazel/phase42/platform_contract.bzl` | Central allowlist | ✓ VERIFIED | Exactly five labels. |
| `tools/bazel/phase42/host_policy.bzl` | Qualifying/non-qualifying host contract | ✓ VERIFIED | Linux and both Darwin architectures handled. |
| `tools/bazel/toolchains/embedded_toolchain.bzl` | Executable provider implementations | ✓ VERIFIED | Exec-configured FilesToRunProviders and policy-only Darwin implementation. |
| `tools/bazel/phase42/arm_link_smoke.rs` | Allocation-free no_std entry | ✓ VERIFIED | Non-returning `_phase42_smoke_entry` and panic loop. |
| `tools/bazel/phase42/arm_link_smoke.ld` | FLASH/RAM link contract | ✓ VERIFIED | Explicit entry and sections. |
| `tools/bazel/phase42/arm_link_smoke.bzl` | Compile/link/inspect/report actions | ✓ VERIFIED | Seven distinct target action classes and declared outputs. |
| `tools/bazel/phase42/arm_link_smoke_test.py` | Output/ABI/provenance/host tests | ✓ VERIFIED | Declared suite passed. |
| `tools/bazel/phase42/BUILD.bazel` | Smoke, negative fixtures, rules_python suites, binaries | ✓ VERIFIED | All expected labels are declared. |
| `tools/bazel/phase42/phase42_test_support.py` | Status-preserving subprocess support | ✓ VERIFIED | Captures command/output/real exit status without coercion. |
| `tools/bazel/phase42/platform_rejection_test.py` | Exact negative matrix | ✓ VERIFIED | Skip disabled and positive controls bracket negatives. |
| `tools/bazel/phase42/graph_isolation_test.py` | cquery/aquery/provider/interpreter audit | ✓ VERIFIED | Includes per-target exact interpreter-owner validation and adversarial tests. |
| `tools/bazel/phase42/capability_gate.bzl` | Analysis-time unavailable rule | ✓ VERIFIED | Publishes no actions, outputs, DefaultInfo, or embedded provider. |
| `tools/bazel/phase2_verify.py` | Revised legacy reference/gate expectations | ✓ VERIFIED | Retired switch appears only as a forbidden-string contract. |
| `tools/bazel/phase42/facade_contract_test.py` | Direct Bazel authority regression matrix | ✓ VERIFIED | Uses underscore Bazel labels; hyphenated recipe routes are covered by aggregate tests. |
| `tools/bazel/phase42/reference_separation_test.py` | Fixed reference semantics and isolation | ✓ VERIFIED | Execution, preview, simulator, closure, actions, and runfiles tested. |
| `tools/bazel/phase42/phase42_verify.py` | Canonical aggregate and Darwin host check | ✓ VERIFIED | Ordered Linux evidence and 10-route Darwin rejection logic. |
| `justfile` | Thin stable, Phase 42, and reference recipes | ✓ VERIFIED | `just --list` exposes all required recipes; bodies are Bazel-only. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `MODULE.bazel` | `embedded_repositories.bzl` | Bzlmod extension/repositories | ✓ WIRED | `use_extension` and `use_repo`. |
| Phase 42 BUILD | provenance test | rules_python py_test | ✓ WIRED | Target executed under pinned Python. |
| embedded toolchain | declared repositories | executable labels/providers | ✓ WIRED | Arm/Mini404 plus rules_rust/rules_python inputs. |
| toolchain BUILD | platform contract | exact target compatibility | ✓ WIRED | All three registrations use `PHASE42_MINI_CONSTRAINTS`. |
| `MODULE.bazel` | toolchain BUILD | registered toolchains | ✓ WIRED | Linux and both Darwin implementations registered. |
| smoke rule | qualification toolchain | imported toolchain-type constant and host-policy-first helper | ✓ WIRED | Mechanical pattern missed the imported constant name; manual trace and executed action prove the link. |
| smoke rule | Rust source/linker | Rust compile followed by Arm link | ✓ WIRED | Source/object/ELF/map action inputs and outputs are declared. |
| platform rejection test | exact smoke | skip-disabled exact commands | ✓ WIRED | Clean Linux matrix passed. |
| graph isolation test | exact smoke | cquery/aquery/provider queries | ✓ WIRED | Clean Linux graph audit passed. |
| `justfile` | public Bazel labels | one-command recipes | ✓ WIRED | Real status propagates. |
| public BUILD | capability rule | analysis-time authority gates | ✓ WIRED | All stable authority labels use the rule. |
| aggregate | smoke and focused suites | ordered subprocess orchestration | ✓ WIRED | Exact aggregate passed on Linux. |
| reference separation | legacy verifier/reference surfaces | fixed contract assertions | ✓ WIRED | Declared suite passed. |

### Data-Flow Trace (Level 4)

This phase has no UI/dynamic-data artifact. The equivalent build-evidence flow was traced end to end.

| Artifact | Data/output | Source | Produces real data | Status |
| --- | --- | --- | --- | --- |
| `arm_link_smoke` | Rust object | rules_rust Rust 1.85.0 compiler action | Yes | ✓ FLOWING |
| `arm_link_smoke` | ARM ELF + GNU map | Pinned Arm GNU 13.2.Rel1 GCC link action | Yes | ✓ FLOWING |
| `arm_link_smoke` | ABI/symbol inspection files | Pinned readelf/objdump/nm/size actions | Yes | ✓ FLOWING |
| `arm_link_smoke` | JSON report | Non-empty ELF/map plus all four successful inspections | Yes | ✓ FLOWING |
| `phase42_verify` | Final pass result | Focused suites, real output cquery/files, identity checks, and equal pre/post lock hash | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| All declared Phase 42 acceptance suites | `bazel test //tools/bazel/phase42:phase42_verifier_tests --nocache_test_results --test_output=errors --lockfile_mode=error` | 9/9 passed on Darwin arm64 | ✓ PASS |
| Route-complete unsupported host behavior | `just phase42-host-check` | 10 expected-failure routes rejected; host check exited 0 | ✓ PASS |
| Darwin aggregate cannot qualify | `just phase42-verify` | Exited 1 with detected Darwin-arm64 and Linux remedy | ✓ PASS |
| Canonical positive qualification | Clean `git archive HEAD` in `linux/amd64`, Bazel 9.2.0, exact `just phase42-verify` | Exited 0; all seven aggregate stages passed; genuine output paths and identities emitted | ✓ PASS |
| Darwin x86_64 Python route | `bazel aquery ...phase42_host_check --platforms=...darwin_x86_64_host --output=textproto --lockfile_mode=error` | Analysis passed; pinned `python_3_12_10_x86_64-apple-darwin/bin/python3` selected; no ambient path | ✓ PASS |
| Adversarial parent-relative interpreter owner | `PYTHONPATH=tools/bazel/phase42 python3 -m unittest graph_isolation_test.GraphIsolationMatcherTest` | 11/11 passed, including evil owner and near-match rejection | ✓ PASS |
| Repository/Rust gates | `git diff --check`; Bright Builds; fmt check; strict Clippy; all-target build; all-feature tests | All exited 0; Bright Builds findings=0; Rust tests passed | ✓ PASS |

### Evidence Paths

- Canonical clean-run ELF: `/tmp/phase42-workspace/bazel-out/k8-fastbuild/bin/tools/bazel/phase42/arm_link_smoke.elf` (ephemeral Linux qualification container).
- Canonical clean-run map: `/tmp/phase42-workspace/bazel-out/k8-fastbuild/bin/tools/bazel/phase42/arm_link_smoke.map` (ephemeral Linux qualification container).
- Canonical clean-run report: `/tmp/phase42-workspace/bazel-out/k8-fastbuild/bin/tools/bazel/phase42/arm_link_smoke.report.json` (ephemeral Linux qualification container).
- Durable source and test evidence: `tools/bazel/phase42/`, `MODULE.bazel`, `MODULE.bazel.lock`, `platforms/BUILD.bazel`, `tools/bazel/toolchains/`, `tools/bazel/BUILD.bazel`, and `justfile`.
- Clean final review evidence: `.planning/phases/42-truthful-bazel-graph-and-executable-mini-toolchain/42-REVIEW.md` and `42-REVIEW-FIX.md`.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| BUILD-02 | 42-05 | Named developer commands perform genuine work or fail visibly. | ✓ SATISFIED | Analysis-time gates, facade matrix, native Darwin host check, and clean Linux aggregate. |
| BUILD-03 | 42-02, 42-03, 42-04, 42-05 | Unsupported products/boards/MCUs/targets/hosts fail before fallback. | ✓ SATISFIED | Exact allowlist, 17-case negative matrix, graph/provider isolation, and Darwin policy. |
| BUILD-04 | 42-05 | Separately named CMake/C++ reference path remains usable but non-qualifying. | ✓ SATISFIED | Eight fixed reference labels/recipes and closure/action/runfiles isolation. |
| TOOL-01 | 42-01 through 42-05 | Reproducible pinned/checksummed toolchain without ambient fallback. | ✓ SATISFIED | Exact declarations, lock stability, rules_python provenance, real Linux action graph and outputs. |

No Phase 42 requirement is orphaned: REQUIREMENTS.md maps exactly these four IDs to Phase 42, and each appears in plan frontmatter.

### Anti-Patterns Found

| File | Line/pattern | Severity | Impact |
| --- | --- | --- | --- |
| `graph_isolation_test.py` | `return []` | ℹ️ Info | Legitimate success result for a provider-boundary audit; not a stub. |
| `toolchain_provenance_test.py` | placeholder strings | ℹ️ Info | Deliberate negative mutation fixtures; production hashes are exact. |

No blocker or warning anti-pattern was found. The final code review is clean with 0 critical, 0 warning, and 0 info findings. Source code has not changed since fix commit `1b2a01b2f`; subsequent commits only updated review documentation.

### Human Verification Required

None. Visual, physical-hardware, real simulator behavior, production flashing, release signing, and final firmware behavior are outside Phase 42. Every Phase 42 acceptance behavior is automated.

### Residual Risks and Scope Boundaries

- Native Darwin positive embedded qualification is intentionally unsupported; Darwin evidence is rejection-only. This is a verified phase contract, not a gap.
- The produced ELF is a genuine hard-float link smoke, not the final safe-boot firmware ELF. Runtime ownership and accepted image work remain explicitly assigned to Phases 43-46.
- Mini404 is pinned and present in the qualification provider, but real simulator scenarios remain Phase 48 work.
- The clean Linux run used a cold `linux/amd64` container and took roughly five minutes under emulation; this affects convenience, not correctness.

### Gaps Summary

No actionable gaps remain. All 17 merged must-haves, D-01 through D-15, all 22 required artifacts, all 13 key links, and all four assigned requirements are verified.

***

_Verified: 2026-08-04T00:05:24Z_
_Verifier: the agent (gsd-verifier)_
