# Phase 27: Retained-Code and Maintainer Acceptance Decisions - Research

**Researched:** 2026-06-25
**Domain:** Contract-backed maintainer decision inputs for retained-code, residual-risk, exception, and readiness gates
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### Acceptance Source Coverage
- **D-01:** Build Phase 27 as a phase-owned wrapper around `tools/bazel/manifests/phase18_cutover_review_contract.json` and Phase 26 upstream-row outputs, not as a new standalone acceptance schema.
- **D-02:** Treat Phase 18 as canonical for retained packet schema, final decision schema, exception fields, status vocabularies, upstream criteria, and demotion blocking rules. Phase 27 may project those into v1.2 outputs but must not fork or silently redefine them.
- **D-03:** The Phase 27 verifier should assert exact coverage for the Phase 18 retained packet and upstream criterion surfaces, including retained-code acceptance, residual-risk review, maintainer-decision, and reference-demotion rows.

### Decision and Status Semantics
- **D-04:** Model evidence state, maintainer decision, exception state, residual-risk state, hard-failure state, and demotion authorization as separate axes, then derive Phase 18-compatible output status from those axes.
- **D-05:** Redaction failures, overclaim failures, unsafe refs, source-ref failures, and stale lifecycle evidence must hard-block acceptance. They must not be transformed into accepted retained-code risk by maintainer exception.
- **D-06:** Retained-code acceptance can become accepted, rejected, blocked, or deferred-approved-exception only from explicit maintainer decision input with rationale and evidence refs. Green evidence alone is not acceptance.
- **D-07:** Reference demotion authorization stays blocked or not approved in Phase 27. Phase 27 may emit a handoff row explaining what Phase 28 still needs, but it must not set demotion as allowed.

### Exception and Residual-Risk Policy
- **D-08:** Use a typed exception gate based on Phase 18's exception fields: scope, rationale, approver, approver_role, affected_printer_or_release_surface, mitigation_or_follow_up, expiry_or_review_trigger, and evidence_refs.
- **D-09:** Require every exception approval to name owner or approver, affected scope, rationale, evidence refs, residual risk, mitigation or follow-up, and an expiration or revisit trigger.
- **D-10:** Distinguish unresolved evidence blockers from accepted residual risks. A blocked evidence row remains a blocker unless the Phase 18 criterion explicitly allows an exception and the exception metadata is complete.
- **D-11:** For safety-, release-, signing-, TLS-, credential-, crash-dump-, and hardware-adjacent surfaces, planning should prefer stricter reviewer-role checks rather than broad "maintainer accepted" wording.

### Retained Outputs and Integration
- **D-12:** Write retained Phase 27 outputs under `build/ci-evidence/phase27`, following the Phase 23-26 execution-wrapper convention.
- **D-13:** Expected retained outputs should include an acceptance run manifest, normalized retained-code decisions, residual-risk register, exception decision register or summary, final-readiness decision summary, Phase 28 handoff manifest, decision row table, safe maintainer input template, artifact reference summary, and source contract snapshots.
- **D-14:** Phase 27 should consume Phase 26 upstream rows without replaying or copying unrelated evidence statuses. It should emit Phase 27-owned decision deltas and a clear precedence/handoff model for Phase 28.
- **D-15:** Add focused tests for Phase 18 schema/vocabulary exact-match checks, Phase 26 upstream-row consumption, retained packet coverage, exception metadata completeness, redaction/overclaim hard blockers, no-demotion guarantees, retained output writing, and Bazel/just wiring.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 27 contract, input template, decision manifests, summaries, and handoff manifest, provided they are explicit, tested, and stable for Phase 28.
- Decide whether to share helper functions with Phase 18/26 or keep a thin standalone Phase 27 verifier. Prefer the smallest approach that avoids schema drift and keeps the acceptance projection readable.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless research finds a real dependency split.

