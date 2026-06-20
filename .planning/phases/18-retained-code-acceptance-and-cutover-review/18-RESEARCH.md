# Phase 18: Retained-Code Acceptance and Cutover Review - Research

**Researched:** 2026-06-20
**Domain:** Evidence governance, retained-code acceptance, final cutover review, Python verifier contracts
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md) [VERIFIED: .planning/phases/18-retained-code-acceptance-and-cutover-review/18-CONTEXT.md]

### Locked Decisions

## Implementation Decisions

### Retained-code acceptance packets

- **D-01:** Use a Phase 18-owned row-level JSON acceptance packet contract as the authoritative retained-code acceptance model.
- **D-02:** Every retained C, C++, ASM, generated, vendor, HAL, RTOS, network, filesystem, signing, release-artifact, resource, MMU, auxiliary-controller, and runtime surface that remains at cutover needs a packet or an explicitly verified row mapping from the Phase 11 retained-code justifications.
- **D-03:** Each packet should require stable identity, taxonomy tags, retained source refs, prior phase refs, required evidence refs, supplied evidence result refs, owner, approver role, approval metadata, status, rationale, residual risk, blocker or deferred action, exception ref, secret-handling policy, and unsupported-claim guards.
- **D-04:** Use statuses that distinguish evidence collection from review: `pending-evidence`, `pending-maintainer-review`, `accepted`, `rejected`, `blocked`, `deferred-approved-exception`, `rejected-redaction`, and `rejected-overclaim`.
- **D-05:** Generate a maintainer-readable checklist or summary from the row-level packets for review ergonomics, but keep the JSON packets and verifier as the source of truth.

### Final reference-demotion checklist

- **D-06:** Model final-demotion review as an evidence index plus maintainer decision packet rather than prose-only approval. The evidence index resolves Phase 13-17 and archived Phase 11 evidence; the decision packet records approve, reject, or exception decisions.
- **D-07:** The checklist must link CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence. It should also preserve source-backed local proof versus non-local supplied evidence and maintainer-only approval boundaries.
- **D-08:** `demotion_allowed` must be derived deterministically. It may be true only when every required criterion is `passed`, `exception-approved`, or validly `not-applicable`; any `pending`, `failed`, `blocked`, `exception-requested`, `exception-rejected`, redaction rejection, or overclaim rejection keeps demotion false.
- **D-09:** Approved exceptions must require scope, rationale, approver, affected printer/release surface, mitigation or follow-up, expiry or review trigger, and links to the Phase 13-17 or archived v1.0 evidence that justifies the exception.
- **D-10:** Do not implement a broad policy mini-engine in this phase. Keep the evaluator explicit, reviewable, and close to the row schema.

### Final readiness dossier

- **D-11:** Use the Phase 13-17 pattern: checked-in contracts, schemas, verifier logic, dry-run examples, Bazel labels, and `just phase18-verify`; generated run manifests, retained-code snapshots, residual-risk registers, redacted summaries, and readiness reports live under `build/ci-evidence/phase18`.
- **D-12:** The generated human-readable readiness report is review material, not the authority. The machine-readable gate rows and maintainer decision input determine final status.
- **D-13:** Generated Phase 18 artifacts should include a run manifest, normalized final-demotion results, retained-code acceptance summary, residual-risk register, redacted readiness report, source-contract snapshot, and maintainer decision input template.
- **D-14:** The verifier must reject secret leakage, raw firmware payloads, raw crash dumps, credential values, private keys/certificates, path traversal, stale or missing source refs, local-only proof overclaims, retained-code acceptance overclaims, and reference-demotion approval without maintainer decision input.

### Traceability and workflow integration

- **D-15:** Every Phase 18 row must map to `REV-01`, `REV-02`, and/or `REV-03`, plus the relevant archived v1.0 and Phase 11 evidence rows and the applicable Phase 13-17 contract rows.
- **D-16:** Add a dedicated Phase 18 standard-library Python verifier/collector, likely `tools/bazel/phase18_cutover_review.py`, with focused unit tests in `tools/bazel/phase18_cutover_review_test.py`.
- **D-17:** Expose Phase 18 through a checked-in contract manifest, Bazel `phase18_verify` and `phase18_verify_tests` labels, root docs/alias filegroups, `tools/bazel/rust_workflow.sh`, and `just phase18-verify`.
- **D-18:** Local phase verification should be deterministic: validate contract schema, required review rows, source refs, wiring, dry-run generated artifacts, redaction, path guards, approval/exception semantics, demotion computation, and overclaim guards without requiring real maintainer sign-off.
- **D-19:** Preserve Phase 13 artifact-retention, Phase 14 simulator, Phase 15 hardware, Phase 16 live-service, and Phase 17 release/signing boundaries. Supporting evidence can feed Phase 18, but none of those gates should be silently upgraded to final cutover approval.

### the agent's Discretion

