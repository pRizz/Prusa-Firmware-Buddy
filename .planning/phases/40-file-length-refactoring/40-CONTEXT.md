---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T16:44:56.730Z
---

# Phase 40: File Length Refactoring - Context

**Gathered:** 2026-07-27
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Make the managed Bright Builds file-length check green immediately, then eliminate every temporary repo-owned exception through ordered, behavior-preserving refactoring campaigns. Preserve generated and imported sources, retain only the three approved repo-owned permanent exceptions, and finish with zero findings and no temporary exception reasons.

</domain>

<decisions>
## Implementation Decisions

### Exception governance

- **D-01:** Seed `.bright-builds-rules-checks.tsv` with exact-path reasons for the current 933 findings: 838 permanent provenance/declarative entries and 95 temporary repo-owned entries.
- **D-02:** Treat the managed checker and its CI workflow as immutable. Enforce policy through the user-owned exception ledger, stable reason prefixes, documentation, and verification around that interface.
- **D-03:** The temporary owned set is shrink-only. Permanent reclassification is allowed only for `src/guiapi/include/Rect16.h`, `src/connect/planner.cpp`, and `src/gui/screen_tools_mapping.cpp`, each with deletion-test evidence.
- **D-04:** Final acceptance checks the exact permanent path set, not only its count: 841 permanent entries, zero temporary entries, and zero checker findings.

### Deep-module refactoring

- **D-05:** Preserve external interfaces with stable façades while moving implementation into concept-oriented private modules.
- **D-06:** Rust uses the `foo.rs` plus `foo/` layout; Python entrypoints and helpers remain phase-local; C/C++ public headers and symbols remain stable.
- **D-07:** Escalate to a separate internal build target only when a concept has a distinct dependency closure. Temporary compatibility adapters are allowed only for stateful, fail-closed moves and must be removed in the same campaign.
- **D-08:** Every new file stays below 629 physical lines. Each new seam must pass the deletion test and improve depth, leverage, or locality rather than becoming a shallow pass-through.

### Campaign delivery

- **D-09:** Execute in this fixed order: baseline; Rust; utilities; Phase 5–11 Python; Phase 13–17 Python; Phase 18–28 Python; Phase 31–38 Python; firmware tests; parser/UI/protocol/WUI; network/media; persistent storage; hardware/auxiliary; print/safety with `marlin_server.cpp` last.
- **D-10:** Deliver small, reviewable, self-contained changes. Limited parallel preparation is allowed only inside one campaign with non-overlapping files; campaign gates remain serial.
- **D-11:** Remove a temporary exception in the same atomic change that brings the file below the threshold and proves its preserved contract.

### Verification evidence

- **D-12:** Every campaign records affected paths, checker delta, risk class, executed targeted commands, contract comparison, and residual risk.
- **D-13:** Rust commits run `cargo fmt --all`, clippy with warnings denied, all-target/all-feature build, and all-feature tests in that exact order, followed by relevant repository `just` gates.
- **D-14:** High-risk firmware changes require before/after characterization, executed host tests, representative firmware builds, simulator evidence, and hardware-aware review. Physical hardware is required only for behavior changes or simulator coverage gaps.
- **D-15:** A successful wrapper that only prints a reference command is not execution evidence; retained evidence must show that the underlying command ran.

### the agent's Discretion

- Exact private module names and internal helper placement within the locked concept-oriented architecture.
- Whether a campaign needs one plan or several plans, provided the fixed order, file ownership, and verification gates remain intact.
- The smallest repo-owned enforcement helper needed to validate reason syntax and the exact terminal exception set without modifying the managed checker.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and repository constraints

- `.planning/PROJECT.md` — Rust+Bazel migration posture, behavior-parity requirement, safety expectations, and generated/upstream ownership.
- `AGENTS.md` — repository workflow, verification order, generated-file rules, testing conventions, and GSD enforcement.
- `AGENTS.bright-builds.md` — managed Bright Builds workflow and file-length exception interface.
- `standards-overrides.md` — repository-specific standards deviations; no active file-length override is defined.

### Architecture and verification standards

- `standards/core/architecture.md` — functional core, imperative shell, and domain-type guidance.
- `standards/core/code-shape.md` — 628-line refactor trigger, early returns, and script design.
- `standards/core/testing.md` — focused behavior tests with Arrange, Act, Assert.
- `standards/core/verification.md` — sync and affected-path verification requirements.
- `standards/languages/rust.md` — Rust module layout, guard style, and adapter guidance.

### Managed checker interface

- `scripts/bright-builds-check.ts` — authoritative file-length scan, exact-path exception parsing, and stale-exception behavior.
- `.github/workflows/bright-builds-checks.yml` — CI invocation that must remain unchanged.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets

- Existing Rust public modules provide stable façades for private `network/` and `auxiliary/` implementations.
- Phase-local Python helpers such as `tools/bazel/phase32_blocker_normalization.py` and `tools/bazel/phase34_decision_reconciliation.py` demonstrate the intended extraction pattern.
- Existing `just` phase verification targets and Bazel tests provide contract-focused campaign gates.

### Established Patterns

- Python phase entrypoints own CLI and artifact contracts while phase-prefixed siblings hold focused policy.
- C/C++ public headers and target source lists provide stable interfaces while private implementation moves within a subsystem.
- Generated, vendor, HAL, and upstream sources remain intact and are documented through exact exceptions.

### Integration Points

- `.bright-builds-rules-checks.tsv` is the only exception interface consumed by the managed checker.
- `Cargo.toml`, Bazel source lists, CMake target source lists, and phase-local tests must be updated whenever implementation moves.
- `just`, Bazel, host tests, simulator tooling, and representative firmware builds provide progressively stronger evidence by campaign risk.

</code-context>

<specifics>
## Specific Ideas

- Make CI green first, then pay down owned debt without allowing the baseline to grow.
- Split tests by behavior and failure domain before production firmware refactors so they become characterization guards.
- Keep Python policy local to its producing phase; do not create a cross-phase evidence framework.
- Reserve the most stateful and safety-sensitive implementation, especially `src/common/marlin_server.cpp`, for the final campaign.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

*Phase: 40-file-length-refactoring*
*Context gathered: 2026-07-27*