### Deferred Ideas (OUT OF SCOPE)
- Signed attestation-style maintainer approvals may be useful later, but they are broader than Phase 27 unless a future phase explicitly adds signed cross-party approval infrastructure.
- External issue-tracker risk registers may be useful if exceptions become numerous or need lifecycle tracking beyond checked-in evidence artifacts.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ACPT-02 | Maintainer can accept, reject, or exception retained-code packets with residual-risk rationale. [VERIFIED: .planning/REQUIREMENTS.md] | Phase 18 already defines 10 retained-code acceptance packets, retained review fields, allowed retained statuses, approver roles, evidence refs, residual-risk fields, and acceptance consistency checks. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; tools/bazel/phase18_cutover_review.py] |
| ACPT-03 | Maintainer can approve or block final readiness using machine-readable decision inputs. [VERIFIED: .planning/REQUIREMENTS.md] | Phase 18 already defines 9 final criteria, final decision fields, exception fields, upstream result requirements, and demotion blocking behavior; Phase 26 emits the canonical 9-row upstream table Phase 27 must consume. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json; build/ci-evidence/phase26/upstream-result-row-table.json] |
</phase_requirements>

## Summary

Phase 27 should be implemented as a small Python standard-library verifier plus manifest, tests, Bazel wiring, and `just phase27-verify`, matching the Phase 23-26 execution-wrapper pattern. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/phase26_release_signing_upstream_evidence.py; tools/bazel/BUILD.bazel; justfile] The core design should parse Phase 18 retained packets/final criteria and Phase 26 upstream rows into explicit decision axes, then emit Phase 27-owned decision deltas under `build/ci-evidence/phase27`. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/manifests/phase18_cutover_review_contract.json; build/ci-evidence/phase26/upstream-result-row-table.json]

Phase 18 is the canonical schema and policy source: it defines retained packet fields, final decision fields, exception metadata, vocabularies, hard blockers, source-ref validation, retained review validation, upstream result consumption, residual-risk register generation, and demotion gating. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; tools/bazel/phase18_cutover_review.py] Phase 26 is the canonical upstream-row producer for v1.2: it emits nine Phase 18 criterion rows and leaves retained-code, residual-risk, maintainer-decision, and reference-demotion rows blocked, pending, or not-required for later phases. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; build/ci-evidence/phase26/upstream-result-row-table.json]

**Primary recommendation:** Build one cohesive plan that creates `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`, `tools/bazel/phase27_retained_code_acceptance_decisions.py`, `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`, retained outputs in `build/ci-evidence/phase27`, Bazel labels, `rust_workflow.sh` cases, and `just phase27-verify`. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/BUILD.bazel; tools/bazel/rust_workflow.sh; justfile]

## Project Constraints (from AGENTS.md)