- Exact packet IDs, schema field order, status spelling, generated artifact filenames, helper boundaries, and dry-run output shape are flexible if the result stays deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated implementation plan with multiple tasks; the roadmap expects one completed plan for this phase.
- Prefer explicit JSON contracts and verifier tests over prose-only checklists. Human-facing review text is useful only when backed by machine-readable rows and verifier checks.
- External assurance vocabulary such as VEX, SLSA, in-toto, or GSN can inform names or future exports, but Phase 18 should not add a new attestation trust root unless the existing repo evidence contract needs it.

### Deferred Ideas (OUT OF SCOPE)

## Deferred Ideas

None - discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements [VERIFIED: .planning/REQUIREMENTS.md]

| ID | Description | Research Support |
|----|-------------|------------------|
| REV-01 | Maintainer can review retained-code acceptance packets for every C, C++, ASM, generated, vendor, HAL, RTOS, network, filesystem, and signing surface that remains at cutover. | Use a Phase 18 JSON packet contract seeded from Phase 11 retained-code rows, `foreign_code_inventory.json`, and `unsafe_boundary_audit.json`; verify coverage or explicit mappings for all required retained surfaces. [VERIFIED: 18-CONTEXT.md; tools/bazel/manifests/phase11_retained_code_justifications.json; tools/bazel/manifests/foreign_code_inventory.json; tools/bazel/manifests/unsafe_boundary_audit.json] |
| REV-02 | Maintainer can approve or reject final reference-demotion criteria through an explicit checklist that links CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence. | Build a final-demotion evidence index plus decision packet; resolve source refs into Phase 13-17 contracts and archived Phase 11 cutover rows, then generate a maintainer checklist as derived review output. [VERIFIED: 18-CONTEXT.md; phase13-17 contract manifests; tools/bazel/manifests/phase11_cutover_readiness.json] |
| REV-03 | Maintainer can produce a final cutover readiness report that marks reference demotion allowed only when all required gates pass or have documented maintainer-approved exceptions. | Derive `demotion_allowed` deterministically from final criterion statuses; no quick/local run may set it true without a valid decision input and all criteria `passed`, `exception-approved`, or valid `not-applicable`. [VERIFIED: 18-CONTEXT.md D-08, D-14, D-18] |
</phase_requirements>

## Summary

Phase 18 should be implemented as the final evidence-governance layer, not as another local proof generator. The established repo pattern is a checked-in JSON contract, a standard-library Python verifier, deterministic quick artifacts under `build/ci-evidence/phaseXX`, Bazel labels, and a `just phaseXX-verify` facade; Phase 13 through Phase 17 all follow that shape. [VERIFIED: tools/bazel/phase13_ci_evidence.py; tools/bazel/phase14_simulator_evidence.py; tools/bazel/phase15_hardware_evidence.py; tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/BUILD.bazel; justfile]

The core planning risk is overclaiming. Phase 11 kept reference demotion blocked with `demotion_allowed: false`, and Phase 17 still leaves release/signing/comparison evidence as pending without approved release input. Phase 18 may aggregate those gates for maintainer review, but it must not convert CI, simulator, hardware, live-service, release, retained-code, or residual-risk rows into final approval unless the maintainer decision packet explicitly supplies valid approvals or exceptions. [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md; 18-CONTEXT.md]

**Primary recommendation:** Implement `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`, and `tools/bazel/manifests/phase18_cutover_review_contract.json` as an explicit row-level acceptance and decision evaluator with generated review artifacts under `build/ci-evidence/phase18`. [VERIFIED: 18-CONTEXT.md D-11, D-16, D-17]

## Project Constraints (from AGENTS.md)

