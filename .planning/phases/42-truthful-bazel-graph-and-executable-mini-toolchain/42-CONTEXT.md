---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 42-2026-08-03T19-34-09
generated_at: 2026-08-03T19:34:29.384Z
---

# Phase 42: Truthful Bazel Graph and Executable MINI Toolchain - Context

**Gathered:** 2026-08-03
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 42 replaces the descriptive and print-only Bazel boundary with a hermetic, executable toolchain and one explicit `MINI/BUDDY/STM32F407VG` target-selection contract. It makes developer-facing build, test, package, and simulator verbs truthful: each command either performs work that is genuinely available in this phase or fails nonzero with an actionable diagnostic.

This phase does not claim the final safe-boot firmware link, artifact family, or Mini404 behavior owned by Phases 46-48. It establishes the pinned toolchain, real ARM link-smoke proof, platform rejection rules, stable capability gates, and separately named CMake/C++ reference oracle those later phases extend.

</domain>

<decisions>
## Implementation Decisions

### Hermetic toolchain and host policy

- **D-01:** Pin Bazel 9.2.0, `rules_rust` 0.71.3, Rust 1.85.0, `rules_cc` 0.2.22, `rules_python` 2.2.0, Arm GNU 13.2.Rel1, Mini404 0.9.10, and `thumbv7em-none-eabihf` through declared Bazel/Bzlmod inputs and a committed `MODULE.bazel.lock`.
- **D-02:** Every downloaded archive must have a declared checksum. Rust, Arm GNU, Python, and simulator resolution may not fall back to Cargo product builds, ambient `PATH`, `.dependencies`, CMake outputs, fixtures, archived artifacts, or a different tool version.
- **D-03:** Canonical qualification is Linux x86_64. Darwin may retain separately named host-only checks and CMake reference commands, but Rust embedded build, package, and simulator commands must fail nonzero with the detected host and a Linux CI/container remedy until a verified same-version Darwin toolchain is explicitly added.
- **D-04:** Phase 42 must produce a genuine Cortex-M4 hard-float ARM link-smoke output through the resolved toolchain so executable resolution is proved by target work, not metadata or a version string alone. The smoke output is not the accepted firmware ELF promised by Phase 46.

### Explicit MINI platform and fail-closed selection

- **D-05:** Preserve `//platforms:host_tools` as a distinct execution surface and make one canonical embedded allowlist tuple authoritative: runtime embedded, printer MINI, board BUDDY, MCU STM32F407VG, and Rust target `thumbv7em-none-eabihf`.
- **D-06:** Constrain every Phase 42 embedded toolchain, smoke target, and downstream firmware-facing facade to that exact tuple. Other existing product platform labels remain descriptive/reference-only and cannot enter the Rust qualification provider chain.
- **D-07:** Missing platform selection, the default host platform, `host_tools`, every non-MINI product platform, wrong product/board/MCU/triple or soft-float combinations, unsupported execution hosts, and missing toolchains must fail during analysis or mandatory toolchain resolution.
- **D-08:** Negative verification must invoke exact targets with incompatible-target skipping disabled and pair each failure case with a positive MINI control. It must also inspect the configured/action graph to prove the successful control does not reach reference scripts, host Cargo, CMake, fixtures, archived outputs, or undeclared local tools.

### Truthful developer facade and reference separation

- **D-09:** Keep stable developer verbs for build, test, package, and simulator work, but back not-yet-implemented capabilities with analysis-time unavailable-target gates. A gate must fail under both `bazel build` and `bazel run`, name the later owning phase, and point to the genuine Phase 42 smoke/check command that is available now.
- **D-10:** Add narrowly named Phase 42 commands for toolchain resolution, ARM link-smoke, platform negative tests, and the aggregate phase verifier. These commands must perform their named work and expose real output paths.
- **D-11:** Remove `BUDDY_BAZEL_EXECUTE_REFERENCE` as a mode switch for Rust authority labels. One label must never change between print-only, reference execution, and Rust qualification behavior based on environment state.
- **D-12:** Put executable CMake/C++ comparison and rollback commands under explicit `reference-*` Bazel labels and `just` recipes. If print-only command previews remain useful, name them `reference-*-plan`; neither reference execution nor plans may satisfy Rust build, test, package, simulator, or Phase 42 verification gates.
- **D-13:** Fixture-backed Phase 3 package targets and host-workspace Cargo builds remain valid historical/test surfaces only. Production-looking extensions, successful reference builds, or successful host tests cannot count as Phase 42 embedded success.

### Verification and diagnostics

- **D-14:** The phase verifier must reproduce the current false-positive commands and prove they now either execute genuine Phase 42 work or fail nonzero with actionable diagnostics. Printing a command, emitting metadata only, or building a fixture is an explicit regression failure.
- **D-15:** Verification must cover clean tool resolution, checksums/lockfile stability, positive ARM smoke output inspection, negative platform/host/tool absence cases, facade exit-status propagation, and reference/provider-chain isolation.

### the agent's Discretion