- Read `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before planning or implementation. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md]
- Use Bright Builds Rules unless a narrow local override exists; `standards-overrides.md` has no active real override beyond the placeholder row. [VERIFIED: AGENTS.md; standards-overrides.md]
- Keep GSD artifacts in sync and avoid direct repo edits outside GSD workflow unless explicitly bypassed. [VERIFIED: AGENTS.md]
- Prefer functional core / imperative shell: pure decision logic should be data-in/data-out, with file I/O and CLI code in thin adapters. [VERIFIED: standards/core/architecture.md]
- Parse boundary data into richer domain values early, and make illegal states unrepresentable where practical. [VERIFIED: standards/core/architecture.md]
- Prefer early returns and shallow control flow. [VERIFIED: standards/core/code-shape.md]
- Prefix internal optional or absence-bearing values with `maybe`/`maybe_` when practical. [VERIFIED: standards/core/code-shape.md; standards/languages/rust.md]
- Unit-test pure/business logic with focused tests and explicit Arrange/Act/Assert comments where non-trivial. [VERIFIED: standards/core/testing.md]
- Prefer repo-owned verification entrypoints and run relevant verification before commit. [VERIFIED: standards/core/verification.md]
- Before any git commit in this Rust project, run `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`. [VERIFIED: AGENTS.md]
- Keep generated evidence under ignored build output directories; repo-tracked files should be contracts, templates, verifier code, tests, wiring, and planning artifacts. [VERIFIED: AGENTS.md; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]
- No repo-local `.claude/skills` or `.agents/skills` `SKILL.md` files were found for this phase. [VERIFIED: local `find .claude/skills .agents/skills -maxdepth 2 -name SKILL.md`]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library (`argparse`, `json`, `pathlib`, `shutil`, `unittest`) | Python 3.14.4 locally | Contract parsing, decision normalization, output writing, and unit tests | Existing Phase 18 and Phase 26 verifiers use standard-library Python with `unittest`, avoiding new dependencies. [VERIFIED: python3 --version; tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Bazel `shell_binary` via repo `tools/bazel/shell_rules.bzl` | Bazel 9.1.1 locally | Expose verifier and test commands as repo-native labels | Existing phase verifiers are wired as `shell_binary` targets in `tools/bazel/BUILD.bazel`. [VERIFIED: bazel --version; tools/bazel/BUILD.bazel] |
| `just` facade | just 1.48.0 locally | Developer-facing `phase27-verify` command | Existing phase workflows expose `phaseXX-verify` recipes that run tests before verifiers. [VERIFIED: just --version; justfile] |
| Rust/Cargo workspace checks | cargo 1.91.1 locally | Required pre-commit verification for this Rust project | Repo instructions require Cargo format, lint, build, and test before commits. [VERIFIED: cargo --version; AGENTS.md] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `jq` | jq 1.7.1 locally | Manual JSON inspection during planning/debugging | Useful for validating row sets, but not required in committed verifier code. [VERIFIED: jq --version; local research commands] |
| Existing Phase 18 verifier functions/patterns | Source-backed | Exception metadata, retained review, upstream blocking, source-ref, secret, and demotion logic patterns | Reuse directly or mirror narrowly when avoiding import coupling keeps Phase 27 readable. [VERIFIED: tools/bazel/phase18_cutover_review.py] |
| Existing Phase 26 verifier patterns | Source-backed | Phase 26 upstream-row generation, output-root containment, generated artifact snapshots, and wiring checks | Use as the v1.2 execution-wrapper template. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; tools/bazel/phase26_release_signing_upstream_evidence_test.py] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Standard-library Python verifier | JSON Schema package or Pydantic | Adds dependency surface where existing phase tools already validate with explicit Python functions. [VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Phase-owned wrapper around Phase 18/26 | New standalone acceptance schema | Rejected by locked decisions D-01 and D-02. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md] |
| Generate Phase 27 status from upstream rows alone | Require explicit maintainer decision input | Green evidence alone is not acceptance under D-06. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md] |

**Installation:** No new package installation is recommended. [VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py]

**Version verification:** No npm packages apply. Tool versions verified locally: Python 3.14.4, Bazel 9.1.1, just 1.48.0, cargo 1.91.1, jq 1.7.1. [VERIFIED: local `--version` commands]

## Architecture Patterns

### Recommended Project Structure
```text
tools/bazel/
├── manifests/
│   └── phase27_retained_code_acceptance_decisions_contract.json
├── phase27_retained_code_acceptance_decisions.py
├── phase27_retained_code_acceptance_decisions_test.py
└── BUILD.bazel

build/ci-evidence/phase27/
├── acceptance-run-manifest.json
├── normalized-retained-code-decisions.json
├── residual-risk-register.json
├── exception-decision-register.json
├── final-readiness-decision-summary.json
├── phase28-handoff-manifest.json
├── decision-row-table.json
├── maintainer-acceptance-input-template.json
├── artifact-reference-summary.json
└── contract-snapshots/
    ├── phase18_cutover_review_contract.json
    ├── phase26_release_signing_upstream_evidence_contract.json
    └── phase26-upstream-result-row-table.json
```
[VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/phase26_release_signing_upstream_evidence.py]

### Pattern 1: Phase-Owned Wrapper Around Canonical Contracts
**What:** Load Phase 18 contract and Phase 26 upstream rows, assert exact canonical IDs/vocabularies/required fields, then emit Phase 27-specific decision deltas. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**When to use:** Use for all Phase 27 acceptance and final-readiness decisions. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**Example:**
```python
# Source pattern: tools/bazel/phase26_release_signing_upstream_evidence.py
row_ids = [str(row["criterion_id"]) for row in rows]
if row_ids != CANONICAL_PHASE18_CRITERIA:
    raise VerificationError("normalized upstream rows must match the nine canonical Phase 18 criteria")
