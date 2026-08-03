---
phase: 42
name: truthful-bazel-graph-and-executable-mini-toolchain
status: researched
researched: 2026-08-03
domain: Bazel Bzlmod, embedded Rust/Arm toolchains, explicit platforms, truthful developer commands
confidence: HIGH
requirements:
  - BUILD-02
  - BUILD-03
  - BUILD-04
  - TOOL-01
phase_lifecycle_id: 42-2026-08-03T19-34-09
---

# Phase 42: Truthful Bazel Graph and Executable MINI Toolchain - Research

<user-constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Hermetic toolchain and host policy

- **D-01:** Pin Bazel 9.2.0, `rules_rust` 0.71.3, Rust 1.85.0, `rules_cc` 0.2.22, `rules_python` 2.2.0, Arm GNU 13.2.Rel1, Mini404 0.9.10, and `thumbv7em-none-eabihf` through declared Bazel/Bzlmod inputs and a committed `MODULE.bazel.lock`.
- **D-02:** Every downloaded archive must have a declared checksum. Rust, Arm GNU, Python, and simulator resolution may not fall back to Cargo product builds, ambient `PATH`, `.dependencies`, CMake outputs, fixtures, archived artifacts, or a different tool version.
- **D-03:** Canonical qualification is Linux x86_64. Darwin may retain separately named host-only checks and CMake reference commands, but Rust embedded build, package, and simulator commands must fail nonzero with the detected host and a Linux CI/container remedy until a verified same-version Darwin toolchain is explicitly added.
- **D-04:** Phase 42 must produce a genuine Cortex-M4 hard-float ARM link-smoke output through the resolved toolchain so executable resolution is proved by target work, not metadata or a version string alone. The smoke output is not the accepted firmware ELF promised by Phase 46.

#### Explicit MINI platform and fail-closed selection

- **D-05:** Preserve `//platforms:host_tools` as a distinct execution surface and make one canonical embedded allowlist tuple authoritative: runtime embedded, printer MINI, board BUDDY, MCU STM32F407VG, and Rust target `thumbv7em-none-eabihf`.
- **D-06:** Constrain every Phase 42 embedded toolchain, smoke target, and downstream firmware-facing facade to that exact tuple. Other existing product platform labels remain descriptive/reference-only and cannot enter the Rust qualification provider chain.
- **D-07:** Missing platform selection, the default host platform, `host_tools`, every non-MINI product platform, wrong product/board/MCU/triple or soft-float combinations, unsupported execution hosts, and missing toolchains must fail during analysis or mandatory toolchain resolution.
- **D-08:** Negative verification must invoke exact targets with incompatible-target skipping disabled and pair each failure case with a positive MINI control. It must also inspect the configured/action graph to prove the successful control does not reach reference scripts, host Cargo, CMake, fixtures, archived outputs, or undeclared local tools.

#### Truthful developer facade and reference separation

- **D-09:** Keep stable developer verbs for build, test, package, and simulator work, but back not-yet-implemented capabilities with analysis-time unavailable-target gates. A gate must fail under both `bazel build` and `bazel run`, name the later owning phase, and point to the genuine Phase 42 smoke/check command that is available now.
- **D-10:** Add narrowly named Phase 42 commands for toolchain resolution, ARM link-smoke, platform negative tests, and the aggregate phase verifier. These commands must perform their named work and expose real output paths.
- **D-11:** Remove `BUDDY_BAZEL_EXECUTE_REFERENCE` as a mode switch for Rust authority labels. One label must never change between print-only, reference execution, and Rust qualification behavior based on environment state.
- **D-12:** Put executable CMake/C++ comparison and rollback commands under explicit `reference-*` Bazel labels and `just` recipes. If print-only command previews remain useful, name them `reference-*-plan`; neither reference execution nor plans may satisfy Rust build, test, package, simulator, or Phase 42 verification gates.
- **D-13:** Fixture-backed Phase 3 package targets and host-workspace Cargo builds remain valid historical/test surfaces only. Production-looking extensions, successful reference builds, or successful host tests cannot count as Phase 42 embedded success.

#### Verification and diagnostics

- **D-14:** The phase verifier must reproduce the current false-positive commands and prove they now either execute genuine Phase 42 work or fail nonzero with actionable diagnostics. Printing a command, emitting metadata only, or building a fixture is an explicit regression failure.
- **D-15:** Verification must cover clean tool resolution, checksums/lockfile stability, positive ARM smoke output inspection, negative platform/host/tool absence cases, facade exit-status propagation, and reference/provider-chain isolation.

### the agent's Discretion