- Exact Starlark rule and provider names, toolchain repository decomposition, Python patch version supported by the selected `rules_python`, mirror ordering, strip prefixes, target labels, and diagnostic wording are flexible when they preserve the locked versions, authority boundaries, failure timing, and negative tests above.
- The planner may choose the smallest robust representation for unavailable capability gates; it must be analysis-time or mandatory-toolchain enforced rather than a runtime dispatcher that builds successfully and only prints an error.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and requirements

- `.planning/PROJECT.md` - v1.4 development-only MINI bring-up scope, Bazel authority, `justfile`, and reference-demotion boundaries.
- `.planning/REQUIREMENTS.md` - BUILD-02, BUILD-03, BUILD-04, and TOOL-01 acceptance requirements and explicit exclusions.
- `.planning/ROADMAP.md` - Phase 42 boundary, success criteria, and ownership split across Phases 43-49.
- `.planning/STATE.md` - Current milestone position and unresolved later-phase research gates.

### v1.4 research

- `.planning/research/SUMMARY.md` - selected versions, target ABI, phase ordering, and Linux-canonical qualification direction.
- `.planning/research/STACK.md` - Bzlmod/toolchain configuration, declared download policy, target flags, host constraints, and smoke/artifact graph.
- `.planning/research/FEATURES.md` - observed print-only and fixture-backed baseline plus truthful-command table stakes.
- `.planning/research/PITFALLS.md` - host/ABI drift, non-hermetic wrapper, false authority, and negative-test requirements.
- `.planning/research/ARCHITECTURE.md` - Bazel ownership, CMake reference separation, and the boundary between Phase 42 toolchain proof and later firmware work.

### Existing authority surfaces

- `.planning/milestones/v1.0-phases/02-bazel-authority-and-developer-facade/02-CONTEXT.md` - stable facade and explicit platform decisions whose metadata-only and dry-run allowances Phase 42 now retires.
- `MODULE.bazel` - current root Bzlmod entrypoint and metadata-toolchain registration.
- `MODULE.bazel.lock` - current dependency lock surface that must become the checksum-backed toolchain record.
- `.bazelrc` - current host/product configs and reference-execution environment switch.
- `platforms/BUILD.bazel` - existing runtime/printer/board/MCU constraints and product platform labels.
- `tools/bazel/toolchains/BUILD.bazel` - metadata-only Rust/C/ASM/asset toolchains to separate from executable toolchains.
- `tools/bazel/toolchains/reference_toolchain.bzl` - descriptive provider that must remain reference-only.
- `tools/bazel/reference_contract.sh` - current `run_or_print` false-success boundary and environment-controlled authority switch.
- `tools/bazel/rust_workflow.sh` - current host Cargo workflow that cannot prove embedded target execution.
- `tools/bazel/BUILD.bazel` - current facade labels, fixture artifact labels, and integration points.
- `justfile` - stable developer recipe surface and current false-positive build/test/simulator routes.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets

- `//platforms:mini_buddy_stm32f407vg`: already models the required runtime/product/board/MCU tuple and should remain the canonical selection label.
- `.bazelrc` named configs: provide stable config names that can be narrowed to supported authority classes.
- `tools/bazel/shell_rules.bzl`: existing repo-owned executable rule support can remain for thin host tools when it does not hide target work.
- `tools/bazel/phase2_verify.py`: useful historical graph/facade checks that can inform, but not substitute for, Phase 42 execution and negative tests.

### Established Patterns

- Root `justfile` recipes already delegate to Bazel labels; preserve that thin facade while changing the labels from print-only/fixture-backed behavior to real work or hard failure.
- The repository uses explicit platform constraints for runtime, printer, board, and MCU, but the registered firmware toolchains currently return descriptive metadata only.
- Rust workflow labels currently run Cargo against the host workspace; this remains a host-test surface and is not an embedded firmware proof.

### Integration Points

- Replace root module/toolchain registrations in `MODULE.bazel` and `tools/bazel/toolchains/` while keeping reference providers in a visibly separate namespace.
- Tighten target compatibility and command routes across `.bazelrc`, `platforms/BUILD.bazel`, `tools/bazel/BUILD.bazel`, and `justfile`.
- Extend verification under `tools/bazel/` with a real ARM link-smoke and exact negative selection/fallback cases.

</code-context>

<specifics>
## Specific Ideas

- Preserve familiar `just build`, `just test`, package, and simulator verbs, but prefer a clear nonzero “capability lands in Phase 46/47/48” error over a temporary green placeholder.
- A passing smoke target should identify the exact Bazel target, target triple, selected platform, resolved tool versions, and real output path without suggesting that the safe-boot firmware itself already exists.
- Reference execution and reference command previews are both useful, but their names must make their evidence class impossible to confuse with Rust qualification.

</specifics>

<deferred>
## Deferred Ideas

- Native Darwin embedded build/package/simulator parity is deferred until same-version checksum-verified Arm GNU and Mini404 prerequisites have an explicit support decision.
- Additional printer, board, MCU, or Rust target tuples remain outside v1.4.
- Final safe-boot firmware linking, real package lineage, and real Mini404 scenarios remain owned by Phases 46, 47, and 48 respectively.

</deferred>

***

*Phase: 42-truthful-bazel-graph-and-executable-mini-toolchain*
*Context gathered: 2026-08-03*