```
[VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

### Pattern 2: Orthogonal Decision Axes
**What:** Keep `evidence_state`, `maintainer_decision`, `exception_state`, `residual_risk_state`, `hard_failure_state`, and `demotion_authorization` as separate fields before deriving Phase 18-compatible status. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**When to use:** Use for `decision-row-table.json`, `final-readiness-decision-summary.json`, and `phase28-handoff-manifest.json`. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**Example:**
```python
# Source pattern: tools/bazel/phase18_cutover_review.py
status_allows = maintainer_status_allows and upstream_status_allows
```
[VERIFIED: tools/bazel/phase18_cutover_review.py]

### Pattern 3: Hard-Block Before Exception Evaluation
**What:** Redaction, overclaim, source-ref, unsafe-ref, and stale lifecycle failures must set a hard-blocked state before maintainer exception logic runs. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/phase26_release_signing_upstream_evidence.py]

**When to use:** Use while normalizing Phase 26 rows and Phase 27 decision inputs. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; tools/bazel/phase18_cutover_review.py]

**Example:**
```python
# Source pattern: tools/bazel/phase26_release_signing_upstream_evidence.py
if normalized.get("redaction_status") != "passed":
    normalized["status"] = "blocked"
    normalized["maintainer_state"] = "blocked"
```
[VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

### Pattern 4: Safe Retained Outputs Under Build Root
**What:** Validate `--output-dir` is repo-relative, under `build/ci-evidence/phase27`, and not a symlink escape before deleting or writing output. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

**When to use:** Use for every retained Phase 27 output write. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**Example:**
```python
# Source pattern: tools/bazel/phase26_release_signing_upstream_evidence.py
if output_dir.is_absolute() or ".." in output_dir.parts:
    raise VerificationError("--output-dir must be repo-relative")