- Exact Starlark rule and provider names, toolchain repository decomposition, Python patch version supported by the selected `rules_python`, mirror ordering, strip prefixes, target labels, and diagnostic wording are flexible when they preserve the locked versions, authority boundaries, failure timing, and negative tests above.
- The planner may choose the smallest robust representation for unavailable capability gates; it must be analysis-time or mandatory-toolchain enforced rather than a runtime dispatcher that builds successfully and only prints an error.

### Deferred Ideas (OUT OF SCOPE)

- Native Darwin embedded build/package/simulator parity is deferred until same-version checksum-verified Arm GNU and Mini404 prerequisites have an explicit support decision.
- Additional printer, board, MCU, or Rust target tuples remain outside v1.4.
- Final safe-boot firmware linking, real package lineage, and real Mini404 scenarios remain owned by Phases 46, 47, and 48 respectively.
</user-constraints>

<phase-requirements>
## Phase Requirements

| ID | Description | Research Support |
| --- | --- | --- |
| BUILD-02 | Developer-facing build, test, package, and simulator commands either perform the named work and emit genuine outputs or exit nonzero with an actionable error. | Replace print-only or fixture-backed authority labels with analysis-time unavailable gates; retain genuine Phase 42 toolchain/link-smoke commands. [VERIFIED: `.planning/REQUIREMENTS.md`, `42-CONTEXT.md` D-09/D-10/D-14] |
| BUILD-03 | Unsupported product, board, MCU, or host combinations fail during Bazel analysis or toolchain resolution without silently selecting a host build, fixture, CMake result, or reference artifact. | Bind the smoke and firmware-facing gates to the exact MINI tuple, test exact targets with `--noskip_incompatible_explicit_targets`, and inspect toolchain/action resolution. [VERIFIED: `.planning/REQUIREMENTS.md`, `42-CONTEXT.md` D-05-D-08] |
| BUILD-04 | Developer can invoke the CMake/C++ reference path through separately named commands and labels that cannot satisfy Rust firmware success criteria. | Split reference execution and command previews into explicitly named labels/recipes and exclude them from the Rust provider and verification chain. [VERIFIED: `.planning/REQUIREMENTS.md`, `42-CONTEXT.md` D-11-D-13] |
| TOOL-01 | Maintainer can reproduce the embedded target with pinned, checksum-verified Rust, Arm GNU, Python, and simulator tools without undeclared `PATH` or `.dependencies` fallback. | Declare exact Bzlmod/archive inputs, commit lock state, run a real hard-float ARM link action, and verify the configured/action graph contains only declared tools. [VERIFIED: `.planning/REQUIREMENTS.md`, `42-CONTEXT.md` D-01-D-04/D-15] |
</phase-requirements>

## Summary

The current Bazel boundary is descriptive rather than executable: Bazel 9.2.0 happens to run without a repository `.bazelversion`, `MODULE.bazel` registers four `reference_toolchain` metadata providers without real module dependencies, and the stable build/test/simulator facades invoke `reference_contract.sh`, which prints commands and exits successfully unless an environment switch is set. The production-looking package facade is worse: `representative_release_artifacts` remains fixture-backed and produces a 346-byte Phase 3 artifact even when host, MK4, or COREONE platforms are selected. [VERIFIED: Phase 42 baseline reproduction; `MODULE.bazel`; `.bazelrc`; `tools/bazel/toolchains/BUILD.bazel`; `tools/bazel/BUILD.bazel`; `tools/bazel/reference_contract.sh`]

Phase 42 should establish one narrow, real vertical slice: a checksum-declared Linux x86_64 Bazel toolchain resolves Rust 1.85.0 for `thumbv7em-none-eabihf` plus Arm GNU 13.2.Rel1 utilities, then creates and inspects a genuine Cortex-M4 hard-float link-smoke output under `//platforms:mini_buddy_stm32f407vg`. Python and Mini404 must also be declared at their locked versions, but the package and simulator product capabilities remain unavailable until Phases 47 and 48. [VERIFIED: `42-CONTEXT.md` D-01-D-10; `.planning/research/STACK.md`; `.planning/ROADMAP.md`]

The core design is fail-closed separation. Firmware-facing labels require an explicit canonical MINI platform and executable toolchains. Unsupported or absent selections fail during analysis/toolchain resolution. Generic `just build`, `just test`, `just release-package`, and `just simulator-parity` remain stable entry points but must fail nonzero with the owning future phase and the available Phase 42 smoke remedy. CMake/C++ reference execution moves to explicitly named `reference-*` labels and recipes; preview-only commands use `reference-*-plan`. [VERIFIED: `42-CONTEXT.md` D-05-D-15]

**Primary recommendation:** Implement the pinned repositories/toolchains and positive MINI ARM link-smoke first, then use the same platform/toolchain contract to make every unsupported selection and not-yet-implemented facade fail before execution. [VERIFIED: `.planning/research/ARCHITECTURE.md`; `42-CONTEXT.md`]