- Use `AGENTS.md` as the repo-local instruction entrypoint, then read `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before planning or implementation work. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md]
- The project constraints are Big Bang migration, behavior parity, Bazel Primary Now, a required `justfile`, Bright Builds Rules, evidence-backed safety validation, and named/justified retained third-party code. [VERIFIED: AGENTS.md; .planning/PROJECT.md]
- Direct repo edits should happen through GSD workflow artifacts unless the user explicitly bypasses GSD; this research is the GSD Phase 18 research artifact. [VERIFIED: AGENTS.md]
- Bright Builds architecture guidance favors functional core / imperative shell, parse-at-boundary domain values, and illegal-state prevention when practical. [VERIFIED: standards/core/architecture.md]
- Bright Builds code-shape guidance favors early returns, `maybe` naming for internal optional values, no substantial foreign-language logic hidden in strings, rerunnable scripts, and refactor triggers for very large functions/files. [VERIFIED: standards/core/code-shape.md]
- Bright Builds verification guidance requires repo-native verification before commit and prefers repo-owned verification entrypoints such as `just` or Bazel labels. [VERIFIED: standards/core/verification.md]
- Bright Builds testing guidance requires pure/business logic unit tests, one concern per unit test, and clear Arrange/Act/Assert structure. [VERIFIED: standards/core/testing.md]
- `standards-overrides.md` has no active local override beyond the placeholder row, so the managed standards apply. [VERIFIED: standards-overrides.md]
- No project-local skills were found under `.claude/skills/` or `.agents/skills/`. [VERIFIED: find .claude/skills .agents/skills -maxdepth 2 -name SKILL.md]

## Standard Stack

### Core

| Tool / Library | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python standard library | Python 3.14.4 available locally | Implement the Phase 18 verifier, JSON parsing, path checks, UTC timestamp parsing, regex scans, artifact writing, and `unittest` tests. | Existing phase verifiers are standard-library Python scripts with no third-party package dependency. [VERIFIED: `python3 --version`; tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase17_release_candidate_evidence_test.py] |
| JSON manifests | Existing checked-in manifests | Define authoritative retained-code packets, final-demotion criteria, source refs, decision schemas, status vocabulary, and artifact kinds. | Phase 11 and Phase 13-17 use checked-in JSON manifests as durable source contracts. [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json; tools/bazel/manifests/phase17_release_candidate_evidence_contract.json] |
| Bazel `shell_binary` via repo `shell_rules.bzl` | Bazel 9.1.1 available locally | Expose `phase18_verify` and `phase18_verify_tests` through `tools/bazel/BUILD.bazel` and root aliases. | Phase 13-17 verifier labels are Bazel `shell_binary` rules dispatched through `rust_workflow.sh`. [VERIFIED: `bazel --version`; tools/bazel/BUILD.bazel; tools/bazel/rust_workflow.sh] |
| `just` | just 1.48.0 available locally | Provide `just phase18-verify` facade running tests before verifier. | Existing Phase 13-17 recipes run `phaseX_verify_tests` before `phaseX_verify`. [VERIFIED: `just --version`; justfile] |

### Supporting

| Tool / Library | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| `jq` | jq 1.7.1 available locally | Inspect JSON contracts during planning and verification debugging. | Useful for manual spot checks; not required by the Phase 18 verifier. [VERIFIED: `jq --version`; local JSON inspection commands] |
| Node GSD tools | Node 24.13.0 available locally | Lifecycle/init and optional GSD commit helpers. | Use for GSD lifecycle checks and optional docs commit flow, not for verifier implementation. [VERIFIED: `node --version`; gsd-tools init output] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Phase 18 JSON contract plus explicit evaluator | Prose-only checklist | Rejected because the context says JSON packets and verifier remain authoritative, with human-readable reports derived from machine rows. [VERIFIED: 18-CONTEXT.md D-05, D-12] |
| Explicit row evaluator | Broad policy mini-engine | Rejected because the context explicitly forbids a broad policy mini-engine for this phase. [VERIFIED: 18-CONTEXT.md D-10] |
| Existing local source-ref resolver pattern | New attestation trust root | Rejected for Phase 18 unless needed by existing repo evidence contract; context says external assurance vocabularies may inform names but should not add a new trust root. [VERIFIED: 18-CONTEXT.md agent discretion] |

**Installation:** No new package install is recommended; use existing Python standard library, Bazel, and just. [VERIFIED: Phase 13-17 verifiers; environment audit commands]

**Version verification:** Package registry verification is not applicable because this phase should not add npm, pip, Cargo, or other external dependencies. Local tool versions were verified with `python3 --version`, `bazel --version`, `just --version`, `jq --version`, and `node --version`. [VERIFIED: environment availability audit]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase18_cutover_review.py                 # Phase 18 verifier/collector
├── phase18_cutover_review_test.py            # stdlib unittest regression suite
├── manifests/
│   └── phase18_cutover_review_contract.json  # authoritative packet/checklist contract
├── BUILD.bazel                               # phase18_verify and phase18_verify_tests labels
└── rust_workflow.sh                          # phase18 dispatch cases

BUILD.bazel                                   # Phase 18 docs filegroup and root aliases
justfile                                      # just phase18-verify
build/ci-evidence/phase18/                   # ignored generated runtime evidence
```

This mirrors Phase 13-17 wiring and keeps generated evidence out of checked-in source. [VERIFIED: tools/bazel/BUILD.bazel; BUILD.bazel; justfile; 18-CONTEXT.md D-11]

### Pattern 1: Phase-Owned Row Contract

**What:** Add `phase18_cutover_review_contract.json` with top-level metadata, `status_vocabulary`, `retained_code_packet_schema`, `final_decision_schema`, `source_ref_collections`, `retained_code_acceptance_packets`, and `final_demotion_criteria`. [VERIFIED: 18-CONTEXT.md D-01, D-03, D-06, D-15]

**When to use:** Use this for all retained-code acceptance and final-demotion criteria; do not mutate Phase 11 or Phase 13-17 source contracts to mean Phase 18 approval. [VERIFIED: 18-CONTEXT.md D-06, D-19; phase13-17 contexts]