```
[VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

### Anti-Patterns to Avoid
- **Forking Phase 18 vocabulary:** Causes schema drift and violates D-02. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]
- **Treating upstream pass as acceptance:** Green evidence cannot accept retained code without explicit maintainer input. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]
- **Exception-covering redaction/source lifecycle failures:** Phase 27 hard-blockers cannot be transformed into accepted retained-code risk. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]
- **Setting demotion allowed in Phase 27:** Reference demotion remains a Phase 28 decision. [VERIFIED: .planning/ROADMAP.md; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Acceptance schema | New Phase 27-only schema | Phase 18 `retained_code_acceptance_packet_schema`, `final_decision_schema`, vocabularies, and upstream criteria | Locked decisions require Phase 18 to stay canonical. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md] |
| Exception metadata | Ad hoc exception objects | Phase 18 exception fields: `scope`, `rationale`, `approver`, `approver_role`, `affected_printer_or_release_surface`, `mitigation_or_follow_up`, `expiry_or_review_trigger`, `evidence_refs` | Phase 18 already validates complete exception metadata. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; tools/bazel/phase18_cutover_review.py] |
| Upstream rows | Recomputed evidence status catalog | Phase 26 `upstream-result-row-table.json` and Phase 26 upstream policy | Phase 27 should consume Phase 26 rows without replaying unrelated statuses. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; build/ci-evidence/phase26/upstream-result-row-table.json] |
| Demotion policy | Boolean `approved` flag | Separate Phase 28 handoff with `demotion_authorization: "blocked"` or equivalent non-allowing state | Phase 27 must not authorize demotion. [VERIFIED: .planning/ROADMAP.md; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md] |
| Secret/overclaim scanning | New marker set from scratch | Reuse or narrowly mirror Phase 18/26 forbidden field/text patterns | Existing verifiers already reject secret-bearing fields and overclaim language. [VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Output containment | Direct `shutil.rmtree(output_dir)` | Phase 26-style `validate_output_dir` preflight | Phase 26 tests cover absolute, parent traversal, and symlink escape failures. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; tools/bazel/phase26_release_signing_upstream_evidence_test.py] |

**Key insight:** Phase 27 is not a schema invention phase; it is a decision input and projection phase that must preserve Phase 18 semantics while handing Phase 28 a clean machine-readable delta. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Schema Drift From Phase 18
**What goes wrong:** Phase 27 adds fields/statuses that appear reasonable but do not match Phase 18 retained packet, final decision, exception, or upstream criteria contracts. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json]

**Why it happens:** Phase 27 needs v1.2 outputs, which can tempt the planner to treat projections as a new source of truth. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**How to avoid:** Add exact-match tests for Phase 18 retained packet IDs, final criterion IDs, status vocabularies, exception fields, and upstream criterion IDs. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/phase26_release_signing_upstream_evidence_test.py]

**Warning signs:** Test fixtures copy the Phase 18 row catalog into Phase 27 instead of loading it from `phase18_cutover_review_contract.json`. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

### Pitfall 2: Conflating Evidence Status With Maintainer Acceptance
**What goes wrong:** A passed upstream row becomes `accepted` retained-code or final readiness without maintainer decision input. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**Why it happens:** Phase 26 rows already include `status` and `maintainer_state`, but Phase 26 intentionally leaves Phase 27-owned gates blocked/pending/not-required. [VERIFIED: build/ci-evidence/phase26/upstream-result-row-table.json]

**How to avoid:** Require explicit Phase 27 decision rows with approver, role, timestamp, rationale, residual risk, and evidence refs before deriving accepted/rejected/exception states. [VERIFIED: tools/bazel/phase18_cutover_review.py]

**Warning signs:** Quick mode emits phrases such as `retained-code accepted` or `final approval complete`. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]

### Pitfall 3: Letting Exceptions Cover Hard Blockers
**What goes wrong:** Redaction failures, source-ref failures, stale lifecycle rows, or overclaim failures become exception-approved risk. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**Why it happens:** Phase 18 has exception-coverable upstream statuses, but hard-blocking statuses are explicitly separate. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json]

**How to avoid:** Evaluate hard blockers before exception logic and assert `redaction_status == "passed"`, `source_ref_status == "passed"`, and current/not-required lifecycle before accepting exception coverage. [VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py]

**Warning signs:** A test named like `exception_coverable_status_does_not_become_passed` is missing for Phase 27. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]

### Pitfall 4: Fresh Checkout Missing Phase 26 Generated Rows
**What goes wrong:** `just phase27-verify` fails because `build/ci-evidence/phase26/upstream-result-row-table.json` is generated and not committed. [VERIFIED: build/ci-evidence/phase26/upstream-result-row-table.json; git ls-files build/ci-evidence]

**Why it happens:** Prior phases retain evidence under ignored build outputs. [VERIFIED: .planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md]

**How to avoid:** In the Phase 27 workflow, run Phase 26 quick generation before Phase 27 quick consumption, or make Phase 27 fail with a precise instruction and keep `just phase27-verify` ordered to generate Phase 26 first. [VERIFIED: tools/bazel/rust_workflow.sh; tools/bazel/phase26_release_signing_upstream_evidence.py]

**Warning signs:** Phase 27 tests rely on a pre-existing local `build/ci-evidence/phase26` directory instead of creating it in a temp root. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]

### Pitfall 5: Over-Approving Phase 28 Decisions
**What goes wrong:** Phase 27 emits `demotion_allowed: true` or equivalent. [VERIFIED: .planning/ROADMAP.md; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**Why it happens:** Phase 18 can compute demotion status when complete decisions and upstream results pass, but Phase 27's boundary explicitly stops before reference demotion. [VERIFIED: tools/bazel/phase18_cutover_review.py; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**How to avoid:** Emit a Phase 28 handoff manifest that states demotion authorization is blocked/not-approved and lists remaining Phase 28 inputs. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

**Warning signs:** Security tests only scan run manifests, not every generated JSON/Markdown output. [VERIFIED: tools/bazel/phase18_cutover_review_test.py; tools/bazel/phase26_release_signing_upstream_evidence_test.py]

## Code Examples

### Validate Complete Exception Metadata
```python
# Source: tools/bazel/phase18_cutover_review.py
def validate_exception_metadata(exception: Any, row_name: str) -> dict[str, Any]:
    if not isinstance(exception, dict):
        raise VerificationError(f"{row_name} exception must be an object")
    require_fields(exception, EXCEPTION_REQUIRED_FIELDS, f"{row_name} exception")
    evidence_refs = require_list_of_strings(exception, "evidence_refs", f"{row_name} exception")
    require_non_empty_refs(evidence_refs, f"{row_name} exception", "evidence_refs")
    return exception
```
[VERIFIED: tools/bazel/phase18_cutover_review.py]

### Require Explicit Retained-Code Evidence Refs
```python
# Source: tools/bazel/phase18_cutover_review.py
if status in {"accepted", "deferred-approved-exception"}:
    require_non_empty_refs(supplied_refs, row_name, "supplied_evidence_result_refs")
```
[VERIFIED: tools/bazel/phase18_cutover_review.py]

### Preserve Phase 26 Hard-Block Semantics
```python
# Source: tools/bazel/phase26_release_signing_upstream_evidence.py
elif normalized.get("source_lifecycle_status") not in {"current", "not-required"}:
    normalized["status"] = "blocked"
    normalized["failure_reason"] = "lifecycle-mismatch: source lifecycle is not current"
    normalized["maintainer_state"] = "blocked"