## Current-State Evidence

| Surface | Observed state | Planning consequence |
| --- | --- | --- |
| Bazel version | Bazel 9.2.0 runs, but the repo has no `.bazelversion`. [VERIFIED: Phase 42 baseline reproduction] | Add the repository pin so developer/CI resolution is declared rather than ambient. |
| Bzlmod | `MODULE.bazel` declares only the root module and four local toolchain registrations; it has no `bazel_dep` entries. [VERIFIED: `MODULE.bazel`] | Add exact `rules_rust`, `rules_cc`, and `rules_python` module dependencies and extension/toolchain registration; regenerate and commit the lockfile deliberately. |
| Firmware toolchains | The Rust/C/ASM/asset toolchains return descriptive `reference_toolchain` metadata, not compilers, linkers, or generators. [VERIFIED: `tools/bazel/toolchains/BUILD.bazel`; `.planning/research/FEATURES.md`] | Preserve reference metadata only in a clearly reference-only namespace and introduce executable toolchain types/providers for qualification. |
| Platform model | `//platforms:mini_buddy_stm32f407vg` already carries embedded/MINI/BUDDY/STM32F407VG constraints; `host_tools` and other product platforms also exist. [VERIFIED: `platforms/BUILD.bazel`] | Reuse the MINI label, add the target-triple and supported execution-host constraints needed for exact resolution, and constrain every Phase 42 embedded target. |
| Developer facade | `just build`, `just test`, and `just simulator-parity` route to `reference_contract.sh`; the default branch prints the reference command and returns zero. [VERIFIED: `justfile`; `tools/bazel/BUILD.bazel`; `tools/bazel/reference_contract.sh`; Phase 42 baseline reproduction] | Replace authority labels with unavailable analysis gates and add separate, executable reference labels. |
| Package facade | `just release-package` builds `representative_release_artifacts`, whose Phase 3 rules use fixture payloads and are not constrained to the selected target platform; a 346-byte fixture succeeds under host/MK4/COREONE selections. [VERIFIED: `tools/bazel/BUILD.bazel`; Phase 42 baseline reproduction] | Remove this filegroup from the generic package authority path; keep it historical/test-only and gate package authority until Phase 47. |
| Rust host workflow | `rust_workflow.sh` invokes workspace Cargo for Rust build/test/lint/docs. [VERIFIED: `tools/bazel/rust_workflow.sh`] | Keep host checks available but do not allow them to satisfy embedded toolchain or link-smoke success. |
| Local external tools | Arm GNU and Mini404 are absent from ambient `PATH` but present under `.dependencies`. [VERIFIED: Phase 42 environment audit] | A Phase 42 success on this Darwin host would be a forbidden local fallback; embedded commands must report unsupported Darwin and point to canonical Linux execution. |

## Standard Stack

| Component | Locked version | Phase 42 purpose | Required declaration |
| --- | --- | --- | --- |
| Bazel | 9.2.0 | Authoritative analysis, toolchain resolution, actions, and tests | Repository `.bazelversion`; Bzlmod lock state. [VERIFIED: `42-CONTEXT.md` D-01] |
| `rules_rust` | 0.71.3 | Register Rust 1.85.0 and `thumbv7em-none-eabihf`; compile the smoke input | Exact `bazel_dep`, Rust extension config, registered target toolchain. [VERIFIED: `.planning/research/STACK.md`] |
| Rust | 1.85.0 | Compile the bare-metal hard-float Rust smoke component | Checksum-backed rules_rust toolchain with no Cargo product-build fallback. [VERIFIED: `42-CONTEXT.md` D-01/D-02] |
| `rules_cc` | 0.2.22 | Model native/toolchain integration used by Arm linking | Exact `bazel_dep`; no transitive-version reliance. [VERIFIED: `.planning/research/STACK.md`] |
| Arm GNU | 13.2.Rel1 | Cortex-M4 hard-float assemble/link/inspect tools | Linux x86_64 archive repository with checksum and executable toolchain/provider. [VERIFIED: `42-CONTEXT.md` D-01-D-04] |
| `rules_python` | 2.2.0 | Declared Python host-tool basis for later packager/simulator work and Phase 42 checks | Exact `bazel_dep` and pinned interpreter/toolchain configuration. [VERIFIED: `42-CONTEXT.md` D-01/D-02] |
| Mini404 | 0.9.10 | Declared simulator dependency for the later Phase 48 capability | Checksum-backed Linux x86_64 repository/toolchain surface; no successful simulation claim in Phase 42. [VERIFIED: `42-CONTEXT.md` D-01/D-09; `.planning/ROADMAP.md`] |
| Rust target | `thumbv7em-none-eabihf` | Cortex-M4F hard-float ABI selection | Explicit target constraint and registered Rust target triple. [VERIFIED: `.planning/research/STACK.md`; `42-CONTEXT.md` D-05] |

