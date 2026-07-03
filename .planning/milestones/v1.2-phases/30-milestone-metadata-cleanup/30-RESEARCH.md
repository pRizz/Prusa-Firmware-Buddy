# Phase 30: Milestone Metadata Cleanup - Research

**Researched:** 2026-06-26 [VERIFIED: environment current date]
**Domain:** GSD milestone metadata, summary frontmatter extraction, verification-report normalization, and milestone audit closure [VERIFIED: .planning/ROADMAP.md; .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]
**Confidence:** HIGH [VERIFIED: local file reads; gsd-tools command output; GSD helper source inspection]

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### State Metadata Consistency
- **D-01:** Refresh `.planning/STATE.md` so frontmatter, progress counts, current position, recent trend, stopped-at text, and session continuity agree with the roadmap and completed Phase 23-29 artifacts.
- **D-02:** Preserve the milestone's external-evidence boundaries while cleaning stale prose. State text may say v1.2 is ready for archival after Phase 30, but it must not imply real simulator, hardware, live-service, release, retained-code, final-readiness, or demotion inputs have been supplied when they remain external maintainer/operator inputs.

### Summary Extraction Contract
- **D-03:** Resolve the `summary-extract --fields requirements_completed` drift before archival. Prefer the smallest durable repo-local fix that makes current completion metadata unambiguous for milestone review.
- **D-04:** If the GSD helper itself cannot be changed inside this repository, update milestone/audit documentation so direct summary frontmatter parsing is the authoritative source and `summary-extract` is not treated as the sole requirement-completion source.
- **D-05:** Any metadata normalization must avoid broad historical rewrites. Touch only the current v1.2 summaries or docs needed to prove the Phase 30 success criterion.

### Phase 25 Verification Shape
- **D-06:** Expand `.planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md` into the same audit-friendly shape used by the other v1.2 verification reports, including explicit requirement coverage for `EVID-03`, command evidence, and residual-risk boundaries.
- **D-07:** Keep Phase 25's substantive verification status unchanged. The cleanup should clarify evidence shape, not alter the passed result or claim real live-service proof beyond the existing safe fixture and blocked-placeholder boundaries.

### Audit Closure
- **D-08:** Produce a fresh milestone audit after metadata cleanup. The closure proof is a current audit report with no critical gaps and no contradictory stale metadata.
- **D-09:** The final audit may still name intentional external evidence boundaries, but Phase 30 should eliminate the known TD-1 through TD-4 archival blockers or explicitly document any durable local exception.

### the agent's Discretion
- Choose whether to fix extraction by metadata normalization, audit wording, or a narrow helper-compatible bridge, provided the final command/audit evidence is reproducible.
- Choose exact wording for refreshed state and verification reports, keeping edits localized and source-backed.
- Choose the smallest verification command set that proves this metadata-only phase without rerunning unrelated firmware or external-service suites.

### Deferred Ideas (OUT OF SCOPE)
- Updating global GSD helper code outside this repository is out of scope for the repo commit unless the user explicitly asks for a GSD tool fix.
- Milestone archival itself remains a later `/gsd-complete-milestone` action after Phase 30 passes verification.
- Real external evidence acquisition and reference demotion approval remain maintainer/operator actions, not Phase 30 metadata cleanup work.
</user_constraints>

## Summary

Phase 30 is a metadata-only cleanup phase; it should modify planning artifacts and current v1.2 summary frontmatter, not firmware source, evidence generators, or the installed GSD helper under `$HOME/.codex/get-shit-done`. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md; /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs]

The highest-confidence implementation path is a localized compatibility bridge: keep existing `requirements_completed` frontmatter, add missing `requirements-completed` aliases to current v1.2 requirement-bearing summaries, add the missing underscore alias to Phase 27, and verify both direct frontmatter review and `summary-extract --fields requirements_completed --pick requirements_completed`. [VERIFIED: summary-extract command output; /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs; .planning/v1.2-MILESTONE-AUDIT.md]

The planner should then refresh `.planning/STATE.md`, expand Phase 25 verification into the Phase 23/24/26/27/28 audit-friendly shape, rerun or refresh the milestone audit so TD-1 through TD-4 are closed, and keep all external evidence boundaries explicit. [VERIFIED: .planning/STATE.md; .planning/phases/23-simulator-evidence-execution/23-VERIFICATION.md; .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md; .planning/v1.2-MILESTONE-AUDIT.md]