```
[VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Source-backed local proof and prose review notes | Machine-readable retained evidence packets, upstream rows, and maintainer decision inputs | v1.1 Phase 18 and Phase 21, shipped 2026-06-20 to 2026-06-21 | Phase 27 can build on canonical schemas instead of inventing acceptance from prose. [VERIFIED: .planning/milestones/v1.1-ROADMAP.md; tools/bazel/manifests/phase18_cutover_review_contract.json] |
| Quick checks that only validate local contracts | v1.2 execution wrappers that retain redacted outputs under `build/ci-evidence/phaseXX` | v1.2 Phases 23-26, completed 2026-06-23 to 2026-06-24 | Phase 27 should emit retained evidence outputs and row tables in the same style. [VERIFIED: .planning/ROADMAP.md; .planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md] |
| Final demotion implied by green evidence | Final demotion stays blocked unless explicitly approved in Phase 28 | Active v1.2 roadmap | Phase 27 may approve/block readiness criteria but must not authorize reference demotion. [VERIFIED: .planning/ROADMAP.md; .planning/REQUIREMENTS.md] |
| ASVS 4 category shorthand such as V2 Authentication/V5 Input Validation | ASVS 5.0.x category numbering starts with V1 Encoding and Sanitization, V2 Validation and Business Logic, V11 Cryptography, V13 Configuration, V15 Secure Coding and Architecture, and V16 Security Logging/Error Handling | ASVS 5.0.0 stable dated May 2025 | Security mapping should use current ASVS 5 category names, not older numbering. [CITED: https://github.com/OWASP/ASVS; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html] |

**Deprecated/outdated:**
- Treating final readiness approval as prose-only notes is out of scope for ACPT-03. [VERIFIED: .planning/REQUIREMENTS.md]
- Treating signed maintainer attestations as Phase 27 scope is deferred. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|

All claims in this research were verified or cited in this session; no user confirmation is needed before planning. [VERIFIED: local file reads; cited official OWASP sources]

## Open Questions

1. **Should Phase 27 encode an additional sensitive-surface reviewer role matrix beyond Phase 18 packet `approver_role`?**
   - What we know: Phase 18 retained packets already define per-packet approver roles, including `network-security-maintainer`, `release-maintainer`, and `safety-maintainer`. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json]
   - What's unclear: D-11 says to prefer stricter reviewer-role checks for sensitive surfaces, but it does not prescribe whether final-readiness criteria need a new role matrix. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]
   - Recommendation: Use Phase 18 retained packet roles for retained reviews, and add a small Phase 27 `sensitive_role_policy` only for final-readiness decisions that touch safety, release/signing, TLS, credential, crash-dump, or hardware-adjacent criteria. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]

2. **Should Phase 27 generate Phase 26 quick outputs or require them as a pre-existing input?**
   - What we know: Phase 26 generated rows live under `build/ci-evidence/phase26` and are not source-tracked. [VERIFIED: .planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md; git ls-files build/ci-evidence]
   - What's unclear: The Phase 27 context requires consuming Phase 26 rows but does not specify command ordering. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]
   - Recommendation: Make `phase27_verify` run Phase 26 quick first, then Phase 27 quick with `--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json`. [VERIFIED: tools/bazel/rust_workflow.sh; tools/bazel/phase26_release_signing_upstream_evidence.py]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 27 verifier and tests | Yes | 3.14.4 | None needed. [VERIFIED: python3 --version] |
| Bazel | `//tools/bazel:phase27_verify` and test labels | Yes | 9.1.1 | Direct Python commands if Bazel is unavailable. [VERIFIED: bazel --version; tools/bazel/BUILD.bazel] |
| just | `just phase27-verify` facade | Yes | 1.48.0 | Bazel labels directly. [VERIFIED: just --version; justfile] |
| cargo | Required pre-commit Rust checks | Yes | 1.91.1 | None under repo rules. [VERIFIED: cargo --version; AGENTS.md] |
| jq | Manual JSON inspection | Yes | 1.7.1 | Python JSON one-liners. [VERIFIED: jq --version] |

**Missing dependencies with no fallback:** None found. [VERIFIED: local version probes]