Do not add a second dependency-resolution plane. Bzlmod and checksum-declared repositories are authoritative; Cargo builds, CMake bootstrap outputs, ambient binaries, `.dependencies`, and archived artifacts are outside the Phase 42 qualification chain. [VERIFIED: `42-CONTEXT.md` D-02; `.planning/research/PITFALLS.md`]

## Architecture Patterns

### 1. Executable toolchain provider, not metadata

Define a small provider that exposes declared Rust/Arm/Python/simulator executables and identity metadata required by actions. Register compatible toolchain implementations against explicit toolchain types. A successful smoke target must consume the resolved toolchain and create a declared output; reading a version string or returning a struct is insufficient. [VERIFIED: `42-CONTEXT.md` D-04/D-10; `.planning/research/ARCHITECTURE.md`]

### 2. One positive platform allowlist

The embedded smoke and every firmware-facing gate must be compatible only with runtime embedded + MINI + BUDDY + STM32F407VG + `thumbv7em-none-eabihf`. The execution toolchain must additionally restrict canonical qualification to Linux x86_64. `host_tools`, default-host selection, other product labels, soft-float, and wrong triples must have no matching embedded toolchain. [VERIFIED: `42-CONTEXT.md` D-03/D-05-D-08]

### 3. Analysis-time capability gates

Represent not-yet-implemented build/test/package/simulator capabilities as rules that fail during analysis, or as targets requiring deliberately unavailable capability toolchains. Their errors must name Phase 46, 43/46, 47, or 48 as appropriate and point to the working Phase 42 link-smoke and verifier. They may not produce an executable whose only behavior is printing an error. [VERIFIED: `42-CONTEXT.md` D-09]

### 4. Names encode evidence class

Use generic names only for Rust authority surfaces. Use `reference-*` for executable CMake/C++ oracle commands and `reference-*-plan` for previews. Keep Phase 3 fixture labels explicitly historical/test-only. No reference or fixture target may return the provider accepted by the Phase 42 verifier or later firmware-facing targets. [VERIFIED: `42-CONTEXT.md` D-11-D-13]

### 5. Verification inspects graph and output

Treat subprocess exit status, platform/toolchain resolution, the configured graph, action inputs/arguments, and binary inspection as separate assertions. A positive control must prove an ARM hard-float output exists at a Bazel-declared path; negative controls must prove the exact target fails rather than being skipped. [VERIFIED: `42-CONTEXT.md` D-08/D-14/D-15]

## Implementation File Map

| File or area | Planned responsibility |
| --- | --- |
| `.bazelversion` | Pin Bazel 9.2.0. [VERIFIED: current file is absent; D-01 requires the pin] |
| `MODULE.bazel`, `MODULE.bazel.lock` | Declare exact rule modules, Rust toolchain/target, checksum-backed external inputs or module extensions, and committed resolution state. [VERIFIED: D-01/D-02] |
| `.bazelrc` | Remove the `BUDDY_BAZEL_EXECUTE_REFERENCE` authority switch; keep explicit `--config=mini`; define only honest host/reference configuration. [VERIFIED: `.bazelrc`; D-03/D-11] |
| `platforms/BUILD.bazel` | Preserve existing product constraints; add target-triple/execution-host constraints if needed; keep the canonical MINI tuple the only embedded allowlist. [VERIFIED: D-05-D-07] |
| `tools/bazel/toolchains/` | Add executable Rust/Arm/Python/Mini404 toolchain repository/configuration and providers; move or clearly retain descriptive providers as reference-only. [VERIFIED: current metadata-only implementation; D-01-D-06] |
| `tools/bazel/phase42/` or equivalent focused package | Own the minimal smoke source/link inputs, declared ARM link-smoke rule/target, binary inspection, unavailable capability rule, and verification tests. Exact names are discretionary. [VERIFIED: D-04/D-09/D-10] |
| `tools/bazel/BUILD.bazel` | Rewire public authority labels to real Phase 42 work or unavailable gates; expose clearly named reference labels; keep fixture targets historical. [VERIFIED: current facade definitions; D-09-D-13] |
| `tools/bazel/reference_contract.sh` | Remove environment-selected behavior from authority routes; retain only explicit reference execution/plan behavior if the script remains. [VERIFIED: current `run_or_print`; D-11/D-12] |
| `justfile` | Keep stable authority verbs, add Phase 42 smoke/toolchain/platform/verifier recipes, and add explicit `reference-*` / `reference-*-plan` recipes. [VERIFIED: D-09/D-10/D-12] |
| `tools/bazel/phase42_verify.py` and focused tests | Orchestrate positive/negative subprocess assertions, graph isolation checks, output inspection, facade regression checks, and lock/checksum checks. Use small helpers and behavior-based tests. [VERIFIED: D-08/D-14/D-15; AGENTS.md testing rules] |