**Implementation notes:** The source-ref resolver must support row collections with different identity keys: Phase 11 retained rows use `id`, foreign-code inventory uses `components[].id`, unsafe boundary audit uses `surfaces[].surface_id`, Phase 13 uses `gates[].id`, Phase 14-16 use `scenarios[].id`, and Phase 17 uses `rows[].id`. [VERIFIED: tools/bazel/manifests/phase11_retained_code_justifications.json; tools/bazel/manifests/foreign_code_inventory.json; tools/bazel/manifests/unsafe_boundary_audit.json; phase13-17 contract manifests]

### Pattern 2: Retained-Code Packets with Explicit Coverage

**What:** Each acceptance packet should carry stable identity, taxonomy tags, retained source refs, prior phase refs, required evidence refs, supplied result refs, owner, approver role, status, rationale, residual risk, blocker/deferred action, exception ref, secret-handling policy, and unsupported-claim guards. [VERIFIED: 18-CONTEXT.md D-03]

**When to use:** Use one packet per retained surface or an explicitly verified mapping from Phase 11 retained-code justifications; the verifier should fail if a required retained surface is neither packeted nor mapped. [VERIFIED: 18-CONTEXT.md D-02; tools/bazel/manifests/phase11_retained_code_justifications.json]

**Coverage seed:** Phase 11 has 8 retained-code rows; foreign-code inventory has 31 component IDs; unsafe boundary audit has 21 boundary rows. Phase 18 should validate coverage or explicit mappings across those inputs. [VERIFIED: `jq` inspection of phase11_retained_code_justifications.json, foreign_code_inventory.json, unsafe_boundary_audit.json]

### Pattern 3: Final Evidence Index plus Maintainer Decision Packet

**What:** Build a normalized evidence index that links Phase 13 CI gates, Phase 14 simulator scenarios, Phase 15 hardware scenarios, Phase 16 live-service scenarios, Phase 17 release rows, Phase 11 cutover criteria, retained-code packets, and residual-risk entries. Accept an optional maintainer decision input that records approve, reject, or exception decisions. [VERIFIED: 18-CONTEXT.md D-06, D-07, D-13]

**When to use:** Use generated index/report artifacts for review ergonomics, but derive final status only from validated machine-readable rows and decision input. [VERIFIED: 18-CONTEXT.md D-12]

**Recommended generated files:** `run-manifest.json`, `normalized-final-demotion-results.json`, `retained-code-acceptance-summary.json`, `residual-risk-register.json`, `redacted-readiness-report.md`, `source-contract-snapshots/phase18_cutover_review_contract.json`, and `maintainer-decision-input-template.json`. [VERIFIED: 18-CONTEXT.md D-13]

### Pattern 4: Deterministic Demotion Evaluator

**What:** Keep `demotion_allowed` a pure function of validated criteria statuses and validated maintainer exceptions. Allowed statuses are `passed`, `exception-approved`, and valid `not-applicable`; everything else blocks demotion. [VERIFIED: 18-CONTEXT.md D-08]

**When to use:** Run this in quick mode and in decision-input mode. Without a decision input, generated quick artifacts should leave maintainer-owned criteria pending and `demotion_allowed` false. [VERIFIED: 18-CONTEXT.md D-14, D-18; phase17 quick pending behavior in 17-VERIFICATION.md]

**Example:**

```python
ALLOWED_DEMOTION_STATUSES = {"passed", "exception-approved", "not-applicable"}


def demotion_allowed(rows: list[dict[str, object]]) -> bool:
    for row in rows:
        if row["status"] not in ALLOWED_DEMOTION_STATUSES:
            return False
        if row["status"] == "not-applicable" and not row.get("not_applicable_rationale"):
            return False
    return True
```

This is a Phase 18 version of the explicit evaluator requested by D-08/D-10, not a general policy engine. [VERIFIED: 18-CONTEXT.md D-08, D-10]

### Pattern 5: Security and Overclaim Scan as First-Class Behavior

**What:** Reuse the Phase 17 scanner pattern: reject forbidden field names, private key/certificate markers, raw payload markers, credential assignments, path traversal, and overclaim phrases in contracts, external inputs, and generated artifacts. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; 18-CONTEXT.md D-14]

**When to use:** Run in `--security-only`, `--quick`, and while validating optional decision/acceptance input. [VERIFIED: phase17 verifier modes; 18-CONTEXT.md D-14, D-18]

### Anti-Patterns to Avoid