**Missing dependencies with fallback:** None found. [VERIFIED: local version probes]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python `unittest` for phase verifier tests; Bazel `shell_binary` labels; Cargo checks for Rust workspace. [VERIFIED: tools/bazel/phase18_cutover_review_test.py; tools/bazel/phase26_release_signing_upstream_evidence_test.py; AGENTS.md] |
| Config file | None for phase verifier `unittest`; `pyproject.toml` exists for pytest integration tests but Phase 18/26 tools use direct `python3 ..._test.py`. [VERIFIED: tools/bazel/phase18_cutover_review_test.py; tools/bazel/phase26_release_signing_upstream_evidence_test.py; pyproject.toml] |
| Quick run command | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py && python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --output-dir build/ci-evidence/phase27` after files exist. [VERIFIED: tools/bazel/rust_workflow.sh pattern] |
| Full suite command | `just phase27-verify` after wiring exists; before commit, also run the required Cargo sequence. [VERIFIED: justfile; AGENTS.md] |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| ACPT-02 | Maintainer decisions accept, reject, block, or exception every Phase 18 retained packet with rationale, residual risk, approver role, timestamp, and evidence refs. [VERIFIED: .planning/REQUIREMENTS.md; tools/bazel/phase18_cutover_review.py] | unit + quick smoke | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - Wave 0 must create it. [VERIFIED: rg phase27] |
| ACPT-02 | Exceptions require scope, owner/approver, affected scope, rationale, evidence refs, residual risk, mitigation/follow-up, and expiry/revisit trigger. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/manifests/phase18_cutover_review_contract.json] | unit | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - Wave 0 must create it. [VERIFIED: rg phase27] |
| ACPT-03 | Final-readiness criteria are approved or blocked through machine-readable decision rows, not prose-only notes. [VERIFIED: .planning/REQUIREMENTS.md] | unit + quick smoke | `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --output-dir build/ci-evidence/phase27` | No - Wave 0 must create it. [VERIFIED: rg phase27] |
| ACPT-03 | Phase 27 output distinguishes evidence failures, accepted retained-code risks, unresolved residual risks, and demotion approval state while keeping demotion blocked/not-approved. [VERIFIED: .planning/ROADMAP.md; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md] | unit + security/overclaim | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - Wave 0 must create it. [VERIFIED: rg phase27] |

### Sampling Rate
- **Per task commit:** `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py`, `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --contract-only`, `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --security-only`, and changed-path wiring checks once implemented. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py pattern]
- **Per wave merge:** `just phase27-verify` plus the repo-required Cargo sequence before commit. [VERIFIED: justfile; AGENTS.md]
- **Phase gate:** `just phase27-verify`, `git diff --check`, and the Cargo sequence green before `/gsd-verify-work`. [VERIFIED: AGENTS.md; standards/core/verification.md]

### Wave 0 Gaps
- [ ] `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` - Phase 27 source contract and output file list. [VERIFIED: rg phase27]
- [ ] `tools/bazel/phase27_retained_code_acceptance_decisions.py` - verifier, normalizer, retained output writer, and CLI. [VERIFIED: rg phase27]
- [ ] `tools/bazel/phase27_retained_code_acceptance_decisions_test.py` - regression tests for ACPT-02 and ACPT-03. [VERIFIED: rg phase27]
- [ ] Bazel/root/just/wiring entries for `phase27_verify` and `phase27_verify_tests`. [VERIFIED: BUILD.bazel; tools/bazel/BUILD.bazel; tools/bazel/rust_workflow.sh; justfile]

## Security Domain

### Applicable ASVS Categories

ASVS 5.0.0 is the latest stable ASVS version dated May 2025, and ASVS 5 category numbering differs from the older V2 Authentication/V5 Input Validation shorthand. [CITED: https://github.com/OWASP/ASVS; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V1 Encoding and Sanitization | Yes | Reject secret-bearing fields/text and overclaim phrases before retaining outputs; use strict JSON parsing and safe refs. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase18_cutover_review.py] |
| V2 Validation and Business Logic | Yes | Parse machine-readable inputs into explicit decision axes; reject impossible combinations such as acceptance without evidence refs. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase18_cutover_review.py] |
| V4 API and Web Service | No | Phase 27 adds local/offline verifier inputs, not a network API. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md] |
| V6 Authentication / V7 Session Management / V8 Authorization | No | Phase 27 records maintainer identity/role strings in evidence artifacts but does not implement runtime authentication, sessions, or access control. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json] |
| V11 Cryptography | Indirect | Do not retain private keys, raw signing payloads, private certificates, tokens, or credentials; retain signing identity by reference only. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| V13 Configuration | Yes | Keep generated evidence under `build/ci-evidence/phase27`, enforce output-root containment, and snapshot source contracts. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| V15 Secure Coding and Architecture | Yes | Use functional core / imperative shell and exact schema validation instead of ad hoc primitive checks. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: standards/core/architecture.md] |
| V16 Security Logging and Error Handling | Yes | Fail closed with explicit `VerificationError` messages and retained summaries that distinguish blockers, exceptions, residual risks, and handoff state. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py] |

### Known Threat Patterns for Phase 27

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secret material retained in decision inputs or outputs | Information Disclosure | Reject forbidden fields/text before output writes and scan generated artifacts. [VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase18_cutover_review_test.py] |
| Path traversal or symlink escape in output directory | Tampering | Require repo-relative output under `build/ci-evidence/phase27` and reject symlink components. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; tools/bazel/phase26_release_signing_upstream_evidence_test.py] |
| Maintainer decision overclaiming final demotion | Elevation of Privilege | Emit no `demotion_allowed: true`; use Phase 28 handoff state only. [VERIFIED: .planning/ROADMAP.md; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md] |
| Exception laundering of hard evidence failures | Tampering | Evaluate redaction/source/lifecycle/overclaim hard blockers before exception coverage. [VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Schema drift causing wrong acceptance coverage | Repudiation | Exact-match Phase 18 packet/criterion/vocabulary tests and Phase 26 upstream row required-field tests. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py; tools/bazel/phase18_cutover_review_test.py] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md` - locked decisions, scope, outputs, and integration points. [VERIFIED]
- `.planning/REQUIREMENTS.md` - ACPT-02 and ACPT-03 requirement text. [VERIFIED]
- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/PROJECT.md` - milestone posture, Phase 27/28 boundaries, demotion policy. [VERIFIED]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/testing.md`, `standards/core/verification.md`, `standards/languages/rust.md` - project and standards constraints. [VERIFIED]
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - canonical retained packet, final decision, exception, status, upstream, and demotion contract. [VERIFIED]
- `tools/bazel/phase18_cutover_review.py` and `tools/bazel/phase18_cutover_review_test.py` - implementation/test patterns for decision validation, upstream consumption, hard blockers, residual-risk, and demotion blocking. [VERIFIED]
- `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json`, `tools/bazel/phase26_release_signing_upstream_evidence.py`, and `tools/bazel/phase26_release_signing_upstream_evidence_test.py` - v1.2 upstream-row and retained-output pattern. [VERIFIED]
- `build/ci-evidence/phase26/upstream-result-row-table.json` - current generated Phase 26 upstream row shape and statuses. [VERIFIED]
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - wiring conventions. [VERIFIED]