## Don't Hand-Roll

| Problem | Do not build | Use instead | Reason |
| --- | --- | --- | --- |
| Rust compiler/sysroot download | A shell bootstrapper or Cargo wrapper | `rules_rust` Bzlmod toolchain extension with exact Rust/target pins | The toolchain participates in Bazel resolution and declared actions. [VERIFIED: `.planning/research/STACK.md`] |
| Host/product selection | Environment-variable dispatch inside an executable | Bazel platform constraints, target compatibility, and toolchain resolution | Runtime dispatch allows unsupported builds to analyze and appear green. [VERIFIED: D-05-D-09/D-11] |
| Reference/authority mode switch | `BUDDY_BAZEL_EXECUTE_REFERENCE` or equivalent | Separately named labels and recipes | One label must represent one evidence class. [VERIFIED: D-11/D-12] |
| Package placeholder | A tiny `.bbf`/`.bin` copied from fixtures | An unavailable package gate until Phase 47 | File extensions and successful actions are not artifact lineage. [VERIFIED: baseline; D-09/D-13] |
| Simulator placeholder | A printed pytest/Mini404 command | An unavailable simulator gate until Phase 48 | Simulation requires the real accepted image and is out of scope here. [VERIFIED: D-09; Phase 48 roadmap] |
| Tool discovery | `which`, ambient `PATH`, or `.dependencies` probing inside actions | Checksum-declared repositories plus resolved toolchain executables | Local state would violate clean reproducibility and mask missing pins. [VERIFIED: D-02/D-15] |

## Common Pitfalls

### Incompatible targets silently skipped

Wildcard patterns may skip incompatible targets and return zero. Negative tests must invoke exact labels and pass `--noskip_incompatible_explicit_targets`; every negative run needs the positive MINI control in the same verifier. [VERIFIED: D-08]

### Host execution confused with target compilation

Python verifiers and repository helpers execute on the host, while the Rust/Arm output targets the MINI. Keep `//platforms:host_tools` separate and inspect the resolved target and execution platforms; a host Cargo success is never embedded success. [VERIFIED: D-05-D-08/D-13]

### Lockfile drift mistaken for normal operation

Bazel may update `MODULE.bazel.lock` during resolution. Establish the intended lockfile in an explicit update step, then require ordinary verification to leave it byte-for-byte unchanged. [VERIFIED: D-01/D-15; Phase 42 diagnostic observation]

### Metadata/version checks treated as tool execution

A provider containing version strings can pass configuration tests without invoking the compiler or linker. Require an actual target action and inspect its ARM output and action inputs. [VERIFIED: current metadata toolchains; D-04]

### Runtime error wrappers pass `bazel build`

An executable that exits nonzero only when run still makes `bazel build` green. Capability gates must reject both `bazel build` and `bazel run` during analysis or required toolchain resolution. [VERIFIED: D-09]

### Reference or fixture edges leak into authority

A successful CMake command, host Cargo test, or fixture package can look useful enough to reuse. The provider/action-graph isolation test must reject `reference_contract.sh`, `rust_workflow.sh`, CMake, Cargo, fixture paths, archives, and `.dependencies` in the positive embedded chain. [VERIFIED: D-08/D-13-D-15]

### Darwin accidentally qualifies through local tools

The current workstation has bootstrap-managed tools under `.dependencies`, but Phase 42 locks Linux x86_64 as canonical. An unsupported Darwin embedded invocation must fail with the detected host and a Linux remedy; it cannot search local tools or silently select newer versions. [VERIFIED: environment audit; D-02/D-03]

## Project Constraints (from AGENTS.md)

- Bazel is authoritative now; CMake is a separately named reference/comparison path. Preserve behavior while avoiding false parity claims. [VERIFIED: `AGENTS.md` Project constraints]
- Keep `justfile` as the stable discoverable developer interface. [VERIFIED: `AGENTS.md` Project constraints]
- Prefer simple, root-cause changes; fail visibly rather than swallowing command errors. [VERIFIED: `AGENTS.md` Core principles and error handling]
- Use explicit platform/toolchain boundaries and minimal external dependencies. [VERIFIED: `AGENTS.bright-builds.md`; managed architecture/verification standards]
- Unit tests cover one behavior and use Arrange/Act/Assert structure; verify changed behavior, review the diff, and run relevant lint/build/test checks before completion. [VERIFIED: `AGENTS.md` Testing and Verification Before Done]
- Because the repository contains `Cargo.toml`, any commit containing Rust changes requires, in order, `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`. [VERIFIED: `AGENTS.md` Rust pre-commit requirements]
- Run `bun scripts/bright-builds-check.ts all` as the managed repository standards gate. [VERIFIED: managed block in `AGENTS.md`]