- **Umbrella approval row:** A single `cutover-approved` row would hide which surface failed or was excepted. Use per-criterion rows and packet-level statuses. [VERIFIED: 18-CONTEXT.md D-02, D-06]
- **Dry-run approval:** Quick/local artifacts must not approve reference demotion without maintainer input. [VERIFIED: 18-CONTEXT.md D-08, D-14, D-18]
- **Mutating archived v1.0 evidence:** Phase 18 should cite archived evidence and layer decisions on top. [VERIFIED: 18-CONTEXT.md phase boundary; v1.0-MILESTONE-AUDIT.md]
- **Treating prior phase pass as final cutover pass:** Phase 13-17 verification reports preserve external or maintainer-owned residual gates. [VERIFIED: phase13-17 VERIFICATION.md files]
- **Hard-coding one manifest row shape:** Existing source manifests use different collection names and identity keys. [VERIFIED: source-ref collection inspection]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Final approval policy | A generic policy/rules engine | Explicit row evaluator close to the Phase 18 schema | The context forbids a broad policy mini-engine and requires deterministic derivation. [VERIFIED: 18-CONTEXT.md D-08, D-10] |
| Maintainer checklist authority | Prose-only Markdown checklist | JSON packets plus generated Markdown/report | The machine-readable gate rows and maintainer decision input determine final status. [VERIFIED: 18-CONTEXT.md D-05, D-12] |
| Evidence source graph | New evidence database | Existing checked-in manifests plus generated `build/ci-evidence/phase18` index | Prior phases already expose source-backed row contracts and generated output roots. [VERIFIED: phase13-17 manifests; 18-CONTEXT.md D-11] |
| Secret scanning | One-off manual review | Existing forbidden-marker and overclaim scanner pattern adapted from Phase 17 | Prior verifiers already reject private keys, credential fields, payload markers, and overclaims. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; phase17 tests] |
| Source refs | Free-form strings without resolution | Whitelisted `file#row-id` refs with approved row collections | Phase 17 already rejects unapproved source manifests and nested/non-row refs. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; phase17 tests] |

**Key insight:** Phase 18 is mostly about making decisions reviewable and falsifiable. Custom engines, prose-only approvals, and unvalidated refs increase ambiguity where the phase needs auditability. [VERIFIED: 18-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Collapsing Evidence Collection into Acceptance

**What goes wrong:** A row with supplied evidence gets marked accepted without maintainer review metadata. [VERIFIED: 18-CONTEXT.md D-04, D-08]

**Why it happens:** Earlier phase rows use `passed` for their own phase-local gate, but Phase 18 needs a separate acceptance/review status. [VERIFIED: phase13-17 status vocabularies]

**How to avoid:** Keep retained packet statuses separate from upstream evidence result statuses; require `pending-maintainer-review` before accepted/rejected/exceptioned final states. [VERIFIED: 18-CONTEXT.md D-04]

**Warning signs:** `demotion_allowed` becomes true without a decision input, or a retained-code packet has `accepted` but no approver/rationale metadata. [VERIFIED: 18-CONTEXT.md D-08, D-14]

### Pitfall 2: Missing Retained Surfaces Outside the Original Eight Rows

**What goes wrong:** The planner covers only Phase 11 retained-code rows and misses narrower foreign-code or unsafe/runtime surfaces. [VERIFIED: phase11_retained_code_justifications.json; foreign_code_inventory.json; unsafe_boundary_audit.json]

**Why it happens:** Phase 11 intentionally compressed retained code into 8 review rows, while Phase 5 inventory has 31 components and unsafe boundary audit has 21 rows. [VERIFIED: jq inspection of source manifests]

**How to avoid:** Add contract coverage checks for Phase 11 retained rows, foreign-code component IDs, and unsafe-boundary `surface_id`s, allowing explicit mappings where one acceptance packet covers several source rows. [VERIFIED: 18-CONTEXT.md D-02]

**Warning signs:** `retained-hal-cmsis-vendor` is present, but no packet/mapping cites specific STM32 startup/linker, board-clock, HAL/CMSIS, or unsafe boundary rows. [VERIFIED: phase11_retained_code_justifications.json; foreign_code_inventory.json; unsafe_boundary_audit.json]

### Pitfall 3: Stale or Unapproved Source Refs

**What goes wrong:** A packet points to a file path or row ID that no longer exists, or to a nested metadata ID instead of an approved row collection. [VERIFIED: phase17 source-ref tests]

**Why it happens:** The repo has archived v1.0 paths and current phase paths, and different manifests use different collection names. [VERIFIED: phase11 verifier archive-aware path handling; source-ref collection inspection]

**How to avoid:** Implement a Phase 18 source-ref whitelist with per-file collection names and row-id keys. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py source ref resolver]

**Warning signs:** Source refs are plain file paths without `#row-id`, use `..`, or point at unapproved manifests. [VERIFIED: Phase 17 source-ref/path guard tests]

### Pitfall 4: Secret or Payload Leakage in Review Inputs

**What goes wrong:** Maintainer decision input includes private signing keys, certificates, firmware payload markers, raw crash dumps, credential values, or unredacted logs. [VERIFIED: 18-CONTEXT.md D-14; .planning/codebase/CONCERNS.md]

**Why it happens:** Phase 18 will aggregate sensitive surfaces across signing, live services, crash dumps, network credentials, and firmware artifacts. [VERIFIED: .planning/codebase/INTEGRATIONS.md; phase16 and phase17 contexts]