**Primary recommendation:** Use a repo-local dual-key summary frontmatter bridge plus documentation cleanup; do not edit the installed GSD helper in this phase. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md; /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs]

## Project Constraints (from AGENTS.md)

- Follow `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant standards pages before planning, implementation, review, or audit work. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md; standards/index.md]
- Use GSD workflows before file-changing work unless the user explicitly bypasses the workflow. [VERIFIED: AGENTS.md]
- Prefer localized edits and avoid broad unrelated rewrites. [VERIFIED: AGENTS.md; standards/core/code-shape.md]
- Sync before substantive repo-changing work when the worktree is clean and a remote exists; this research session fetched remote state and found `master` ahead of `origin/master` by 3 commits with no behind commits. [VERIFIED: standards/core/verification.md; git status -sb; git log HEAD..origin/master]
- Run relevant repo-native verification before commit and do not commit failing checks. [VERIFIED: standards/core/verification.md; AGENTS.md]
- Because this repository has `Cargo.toml`, any commit must be preceded by `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`. [VERIFIED: AGENTS.md; Cargo.toml present]
- Use `justfile` wrappers for developer workflows where they exist. [VERIFIED: AGENTS.md; justfile]
- Keep generated and managed files owned by their generators; do not edit managed Bright Builds blocks or generated outputs directly. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md]
- Public evidence docs must not expose private signing keys, tokens, certificates, raw service payloads, or raw crash dumps. [VERIFIED: .planning/REQUIREMENTS.md; .planning/PROJECT.md]
- For tests, use behavior-focused checks and Arrange/Act/Assert when adding or changing unit tests. [VERIFIED: standards/core/testing.md; AGENTS.md]
- No active local standards overrides are recorded. [VERIFIED: standards-overrides.md]

## Standard Stack

### Core

| Tool / Artifact | Version / State | Purpose | Why Standard |
|---|---:|---|---|
| GSD planning artifacts under `.planning/` | v1.2 active milestone [VERIFIED: .planning/ROADMAP.md; node gsd-tools init milestone-op] | Source of milestone state, requirements, phase evidence, validation, and audit records. | Existing GSD lifecycle and audit workflows consume these files. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md] |
| `gsd-tools.cjs` | installed and executable [VERIFIED: test -x /Users/peterryszkiewicz/.codex/get-shit-done/bin/gsd-tools.cjs] | Roadmap analysis, phase init, milestone init, summary extraction, and commits. | Existing GSD workflows use it for milestone and phase parsing. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md; /Users/peterryszkiewicz/.codex/get-shit-done/workflows/complete-milestone.md] |
| YAML frontmatter in `*-SUMMARY.md` and `*-VERIFICATION.md` | current v1.2 summaries mix `requirements_completed` and `requirements-completed` [VERIFIED: rg output; summary-extract output] | Machine-readable requirement completion and phase verification metadata. | Milestone audit cross-checks requirements, verification reports, and summary frontmatter. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md] |
| `25-VERIFICATION.md` expanded verification report shape | current compact report [VERIFIED: .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md] | Audit-friendly proof for EVID-03 without changing pass status. | Phases 23, 24, 26, 27, and 28 already use expanded requirement coverage and command evidence sections. [VERIFIED: phase verification reports read in this session] |

### Supporting

| Tool | Available | Version | Purpose |
|---|---:|---:|---|
| Node.js | yes [VERIFIED: command -v node] | v24.13.0 [VERIFIED: node --version] | Runs `gsd-tools.cjs` and GSD helper commands. [VERIFIED: gsd-tools command output] |
| Python 3 | yes [VERIFIED: command -v python3] | 3.14.4 [VERIFIED: python3 --version] | Runs existing Phase 25 verifier tests when rechecking the unchanged evidence path. [VERIFIED: justfile; tools/bazel/rust_workflow.sh] |
| `just` | yes [VERIFIED: command -v just] | 1.48.0 [VERIFIED: just --version] | Runs `just phase25-verify` and other repo workflow wrappers. [VERIFIED: justfile] |
| Bazel | yes [VERIFIED: command -v bazel] | 9.1.1 [VERIFIED: bazel --version] | Required by `just phase25-verify`. [VERIFIED: justfile] |
| Cargo | yes [VERIFIED: command -v cargo] | 1.91.1 [VERIFIED: cargo --version] | Required by repo commit gate in Rust projects. [VERIFIED: AGENTS.md] |
| ripgrep | yes [VERIFIED: command -v rg] | 15.1.0 [VERIFIED: rg --version] | Fast metadata and stale-prose checks. [VERIFIED: command output] |
| Git | yes [VERIFIED: command -v git] | 2.53.0 [VERIFIED: git --version] | Diff hygiene, status, and commit handling. [VERIFIED: command output] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Dual-key current summary frontmatter bridge | Update `$HOME/.codex/get-shit-done` helper code | Out of scope for a repo commit and deferred by user context. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md] |
| Dual-key current summary frontmatter bridge | Only document direct parsing as authoritative | Allowed by D-04, but it leaves the documented `summary-extract` command returning empty arrays for underscore-only summaries. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md; summary-extract command output] |
| Expand Phase 25 verification | Durable local exception in the audit | Allowed by roadmap success criterion, but context D-06 selects expansion as the preferred cleanup. [VERIFIED: .planning/ROADMAP.md; .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md] |

**Installation:**

```bash
# No new packages should be installed for Phase 30.
```

**Version verification:** No npm, Cargo, or Python dependencies should be added for this phase. [VERIFIED: phase scope in .planning/ROADMAP.md; .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

## Architecture Patterns

### Recommended Project Structure

```text
.planning/
├── STATE.md                                      # refresh stale milestone status and session continuity
├── v1.2-MILESTONE-AUDIT.md                      # final audit closure record
├── ROADMAP.md                                   # phase status may be updated by GSD lifecycle after execution
└── phases/
    ├── 23-.../23-01-SUMMARY.md                  # add current-summary compatibility alias if missing
    ├── 24-.../24-01-SUMMARY.md                  # add current-summary compatibility alias if missing
    ├── 25-live-service-evidence-execution/
    │   ├── 25-01-SUMMARY.md                     # add current-summary compatibility alias if missing
    │   └── 25-VERIFICATION.md                   # expand report shape; keep status passed
    ├── 26-.../26-01-SUMMARY.md                  # add current-summary compatibility alias if missing
    ├── 27-.../27-01-SUMMARY.md                  # add underscore alias for direct-parser symmetry
    ├── 28-.../28-01-SUMMARY.md                  # add current-summary compatibility alias if missing
    ├── 29-.../29-02-SUMMARY.md                  # add current-summary compatibility alias if missing
    └── 30-milestone-metadata-cleanup/
        ├── 30-VALIDATION.md                     # created by planning/validation flow
        ├── 30-01-PLAN.md                        # created by planner
        ├── 30-01-SUMMARY.md                     # created by executor
        └── 30-VERIFICATION.md                   # created by verifier