## Environment Availability

| Dependency | Required by | Available in ambient `PATH` | Required Phase 42 disposition |
| --- | --- | --- | --- |
| Bazel 9.2.0 | Analysis/actions | Yes, but not repo-pinned | Add `.bazelversion`; do not treat ambient resolution as the declaration. [VERIFIED: baseline] |
| Arm GNU 13.2.Rel1 | ARM link-smoke | No | Resolve checksum-backed from Bazel on canonical Linux; `.dependencies` is forbidden. [VERIFIED: environment audit; D-02] |
| Mini404 0.9.10 | Declared simulator tool surface | No | Resolve checksum-backed on canonical Linux; Phase 42 does not claim a simulator run. [VERIFIED: environment audit; D-01/D-09] |
| Rust 1.85.0 target toolchain | Rust smoke input | Must not be sourced from ambient Cargo/rustup | Resolve through the pinned `rules_rust` toolchain and exact target triple. [VERIFIED: D-01/D-02] |
| Python toolchain | Verifier and future host tools | Ambient Python exists but cannot be qualification authority | Register the pinned Bazel Python toolchain; keep verifier host execution declared. [VERIFIED: D-01/D-02] |

**Blocking local condition:** This Darwin host is not a qualifying embedded execution host under D-03. The implementation and host/reference tests may be developed here, but the positive embedded toolchain/link-smoke gate must run on canonical Linux x86_64; Darwin authority commands must fail with a Linux CI/container remedy. [VERIFIED: D-03]

## Validation Architecture

### Test Framework

| Property | Value |
| --- | --- |
| Framework | Bazel analysis/toolchain resolution plus focused Python subprocess tests and ARM binary inspection |
| Config files | `.bazelrc`, `MODULE.bazel`, `platforms/BUILD.bazel`, `tools/bazel/toolchains/BUILD.bazel` |
| Quick positive command | `bazel build --config=mini --noskip_incompatible_explicit_targets //tools/bazel/phase42:arm_link_smoke` |
| Quick test command | `bazel test //tools/bazel/phase42:phase42_verifier_tests` |
| Full phase command | `just phase42-verify` |

Exact target names may change at planning time, but the command classes and evidence below are mandatory. [VERIFIED: D-10; names are agent discretion]

### Requirement-to-Test Map

| Req ID | Behavior | Automated evidence | File exists? |
| --- | --- | --- | --- |
| TOOL-01 | Exact pinned repositories/toolchains resolve without `PATH`, `.dependencies`, Cargo/CMake, fixture, or archive fallback. | Clean Linux resolution; declared-checksum audit; stable lockfile hash; `cquery`/`aquery` toolchain and input inspection; real link action. | No - Wave 0 |
| BUILD-03 | Only the explicit MINI/BUDDY/STM32F407VG/hard-float target and supported Linux execution host resolve. | Positive MINI control plus exact-target failures for missing/default/host_tools/MK4/COREONE/XL/wrong tuple/wrong triple/soft-float/unsupported host/missing toolchain, all with `--noskip_incompatible_explicit_targets`. | No - Wave 0 |
| BUILD-02 | Generic commands either do real named work or fail nonzero with actionable ownership/remedy. | Subprocess tests for both `bazel build` and `bazel run` gates plus `just build`, `just test`, `just release-package`, and `just simulator-parity`; reject print-only success and tiny fixture outputs. | No - Wave 0 |
| BUILD-04 | Reference execution/previews remain usable but cannot satisfy Rust gates. | Run separately named reference plan/execution labels where host-supported; inspect provider/action graph to show zero path into ARM smoke/phase verifier. | No - Wave 0 |

### Positive MINI Link-Smoke

1. On Linux x86_64, build the exact smoke label with `--config=mini --noskip_incompatible_explicit_targets`.
2. Assert the selected target platform contains embedded/MINI/BUDDY/STM32F407VG/`thumbv7em-none-eabihf` and the execution toolchain identifies the locked versions.
3. Require a declared, non-empty output whose creation action invokes the resolved Rust/Arm toolchain rather than a copy/metadata action.
4. Inspect with the pinned Arm tools: machine is ARM, CPU attributes are Cortex-M4-compatible, and hard-float/FPv4-SP-D16 attributes match the target contract. Record the Bazel output path and tool identities without calling the output a Phase 46 firmware ELF.
5. Rerun the positive control after the negative matrix to prove the test harness itself did not merely break resolution.