**How to avoid:** Scan contract text, optional input files, and generated artifacts before writing final outputs; reject forbidden fields and marker patterns. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py]

**Warning signs:** Fields named `private_key`, `token`, `password`, `secret`, `firmware_payload`, `raw_crash_dump`, or PEM private key blocks appear in input/output. [VERIFIED: Phase 17 forbidden field/text pattern]

### Pitfall 5: Checklist Drift

**What goes wrong:** The generated readiness report says one thing while JSON rows say another. [VERIFIED: 18-CONTEXT.md D-12]

**Why it happens:** Human-readable reports are easier to edit manually than regenerated machine outputs. [VERIFIED: 18-CONTEXT.md D-05, D-12]

**How to avoid:** Treat reports as generated only; verifier should rebuild them from normalized rows and reject source-of-truth claims in prose-only artifacts. [VERIFIED: 18-CONTEXT.md D-12, D-13]

**Warning signs:** A checked-in Markdown readiness report claims final approval without matching JSON decision rows. [VERIFIED: 18-CONTEXT.md D-14]

## Code Examples

Verified patterns from local sources:

### Safe Source-Ref Resolution

```python
SOURCE_REF_ROW_COLLECTIONS = {
    "tools/bazel/manifests/phase11_retained_code_justifications.json": [("retained_code_justifications", "id")],
    "tools/bazel/manifests/foreign_code_inventory.json": [("components", "id")],
    "tools/bazel/manifests/unsafe_boundary_audit.json": [("surfaces", "surface_id")],
}
```

Use Phase 17's `file#row-id` validation pattern, extended to support per-collection ID fields. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; foreign_code_inventory.json; unsafe_boundary_audit.json]

### Decision Input Guard

```python
def require_decision_for_approval(row: dict[str, object]) -> None:
    if row["status"] not in {"passed", "exception-approved"}:
        return
    for field in ["approver", "approver_role", "decision_timestamp", "rationale"]:
        if not row.get(field):
            raise VerificationError(f"{row['id']} missing approval field: {field}")
```

This matches Phase 18's requirement for auditable rationale and approver metadata. [VERIFIED: 18-CONTEXT.md D-03, D-09]

### Quick Mode Output Shape

```python
run_manifest = {
    "phase": PHASE,
    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
    "decision_inputs_supplied": bool(decision_rows),
    "demotion_allowed": False,
    "status_counts": status_counts,
    "source_contract_snapshot_path": snapshot_path.as_posix(),
}
```

The field names should follow Phase 17's quick artifact pattern while keeping demotion false until validated decision input allows it. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; 18-CONTEXT.md D-08, D-13]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 11 retained-code justifications and cutover criteria record final demotion as blocked. | Phase 18 should turn those blockers into reviewable retained-code packets and final maintainer decisions. | Phase 18 scope on 2026-06-20. | Planner must add acceptance and decision artifacts without rewriting Phase 11 evidence. [VERIFIED: phase11_cutover_readiness.json; 18-CONTEXT.md] |
| Phase 13-17 phase-local verifiers prove their own contracts and quick artifacts. | Phase 18 should index those phase outputs and require explicit final review status. | v1.1 Phase 13-17. | Prior `passed` phase-local verification is evidence input, not final demotion approval. [VERIFIED: phase13-17 VERIFICATION.md files] |
| Human-readable reports could be treated as approval records. | Machine-readable packets and decision input are authoritative; reports are generated review material. | Phase 18 D-12. | Planner should not create hand-maintained readiness prose as source of truth. [VERIFIED: 18-CONTEXT.md D-12] |

**Deprecated/outdated:**

- Treating `criteria-reference-demotion-blocked` as satisfied by local checks is invalid; it remains blocked until non-local evidence and maintainer acceptance are attached. [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json]
- Treating Phase 17 representative smoke artifacts as production release proof is invalid; Phase 17 keeps release rows pending without approved release-run input. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|

All claims in this research were verified against local project files, tool output, or phase context; no assumed claims are intentionally relied on. [VERIFIED: source list below]

## Open Questions (RESOLVED)

1. **Who are the concrete approver roles?**
   - What we know: Phase 18 packets require owner, approver role, approval metadata, and auditable rationale. [VERIFIED: 18-CONTEXT.md D-03]
   - What's unclear: The context does not name specific maintainer role labels or people. [VERIFIED: 18-CONTEXT.md]
   - RESOLVED: Use role strings in the schema and examples, not person-specific names. The plan requires approver role metadata and leaves concrete organization-specific role labels as data supplied in maintainer decision input. [VERIFIED: 18-CONTEXT.md D-03, D-09, D-18; 18-01-PLAN.md]