### Secondary (MEDIUM confidence)
- OWASP ASVS GitHub README - ASVS 5.0.0 latest stable version and ASVS requirement reference guidance. [CITED: https://github.com/OWASP/ASVS]
- OWASP Cheat Sheet ASVS index - ASVS 5.0.x category index. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Tertiary (LOW confidence)
- None. [VERIFIED: source review]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - existing local verifiers and tool versions were verified directly. [VERIFIED: tools/bazel/phase18_cutover_review.py; tools/bazel/phase26_release_signing_upstream_evidence.py; local version probes]
- Architecture: HIGH - Phase 27 locked decisions, Phase 18 contract, and Phase 26 output producer all point to the same wrapper pattern. [VERIFIED: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md; tools/bazel/manifests/phase18_cutover_review_contract.json; tools/bazel/phase26_release_signing_upstream_evidence.py]
- Pitfalls: HIGH - pitfalls are backed by existing Phase 18/26 regression tests and locked Phase 27 decisions. [VERIFIED: tools/bazel/phase18_cutover_review_test.py; tools/bazel/phase26_release_signing_upstream_evidence_test.py; .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md]
- Security domain: MEDIUM - current ASVS version/category facts were verified from official OWASP/GitHub sources, while phase-specific controls are mapped from local code behavior. [CITED: https://github.com/OWASP/ASVS; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase18_cutover_review.py]

**Research date:** 2026-06-25
**Valid until:** 2026-07-25 for local contract/wiring facts; re-check ASVS/version-sensitive security references if planning after that date. [CITED: https://github.com/OWASP/ASVS]