[VERIFIED: D-04/D-08/D-10/D-15; `.planning/research/STACK.md`]

### Fail-Closed Platform and Toolchain Negatives

For each case, invoke the exact smoke or firmware-facing target with `--noskip_incompatible_explicit_targets`, assert nonzero exit, and match an actionable analysis/toolchain diagnostic:

- no `--platforms`/default host selection;
- `//platforms:host_tools`;
- every non-MINI product platform currently declared (`mk4`, `coreone`, `xl`, xBuddy extension, and any other descriptive platform);
- a fixture wrong-printer, wrong-board, wrong-MCU, wrong-target-triple, and soft-float platform;
- unsupported Darwin embedded execution host;
- intentionally unavailable Rust, Arm, Python, or Mini404 toolchain/repository selection.

The test must fail if Bazel skips the target, builds a host variant, copies a fixture, runs CMake/Cargo, or returns zero after printing a warning. [VERIFIED: D-07/D-08/D-14/D-15]

### Action Graph and Provider Isolation

- Use `cquery` to assert the configured target/platform/toolchain identities of the positive control.
- Use `aquery` to capture the smoke action inputs, executable paths, arguments, and outputs.
- Reject forbidden provenance markers in the positive chain: `reference_contract.sh`, `rust_workflow.sh`, `cargo build`, `utils/build.py`, CMake product outputs, `tools/bazel/fixtures`, `.planning/archive`, `.dependencies`, and undeclared absolute tool paths.
- Require the smoke/qualification provider only from executable embedded toolchain targets; reference and fixture targets must not export it.
- Inspect generic unavailable-gate labels to ensure no executable/file output can masquerade as completion.

[VERIFIED: D-08/D-13-D-15]

### Truthful Facade and Reference Separation

- For `build`, `test`, `release-package`, and `simulator-parity`, test the direct Bazel label under both `bazel build` and `bazel run`, then test the corresponding `just` recipe. Until later phases land, all must exit nonzero during analysis/toolchain resolution, name the owning phase, and point to the Phase 42 smoke/verifier.
- Assert output is not only a `reference command:` line and that package routes do not emit the known 346-byte fixture or any Phase 3 fixture lineage.
- Test explicit `reference-build`, `reference-test`, and related labels/recipes independently. If plan-only previews remain, require `reference-*-plan` naming and do not count their success in the Phase 42 result.
- Verify `BUDDY_BAZEL_EXECUTE_REFERENCE` no longer changes authority-label semantics.

[VERIFIED: baseline; D-09-D-14]

### Repository and Rust Gates

Run at the phase boundary:

1. `git diff --check`
2. `bun scripts/bright-builds-check.ts all`
3. `cargo fmt --all`
4. `cargo clippy --all-targets --all-features -- -D warnings`
5. `cargo build --all-targets --all-features`
6. `cargo test --all-features`
7. `bazel test //tools/bazel/phase42:phase42_verifier_tests`
8. `just phase42-verify` on canonical Linux x86_64
9. Confirm `MODULE.bazel.lock` is unchanged by ordinary verification after the intentional lock update.

[VERIFIED: AGENTS.md; D-15]

### Sampling Rate

- **Per task commit:** focused Bazel/Python test for the changed boundary plus the positive MINI control where Linux is available.
- **Per wave:** complete Phase 42 Bazel test suite and affected `just` facade checks.
- **Phase gate:** all repository/Rust gates plus canonical Linux `just phase42-verify`, graph isolation, negative matrix, and stable lockfile.

### Wave 0 Gaps

- [ ] Minimal ARM link-smoke source/link input and executable Bazel rule/target.
- [ ] Focused subprocess test support that preserves stdout, stderr, and exit status for exact-target assertions.
- [ ] Fixture platforms/toolchain selections for wrong tuple, wrong triple, soft-float, and missing-tool cases.
- [ ] Graph-isolation allow/deny matcher over stable `cquery`/`aquery` output.
- [ ] Analysis-time unavailable capability rule and tests for both build and run.
- [ ] Aggregate `phase42-verify` label and `just` recipe.

## Security Domain

Phase 42 is a build-supply-chain boundary. Authentication, sessions, and application access control are not present. Input validation and integrity controls apply to platform selection, archive identity, and executable provenance. [VERIFIED: phase scope; security enforcement enabled at ASVS Level 1]