2. **Will Phase 18 consume real maintainer decisions during local verification?**
   - What we know: Local verification must not require real sign-off and should reject reference-demotion approval without decision input. [VERIFIED: 18-CONTEXT.md D-14, D-18]
   - What's unclear: Whether a real decision input will be supplied during final UAT is outside research scope. [VERIFIED: 18-CONTEXT.md]
   - RESOLVED: Generate a decision input template in quick mode and allow optional `--decision-input` validation, while default local quick artifacts remain pending with `demotion_allowed: false`. [VERIFIED: 18-CONTEXT.md D-08, D-13, D-18; 18-01-PLAN.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Verifier and tests | yes | 3.14.4 | None needed. [VERIFIED: `python3 --version`] |
| Bazel | `phase18_verify` and `phase18_verify_tests` labels | yes | 9.1.1 | Direct `python3` verifier commands if Bazel is unavailable during development. [VERIFIED: `bazel --version`] |
| just | `just phase18-verify` facade | yes | 1.48.0 | Direct `bazel run //tools/bazel:phase18_verify_tests` and `bazel run //tools/bazel:phase18_verify`. [VERIFIED: `just --version`] |
| jq | Manual JSON inspection | yes | 1.7.1 | Python `json.tool` or verifier output. [VERIFIED: `jq --version`] |
| Node | GSD lifecycle/init helpers | yes | 24.13.0 | None needed for verifier. [VERIFIED: `node --version`] |

**Missing dependencies with no fallback:** None found for Phase 18 planning. [VERIFIED: environment audit]

**Missing dependencies with fallback:** None found for Phase 18 planning. [VERIFIED: environment audit]

**Worktree note:** `.planning/config.json` was already modified before this research write; leave it untouched. [VERIFIED: `git status --short`]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python standard-library `unittest` run by `python3`. [VERIFIED: tools/bazel/phase17_release_candidate_evidence_test.py] |
| Config file | None for Phase 18 verifier tests; existing phase verifier tests are standalone scripts. [VERIFIED: tools/bazel/*_test.py] |
| Quick run command | `python3 tools/bazel/phase18_cutover_review_test.py && python3 tools/bazel/phase18_cutover_review.py --contract-only && python3 tools/bazel/phase18_cutover_review.py --quick` [VERIFIED: Phase 13-17 verifier command pattern] |
| Full suite command | `just phase18-verify` after Bazel and just wiring exist. [VERIFIED: justfile phase13-17 pattern; 18-CONTEXT.md D-17] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| REV-01 | Contract covers retained-code packets or explicit mappings for required retained surfaces. | unit/contract | `python3 tools/bazel/phase18_cutover_review_test.py Phase18CutoverReviewTest.test_contract_requires_retained_surface_coverage` | No - Wave 0. [VERIFIED: file listing] |
| REV-02 | Final checklist/index links CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence. | unit/contract | `python3 tools/bazel/phase18_cutover_review_test.py Phase18CutoverReviewTest.test_contract_requires_final_demotion_evidence_links` | No - Wave 0. [VERIFIED: file listing] |
| REV-03 | `demotion_allowed` is false unless every criterion passes, is exception-approved, or validly not-applicable. | unit | `python3 tools/bazel/phase18_cutover_review_test.py Phase18CutoverReviewTest.test_demotion_allowed_requires_all_final_gate_statuses` | No - Wave 0. [VERIFIED: file listing] |

### Sampling Rate

- **Per task commit:** `python3 tools/bazel/phase18_cutover_review_test.py` plus the verifier mode touched by the task. [VERIFIED: Phase 13-17 test pattern]
- **Per wave merge:** `bazel run //tools/bazel:phase18_verify_tests && bazel run //tools/bazel:phase18_verify`. [VERIFIED: Phase 13-17 Bazel pattern]
- **Phase gate:** `just phase18-verify`, `python3 tools/bazel/phase18_cutover_review.py --security-only`, and `git diff --check`. [VERIFIED: Phase 13-17 verification reports; standards/core/verification.md]

### Wave 0 Gaps

- [ ] `tools/bazel/phase18_cutover_review.py` - verifier/collector for contract, input, quick artifacts, security, and wiring. [VERIFIED: 18-CONTEXT.md D-16; file listing]
- [ ] `tools/bazel/phase18_cutover_review_test.py` - stdlib regression tests for contract, coverage, decision semantics, security, path guards, and wiring. [VERIFIED: 18-CONTEXT.md D-16; file listing]
- [ ] `tools/bazel/manifests/phase18_cutover_review_contract.json` - authoritative Phase 18 contract. [VERIFIED: 18-CONTEXT.md D-01; file listing]
- [ ] Bazel labels, root aliases/docs filegroup, `rust_workflow.sh` cases, and `just phase18-verify`. [VERIFIED: 18-CONTEXT.md D-17; current wiring scan]

## Security Domain

Security enforcement is enabled by default because `.planning/config.json` does not set `security_enforcement: false`. [VERIFIED: .planning/config.json]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | Yes, for approval metadata integrity rather than runtime login. | Require approver, approver role, timestamp, rationale, and decision input presence before approval states can affect final demotion. [VERIFIED: 18-CONTEXT.md D-03, D-09, D-14] |
| V3 Session Management | No runtime session surface in the Phase 18 local verifier. | Do not add a web/session workflow in this phase. [VERIFIED: 18-CONTEXT.md phase boundary] |
| V4 Access Control | Yes, as an evidence gate boundary. | Only validated maintainer decision rows can produce `passed` or `exception-approved` final-demotion criteria. [VERIFIED: 18-CONTEXT.md D-06, D-08, D-14] |
| V5 Input Validation | Yes. | Validate JSON schemas, status vocabularies, source refs, path containment, UTC timestamps, required fields, and source row existence. [VERIFIED: Phase 17 verifier pattern; 18-CONTEXT.md D-14, D-18] |
| V6 Cryptography | Yes, for signing evidence handling. | Never accept private key/certificate material; reference signing evidence by key identity, digest, and external refs only. [VERIFIED: Phase 17 contract/verifier; .planning/codebase/INTEGRATIONS.md] |

### Known Threat Patterns for Phase 18

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Forged maintainer approval in input JSON | Spoofing / Elevation of privilege | Require complete approval metadata and keep local quick mode pending without decision input. [VERIFIED: 18-CONTEXT.md D-03, D-14, D-18] |
| Tampered source refs or path traversal | Tampering | Whitelist approved manifests, resolve `file#row-id` refs, reject absolute paths and `..`. [VERIFIED: Phase 17 verifier source/path guards] |
| Secret leakage in decision or readiness artifacts | Information disclosure | Reuse forbidden field/text scans for private keys, certificates, credentials, firmware payloads, raw crash dumps, and token/password assignments. [VERIFIED: Phase 17 verifier; 18-CONTEXT.md D-14] |
| Repudiation of exception rationale | Repudiation | Exceptions require scope, rationale, approver, affected surface, mitigation/follow-up, expiry or review trigger, and evidence links. [VERIFIED: 18-CONTEXT.md D-09] |
| Local proof overclaim | Tampering / Elevation of privilege | Reject phrases claiming retained-code acceptance, reference demotion approval, release readiness, or final cutover without valid decision rows. [VERIFIED: Phase 17 overclaim scanner; 18-CONTEXT.md D-14] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-CONTEXT.md` - locked decisions, discretion, deferred scope, canonical refs, and Phase 18 code context.
- `.planning/REQUIREMENTS.md` - `REV-01`, `REV-02`, `REV-03`.
- `.planning/STATE.md` - current milestone state and Phase 18 starting point.
- `.planning/ROADMAP.md` - Phase 18 goal, dependencies, and success criteria.
- `.planning/PROJECT.md` - project constraints, v1.1 objective, and final demotion boundary.
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, `standards/core/testing.md` - repo workflow and standards.
- `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`, and `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - latest complete verifier pattern.
- `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`, `tools/bazel/manifests/phase11_cutover_readiness.json`, and `tools/bazel/manifests/phase11_retained_code_justifications.json` - archived cutover and retained-code patterns.
- `tools/bazel/manifests/phase13_ci_evidence_contract.json`, `phase14_simulator_evidence_contract.json`, `phase15_hardware_evidence_contract.json`, `phase16_live_network_evidence_contract.json` - upstream evidence row inputs.
- `tools/bazel/manifests/foreign_code_inventory.json` and `tools/bazel/manifests/unsafe_boundary_audit.json` - retained-code and unsafe boundary coverage inputs.
- `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - existing verifier wiring.

### Secondary (MEDIUM confidence)

- `.planning/codebase/CONCERNS.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/STRUCTURE.md` - retained-surface, secret, artifact, testing, and integration context generated from the codebase.
- `.planning/phases/13-*/13-VERIFICATION.md`, `.planning/phases/14-*/14-VERIFICATION.md`, `.planning/phases/15-*/15-VERIFICATION.md`, `.planning/phases/16-*/16-VERIFICATION.md`, `.planning/phases/17-*/17-VERIFICATION.md` - passed prior phase boundaries and residual evidence notes.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` and `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md` - v1.0 local proof boundary.

### Tertiary (LOW confidence)

- None. No web-only or unverified ecosystem claims are used.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - verified from existing phase verifiers and local tool versions.
- Architecture: HIGH - Phase 13-17 verifier/manifest/wiring pattern is present and directly reusable.
- Pitfalls: HIGH - pitfalls are grounded in explicit Phase 18 decisions and Phase 11/17 overclaim boundaries.
- Retained-code coverage: HIGH for source inventory existence and counts; MEDIUM for final grouping because packet IDs are discretionary and should be set during planning.
- Security: HIGH - forbidden marker and overclaim scanner behavior exists in prior phase verifiers and Phase 18 context requires equivalent guards.

**Research date:** 2026-06-20
**Valid until:** 2026-07-20 for repo-local patterns; recheck if Phase 13-17 manifests or verifier wiring changes before planning.