```

The listed planning artifacts are the exact likely modification set for Phase 30; no firmware source files are needed to satisfy the phase goal. [VERIFIED: .planning/ROADMAP.md; .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md; current v1.2 artifact reads]

### Pattern 1: Localized Metadata-Only Cleanup

**What:** Touch only stale planning metadata, current v1.2 summary frontmatter, Phase 25 verification prose, and the milestone audit record. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

**When to use:** Use this for TD-1 through TD-4 because the audit explicitly classifies them as non-critical metadata debt, not code or evidence behavior gaps. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md]

**Example:**

```markdown
---
requirements:
  - EVID-03
requirements_completed:
  - EVID-03
requirements-completed:
  - EVID-03
---
```

The example preserves the existing underscore key while adding the hyphenated key consumed by `summary-extract`. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs; summary-extract command output]

### Pattern 2: Current-Summary Compatibility Bridge

**What:** Add missing counterpart requirement-completion keys to current v1.2 requirement-bearing summary files. [VERIFIED: current summary frontmatter reads; summary-extract command output]

**When to use:** Use it because current `summary-extract` constructs `requirements_completed` from `fm['requirements-completed'] || []`, while most v1.2 summaries currently use only `requirements_completed`. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs; rg output]

**Required files:**

| File | Current issue | Planned normalization |
|---|---|---|
| `.planning/phases/23-simulator-evidence-execution/23-01-SUMMARY.md` | Has `requirements_completed`; helper returns empty. [VERIFIED: file read; summary-extract output] | Add `requirements-completed: [EVID-01]` block or list. [VERIFIED: helper behavior] |
| `.planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-SUMMARY.md` | Has `requirements_completed`; helper returns empty. [VERIFIED: file read; summary-extract output] | Add `requirements-completed: [EVID-02]`. [VERIFIED: helper behavior] |
| `.planning/phases/25-live-service-evidence-execution/25-01-SUMMARY.md` | Has `requirements_completed`; helper returns empty. [VERIFIED: file read; summary-extract output] | Add `requirements-completed: [EVID-03]`. [VERIFIED: helper behavior] |
| `.planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md` | Has `requirements_completed`; helper returns empty. [VERIFIED: file read; summary-extract output] | Add `requirements-completed: [EVID-04, ACPT-01]`. [VERIFIED: helper behavior] |
| `.planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-01-SUMMARY.md` | Has `requirements-completed`; helper works; underscore direct-parser symmetry is missing. [VERIFIED: file read; summary-extract output] | Add `requirements_completed: [ACPT-02, ACPT-03]`. [VERIFIED: current audit checks both key spellings] |
| `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-01-SUMMARY.md` | Has `requirements_completed`; helper returns empty. [VERIFIED: file read; summary-extract output] | Add `requirements-completed: [READ-01, READ-02, READ-03]`. [VERIFIED: helper behavior] |
| `.planning/phases/29-upstream-evidence-flow-closure/29-02-SUMMARY.md` | Has `requirements_completed`; helper returns empty. [VERIFIED: file read; summary-extract output] | Add `requirements-completed: [ACPT-01, READ-01, READ-02]`. [VERIFIED: helper behavior] |

Do not add completion metadata to `29-01-SUMMARY.md` because it records partial implementation work and the completion metadata is in `29-02-SUMMARY.md`. [VERIFIED: .planning/phases/29-upstream-evidence-flow-closure/29-01-SUMMARY.md; .planning/phases/29-upstream-evidence-flow-closure/29-02-SUMMARY.md]

### Pattern 3: Audit-Friendly Phase 25 Verification

**What:** Expand `25-VERIFICATION.md` to match the sections used by Phase 23, 24, 26, 27, and 28 reports: goal, status, observable truths, required artifacts, behavioral spot-checks, requirements coverage, human verification boundary, and gaps summary. [VERIFIED: phase verification reports read in this session]

**When to use:** Use it because TD-4 says Phase 25 verification is compact even though status, summary metadata, and tests already satisfy EVID-03. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md; .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md]

**Example skeleton:**

```markdown
## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| EVID-03 | 25-01 | Maintainer can supply real live-service evidence for Connect, WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows. | SATISFIED | Phase 25 verifier requires Phase 16 scenario coverage, rejects secret-bearing inputs, retains blocked quick placeholders, and exposes `just phase25-verify`. |
```

The skeleton uses the same requirement-table columns described by the milestone audit workflow. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md]

### Pattern 4: Audit Closure After Local Checks

**What:** Run the milestone audit workflow only after state, summary extraction, and Phase 25 verification shape are locally clean. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md; /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md]

**When to use:** Use it as the final proof for Phase 30 success criterion 4. [VERIFIED: .planning/ROADMAP.md]

**Expected audit outcome:** `status: passed`, no critical gaps, no TD-1 through TD-4 blockers, and external evidence boundaries still documented as intentional non-local inputs. [VERIFIED: .planning/ROADMAP.md; .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md; .planning/v1.2-MILESTONE-AUDIT.md]

### Anti-Patterns to Avoid

- **Editing GSD helper code outside the repo:** This violates the deferred scope unless the user explicitly asks for a GSD tool fix. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]
- **Broad historical summary rewrites:** This violates D-05 and risks masking the current v1.2 extraction issue. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]
- **Changing Phase 25 pass semantics:** This violates D-07; the report expansion must preserve `status: passed` and the blocked-placeholder boundary. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md; .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md]
- **Marking real external evidence as supplied:** This contradicts milestone constraints and external evidence boundaries. [VERIFIED: .planning/REQUIREMENTS.md; .planning/PROJECT.md; .planning/v1.2-MILESTONE-AUDIT.md]
- **Treating `/gsd-complete-milestone` as part of Phase 30:** Milestone archival is deferred until after Phase 30 verification passes. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Milestone audit | A new local audit script | `/gsd-audit-milestone` workflow and `.planning/v1.2-MILESTONE-AUDIT.md` | The existing audit workflow cross-checks phase verification, summary metadata, requirements, integration, and Nyquist metadata. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md] |
| Summary extraction | A one-off parser as the only proof | `summary-extract` plus direct frontmatter review in the audit | The audit workflow already documents `summary-extract`, and the current audit already uses direct parsing as a cross-check. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md; .planning/v1.2-MILESTONE-AUDIT.md] |
| Phase 25 evidence proof | A new live-service evidence run | Existing `python3 tools/bazel/phase25_live_service_evidence_execution_test.py -q` and `just phase25-verify` | Phase 30 changes report shape only; Phase 25 code already has local verification commands. [VERIFIED: .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md; justfile] |
| Completion metadata | Requirement coverage recalculation by hand | Existing REQUIREMENTS traceability, summaries, verification reports, and audit workflow | The milestone already has 10/10 requirements complete; Phase 30 is requirement-neutral. [VERIFIED: .planning/REQUIREMENTS.md; .planning/ROADMAP.md] |

**Key insight:** The only parser bug observed in this phase is a key-name compatibility mismatch; the safest repo-local response is metadata compatibility and audit wording, not new parsing infrastructure. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs; summary-extract command output; .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Stale STATE.md Claims Phase 29 Is Current

**What goes wrong:** `.planning/STATE.md` frontmatter says Phase 30 context is gathered, but the body still says current focus is Phase 29 and plan not started. [VERIFIED: .planning/STATE.md]

**Why it happens:** Shared state updates were intentionally skipped by several executors and are orchestrator-owned. [VERIFIED: .planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md; .planning/phases/28-final-readiness-packet-and-demotion-gate/28-01-SUMMARY.md]

**How to avoid:** Refresh frontmatter, current position, progress metrics, recent trend, blockers, and session continuity together. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

**Warning signs:** `Current focus: Phase 29`, `Phase: 29`, `Plan: Not started`, or `Status: Ready to execute` remain in `STATE.md` after cleanup. [VERIFIED: .planning/STATE.md]

### Pitfall 2: Fixing the Wrong Side of Summary Extraction

**What goes wrong:** Updating `$HOME/.codex/get-shit-done` would fix the helper locally but would create an out-of-repo change not captured by this repository. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

**Why it happens:** The helper implementation currently maps `requirements_completed` output from `fm['requirements-completed']`, while Phase 23/24/25/26/28/29-02 use `requirements_completed`. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs; current summary frontmatter reads]

**How to avoid:** Add current-summary frontmatter aliases and record the bridge in the audit. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

**Warning signs:** The documented summary-extract loop still prints blank output for Phase 23, 24, 25, 26, 28, or 29-02 summaries. [VERIFIED: summary-extract command output]

### Pitfall 3: Phase 25 Report Expansion Overclaims Live Services

**What goes wrong:** Expanded prose could accidentally imply Connect, WUI, TLS, telemetry, proxy, transfer, long-transfer, or crash-dump service proof has passed in a real environment. [VERIFIED: .planning/phases/25-live-service-evidence-execution/25-VALIDATION.md; .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md]

**Why it happens:** The existing verification passed local validation and blocked-placeholder behavior, not real service operation. [VERIFIED: .planning/phases/25-live-service-evidence-execution/25-VALIDATION.md]

**How to avoid:** Copy the Phase 23/24 wording pattern: local implementation verified, real evidence remains an external maintainer input. [VERIFIED: .planning/phases/23-simulator-evidence-execution/23-VERIFICATION.md; .planning/phases/24-hardware-media-and-safety-evidence-execution/24-VERIFICATION.md]

**Warning signs:** Words such as "real live-service evidence passed" appear without an explicit maintainer-supplied evidence-input condition. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

### Pitfall 4: Audit Stays `tech_debt`

**What goes wrong:** The milestone remains non-archivable if `.planning/v1.2-MILESTONE-AUDIT.md` still reports `status: tech_debt` and lists TD-1 through TD-4 as open. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md]

**Why it happens:** Phase 29 fixed critical evidence flow but intentionally left metadata debt for Phase 30. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md; .planning/phases/29-upstream-evidence-flow-closure/29-02-SUMMARY.md]

**How to avoid:** Update or regenerate the audit after cleanup and ensure the verdict distinguishes closed metadata debt from intentional external evidence boundaries. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

**Warning signs:** Audit frontmatter still includes `status: tech_debt` or a `tech_debt` list naming TD-1 through TD-4 as unresolved. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md]

## Code Examples

### Verify Current Summary Extraction

```bash
for summary in .planning/phases/{23,24,25,26,27,28,29-*}*/*-SUMMARY.md; do
  [ -e "$summary" ] || continue
  printf '%s: ' "$summary"
  node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" summary-extract "$summary" --fields requirements_completed --pick requirements_completed
  printf '\n'
done
```

This command currently returns only `ACPT-02,ACPT-03` for Phase 27 and blanks for the underscore-only current v1.2 summaries. [VERIFIED: command run in this session]

### Inspect Helper Compatibility

```javascript
requirements_completed: fm['requirements-completed'] || [],
```

The installed helper currently reads the hyphenated frontmatter key for the `requirements_completed` output field. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs]

### Phase 25 Verification Requirement Table

```markdown
## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| EVID-03 | 25-01 | Maintainer can supply real live-service evidence for Connect, WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows. | SATISFIED | Phase 25 validates Phase 16 scenario coverage, rejects unsafe inputs, writes retained blocked quick outputs, and exposes `just phase25-verify`. |
```

This table shape matches the audit workflow requirement cross-check and the surrounding v1.2 verification reports. [VERIFIED: /Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md; phase verification reports read in this session]

### Practical Verification Command Set

```bash
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init milestone-op
python3 tools/bazel/phase25_live_service_evidence_execution_test.py -q
just phase25-verify
git diff --check
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

These commands cover roadmap state, milestone state, Phase 25 evidence tooling, diff hygiene, and the repo-mandated Rust commit gate. [VERIFIED: command availability checks; justfile; AGENTS.md]

## State of the Art

| Old Approach | Current Approach | When Changed / Observed | Impact |
|---|---|---|---|
| Rely only on `summary-extract` reading `requirements-completed`. [VERIFIED: audit workflow; helper source] | Current v1.2 summaries should be compatibility-readable by both `requirements_completed` and `requirements-completed`. [VERIFIED: current drift; Phase 30 context] | Observed 2026-06-26 during Phase 30 research. [VERIFIED: command output] | Audit can use helper output without losing underscore-only completions. [VERIFIED: helper source] |
| Phase 25 compact verification prose. [VERIFIED: 25-VERIFICATION.md] | Expanded audit-friendly sections with requirement coverage and command evidence. [VERIFIED: Phase 23/24/26/27/28 verification reports] | TD-4 recorded in current audit. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md] | Milestone audit can read Phase 25 like the other v1.2 evidence reports. [VERIFIED: audit workflow] |
| Stale state prose after execution phases. [VERIFIED: .planning/STATE.md] | State synchronized with roadmap analysis and completed Phase 23-29 artifacts. [VERIFIED: roadmap analyze output; Phase 30 context] | TD-2 recorded in current audit. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md] | Archival will not preserve contradictory "Phase 29 current" text. [VERIFIED: .planning/ROADMAP.md; .planning/STATE.md] |

**Deprecated/outdated:**

- Treating the current audit as final is outdated because it explicitly reports `status: tech_debt` and lists TD-1 through TD-4. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md]
- Treating `summary-extract` as the sole requirement-completion source is outdated unless current summary frontmatter is made helper-compatible. [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md; helper source]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| — | None. All recommendations are based on local files or command output gathered in this session. | — | — |

## Open Questions (RESOLVED)

1. **Should Phase 30 mark the audit `passed` or `tech_debt` with durable exceptions if a cleanup item is intentionally left open?** [VERIFIED: .planning/ROADMAP.md]
   - What we know: The roadmap success criterion allows a durable local exception for Phase 25 verification shape, but the context prefers closing TD-1 through TD-4. [VERIFIED: .planning/ROADMAP.md; .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]
   - Resolution: Phase 30 will use the dual-key summary frontmatter bridge and expanded Phase 25 report so the fresh milestone audit can use the passed audit path. [VERIFIED: helper source; current verification report patterns]
   - Durable exception posture: Do not plan a durable local exception. Only document one during execution if the dual-key bridge or audit-friendly Phase 25 report cannot be completed without changing out-of-scope global GSD helper code or overclaiming external evidence. [VERIFIED: .planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---:|---:|---|
| Node.js | `gsd-tools.cjs`, roadmap/milestone/summary extraction | yes [VERIFIED: command -v node] | v24.13.0 [VERIFIED: node --version] | none needed |
| GSD helper | phase init, roadmap analysis, summary extraction, commit | yes [VERIFIED: test -x gsd-tools.cjs] | local install [VERIFIED: gsd-tools usage output] | manual file reads only for research; not for phase execution |
| Python 3 | Phase 25 tests | yes [VERIFIED: command -v python3] | 3.14.4 [VERIFIED: python3 --version] | none needed |
| `just` | `just phase25-verify` | yes [VERIFIED: command -v just] | 1.48.0 [VERIFIED: just --version] | direct Bazel commands from justfile |
| Bazel | `just phase25-verify` | yes [VERIFIED: command -v bazel] | 9.1.1 [VERIFIED: bazel --version] | direct Python tests can prove report-shape edits if Bazel is unavailable |
| Cargo | Rust project commit gate | yes [VERIFIED: command -v cargo] | 1.91.1 [VERIFIED: cargo --version] | none under AGENTS.md commit rules |
| Git | sync, diff, commit | yes [VERIFIED: command -v git] | 2.53.0 [VERIFIED: git --version] | none needed |
| ripgrep | stale metadata search | yes [VERIFIED: command -v rg] | 15.1.0 [VERIFIED: rg --version] | `grep` if unavailable |

**Missing dependencies with no fallback:** None found. [VERIFIED: environment probes]

**Missing dependencies with fallback:** None found. [VERIFIED: environment probes]

## Validation Architecture

Nyquist validation is enabled for this project. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|---|---|
| Framework | GSD metadata checks, Python `unittest` for Phase 25, Bazel/just workflow wrappers, Cargo workspace checks [VERIFIED: .planning/config.json; justfile; Phase 25 verification] |
| Config file | `.planning/config.json`; no dedicated Phase 30 test config exists yet [VERIFIED: .planning/config.json; phase directory listing] |
| Quick run command | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze && python3 tools/bazel/phase25_live_service_evidence_execution_test.py -q && git diff --check` [VERIFIED: command availability; justfile] |
| Full suite command | `just phase25-verify && git diff --check && cargo fmt --all && cargo clippy --all-targets --all-features -- -D warnings && cargo build --all-targets --all-features && cargo test --all-features` [VERIFIED: justfile; AGENTS.md] |

### Phase Success Criteria -> Test Map

| ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| SC-30-01 | `.planning/STATE.md` reports v1.2 progress and position consistently with roadmap and Phase 23-29 artifacts. [VERIFIED: .planning/ROADMAP.md] | metadata check | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze` plus `rg -n "Current focus: Phase 29|Phase: 29|Plan: Not started|Ready to execute" .planning/STATE.md` expected no stale matches after cleanup. [VERIFIED: roadmap analyze; current STATE.md] | yes [VERIFIED: .planning/STATE.md] |
| SC-30-02 | Summary completion metadata is helper-compatible or audit documents direct parsing as authoritative. [VERIFIED: .planning/ROADMAP.md] | metadata check | summary-extract loop from Code Examples, expected to print EVID/ACPT/READ IDs for current v1.2 requirement-bearing summaries after cleanup. [VERIFIED: helper source; command output] | yes [VERIFIED: summary files read] |
| SC-30-03 | Phase 25 verification has audit-friendly EVID-03 requirement coverage without changing pass semantics. [VERIFIED: .planning/ROADMAP.md] | docs plus regression | `python3 tools/bazel/phase25_live_service_evidence_execution_test.py -q && just phase25-verify` [VERIFIED: justfile; current 25-VERIFICATION.md] | yes [VERIFIED: .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md] |
| SC-30-04 | Fresh audit reports no critical gaps and no contradictory stale metadata before archival. [VERIFIED: .planning/ROADMAP.md] | workflow audit | `/gsd-audit-milestone` after local checks; inspect `.planning/v1.2-MILESTONE-AUDIT.md`. [VERIFIED: gsd-audit-milestone workflow; current audit path] | yes [VERIFIED: .planning/v1.2-MILESTONE-AUDIT.md] |

### Sampling Rate

- **Per task commit:** Run metadata extraction loop and `git diff --check`. [VERIFIED: Phase 30 metadata-only scope]
- **Per wave merge:** Run `python3 tools/bazel/phase25_live_service_evidence_execution_test.py -q` and `just phase25-verify` if Phase 25 verification report wording changed. [VERIFIED: justfile; Phase 25 verification scope]
- **Phase gate:** Run `/gsd-audit-milestone`, `git diff --check`, and the AGENTS.md Cargo sequence before commit. [VERIFIED: .planning/ROADMAP.md; AGENTS.md]

### Wave 0 Gaps

- [ ] `.planning/phases/30-milestone-metadata-cleanup/30-VALIDATION.md` — should map SC-30-01 through SC-30-04 because Nyquist is enabled and Phase 30 has no validation file yet. [VERIFIED: .planning/config.json; phase directory listing]
- [ ] `.planning/phases/30-milestone-metadata-cleanup/30-01-PLAN.md` — should include metadata-only tasks and no firmware source edits. [VERIFIED: phase directory listing; Phase 30 context]

## Security Domain

Security enforcement is enabled by default because `.planning/config.json` does not set `security_enforcement: false`. [VERIFIED: .planning/config.json; researcher instructions]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---:|---|
| V2 Authentication | no [VERIFIED: metadata-only scope] | Do not add auth surfaces. [VERIFIED: .planning/ROADMAP.md] |
| V3 Session Management | no [VERIFIED: metadata-only scope] | Do not add session state. [VERIFIED: .planning/ROADMAP.md] |
| V4 Access Control | no [VERIFIED: metadata-only scope] | Do not add access-control decisions. [VERIFIED: .planning/ROADMAP.md] |
| V5 Input Validation | yes [VERIFIED: summary frontmatter is parsed by GSD helper and audit workflow] | Keep frontmatter machine-readable, preserve exact requirement IDs, and verify parser output. [VERIFIED: helper source; audit workflow] |
| V6 Cryptography | no [VERIFIED: metadata-only scope] | Do not handle keys or signing material. [VERIFIED: .planning/REQUIREMENTS.md] |

### Known Threat Patterns for Metadata Cleanup

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Evidence overclaim in docs | Spoofing / Repudiation [VERIFIED: external evidence boundary docs] | Keep quick/local fixture evidence distinct from real maintainer/operator evidence. [VERIFIED: .planning/PROJECT.md; 25-VALIDATION.md] |
| Secret leakage in audit docs | Information Disclosure [VERIFIED: requirements out-of-scope table] | Do not paste private keys, tokens, certificates, raw service payloads, or raw crash dumps. [VERIFIED: .planning/REQUIREMENTS.md] |
| Parser drift creates false missing requirements | Tampering / Integrity [VERIFIED: helper source; audit debt TD-3] | Verify helper output and direct frontmatter key spellings before audit closure. [VERIFIED: summary-extract output; .planning/v1.2-MILESTONE-AUDIT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/30-milestone-metadata-cleanup/30-CONTEXT.md` — locked decisions, discretion, deferred scope, and canonical refs. [VERIFIED: file read]
- `.planning/ROADMAP.md` — Phase 30 goal, success criteria, gap closure, and current progress table. [VERIFIED: file read]
- `.planning/REQUIREMENTS.md` — requirement-neutral Phase 30 state and 10/10 v1.2 completion. [VERIFIED: file read]
- `.planning/STATE.md` — stale state details to reconcile. [VERIFIED: file read]
- `.planning/v1.2-MILESTONE-AUDIT.md` — TD-1 through TD-4 and current `tech_debt` verdict. [VERIFIED: file read]
- Phase 23-29 summaries and verification reports — current metadata patterns and expanded verification report shapes. [VERIFIED: file reads]
- `/Users/peterryszkiewicz/.codex/get-shit-done/bin/lib/commands.cjs` — `summary-extract` frontmatter key behavior. [VERIFIED: file read]
- `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md` — audit cross-check workflow. [VERIFIED: file read]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards/core/verification.md`, `standards/core/testing.md`, `standards/core/code-shape.md`, `standards/core/architecture.md` — repo and standards constraints. [VERIFIED: file reads]

### Secondary (MEDIUM confidence)

- Local command outputs for `roadmap analyze`, `init milestone-op`, `summary-extract`, tool versions, and git status. [VERIFIED: command output]

### Tertiary (LOW confidence)

- None. [VERIFIED: no web-only or training-only claims used]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — tools and versions were checked locally. [VERIFIED: environment probes]
- Architecture: HIGH — modification targets come from Phase 30 context, roadmap, audit debt, and current artifact patterns. [VERIFIED: file reads]
- Pitfalls: HIGH — each pitfall maps to a current stale artifact or verified helper behavior. [VERIFIED: file reads; command output]

**Research date:** 2026-06-26 [VERIFIED: environment current date]
**Valid until:** 2026-07-03 for helper behavior and local metadata shape because GSD helper code can change independently of this repository. [VERIFIED: helper outside repo; Phase 30 context]