| ASVS category | Applies | Phase control |
| --- | --- | --- |
| V2 Authentication | No | No user/authentication surface in the build graph. |
| V3 Session Management | No | No session state. |
| V4 Access Control | No | No application authorization decision; repository/CI permissions remain outside this phase. |
| V5 Validation, Sanitization, Encoding | Yes | Exact allowlisted platform/target/toolchain constraints; reject missing, malformed, unsupported, and soft-float selections during analysis. |
| V6 Stored Cryptography | Integrity only | SHA-256/integrity declarations for every downloaded archive and stable lockfile; do not invent custom cryptography. |
| V14 Configuration | Yes | Pinned versions, no environment-controlled authority switch, fail-closed host policy, declared action inputs. |

### Threat Model

| Threat | STRIDE class | Mitigation | Required verification |
| --- | --- | --- | --- |
| Substituted compiler/simulator archive | Tampering | Exact versions plus declared archive checksums and lockfile | Checksum/lock audit; clean Linux resolution |
| Ambient/local tool substitution | Tampering/Elevation | Toolchain-resolved executables only; no `PATH` or `.dependencies` fallback | `aquery` executable/input inspection; scrubbed-environment negative |
| Wrong platform silently accepted | Spoofing/Tampering | Exact MINI allowlist and incompatible exact-target failures | Positive/negative platform matrix |
| Reference or fixture result presented as Rust success | Spoofing/Repudiation | Separate names/providers and graph isolation | Provider/action denylist and facade regression tests |
| Tool identity/output cannot be reconstructed | Repudiation | Emit output path and resolved version/target metadata; stable lock state | Phase verifier report and lock hash |
| Unsupported host quietly uses a different toolchain | Tampering | Linux x86_64 canonical constraint; actionable Darwin failure | Unsupported-host test |

Every implementation plan for this phase should include this threat model or a narrower equivalent and must block HIGH-severity integrity or authority leaks before completion. [VERIFIED: Phase planning security gate configuration]

## Assumptions Log

No unverified assumptions are required. Exact Starlark/provider names, repository decomposition, Python patch version, mirror ordering, strip prefixes, labels, and diagnostic wording remain implementation discretion explicitly granted by `42-CONTEXT.md`; the planner should choose them without changing the locked evidence contract.

## Open Questions

None that require user input before planning. Implementation may determine the smallest stable Starlark decomposition and exact Python patch release compatible with the locked `rules_python` version, but those are delegated choices bounded by the checksum, host, and no-fallback rules. [VERIFIED: `42-CONTEXT.md` agent discretion]

## Sources

### Primary repository evidence (HIGH confidence)

- `42-CONTEXT.md` - locked decisions, boundary, reference separation, verification requirements.
- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` - BUILD-02/03/04, TOOL-01, Phase 42 success criteria, and later-phase ownership.
- `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelrc`, `platforms/BUILD.bazel` - current dependency, lock, config, and platform surfaces.
- `tools/bazel/toolchains/BUILD.bazel` and `tools/bazel/toolchains/reference_toolchain.bzl` - metadata-only toolchain pattern.
- `tools/bazel/BUILD.bazel`, `tools/bazel/reference_contract.sh`, `tools/bazel/rust_workflow.sh`, `justfile` - current facade, fixture, reference-mode, and host-Cargo boundaries.
- Phase 42 baseline reproduction - false-positive build/test/simulator commands, fixture package result, and environment availability.

### Previously verified official-source synthesis (HIGH confidence)

- `.planning/research/STACK.md` - Bzlmod pins, `rules_rust` target toolchain configuration, Arm hard-float flags, host constraints, and official source links.
- `.planning/research/ARCHITECTURE.md` - executable toolchain boundary, provider/action ownership, and phase ordering.
- `.planning/research/FEATURES.md` - present repository gaps and required capability set.
- `.planning/research/PITFALLS.md` - hermeticity, ABI/platform drift, false authority, and fail-closed verification risks.
- [Bazel platforms and toolchains](https://bazel.build/concepts/platforms) - target/execution platforms and toolchain resolution.
- [rules_rust Bzlmod toolchains](https://bazelbuild.github.io/rules_rust/rust_bzlmod.html) - exact Rust version and extra target registration.
- [Rust Armv7E-M target support](https://doc.rust-lang.org/stable/rustc/platform-support/thumbv7em-none-eabi.html) - Cortex-M4F hard-float target contract.
- [Arm GNU Toolchain downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) - official 13.2.Rel1 toolchain family.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - versions and host/ABI policy are locked in context and backed by prior official-source research.
- Architecture: HIGH - current repository boundaries and false-positive behavior were directly inspected and reproduced.
- Validation: HIGH - every requirement maps to positive, negative, graph, facade, and repository gates.
- Simulator execution details: not researched for this phase because real Mini404 behavior belongs to Phase 48.

**Research date:** 2026-08-03  
**Valid until:** 2026-09-02, or earlier if the locked Bazel/rules/tool versions change.
