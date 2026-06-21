# Phase 20: Release Candidate Artifact Production - Research

**Researched:** 2026-06-21 [VERIFIED: environment_context]
**Domain:** Bazel-owned release-candidate artifact identity, release-environment evidence inputs, signing/provenance metadata, retention, and comparison classification [VERIFIED: .planning/ROADMAP.md; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Confidence:** HIGH for local contract/verifier and Bazel wiring; MEDIUM for real release-environment artifact production because private signing and full release infrastructure are intentionally outside the repo [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase19_aggregate_ci_evidence.py; ProjectOptions.cmake]

<user_constraints>
## User Constraints (from CONTEXT.md)

The following constraints are copied from `.planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md`. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

### Locked Decisions

#### Artifact Identity Target

- **D-01:** Replace the empty `tools/bazel/BUILD.bazel` `phase17_release_candidate_artifacts` filegroup with a non-empty release identity that resolves to production-safe release outputs or explicit release-environment input artifacts.
- **D-02:** Prefer a hybrid release identity: Bazel should own the artifact identity and any locally producible unsigned or metadata outputs, while private signing and release-only infrastructure remain represented through explicit release-environment input manifests.
- **D-03:** Do not make representative smoke fixtures production evidence. `phase17_representative_release_smoke`, `representative_release_artifacts`, `phase3_verify`, and other local smoke labels stay separate and must remain rejected as sources for `phase17_release_candidate_artifacts`.
- **D-04:** The release identity should cover the surfaces already named by Phase 17: `.bin`, `.bbf`, `.dfu`, map/provenance, resource image/package, language bundle, WUI assets, ESP package, MMU package, Dwarf firmware, ModularBed firmware, xBuddy Extension firmware, package manifest, signing summary, provenance summary, retention manifest, and comparison report.

#### Production Proof Boundary

- **D-05:** Add Phase 20-owned contract and verifier logic that distinguishes production release evidence from smoke evidence through explicit proof classes such as release candidate, approved release run, external release key evidence, local smoke, and placeholder.
- **D-06:** Local deterministic verification may validate schemas, target wiring, generated input templates, path guards, redaction guards, and placeholder handling, but it must not mark release rows passed unless real release outputs or approved release-environment inputs are supplied.
- **D-07:** Verifier tests must prove that smoke labels, empty filegroups, generated dry-run placeholders, and local representative products cannot satisfy `REL-01`, `REL-02`, or `REL-03`.
- **D-08:** Generated Phase 20 runtime artifacts should live under `build/ci-evidence/phase20/`; checked-in source should define contracts, verifier logic, templates, target wiring, and regression tests only.

#### Signing, Provenance, and Comparison Metadata

- **D-09:** Keep the repo-native JSON contract and Python standard-library verifier as the authoritative evidence shape. Use attestation-style field names for subject digests, build input identity, builder command, run identity, key identity reference, and verification outcome, but do not introduce a new external attestation trust root in this phase.
- **D-10:** Signing evidence records public key identity or fingerprint, signing mode, artifact digest, build input identity, retention refs, timestamp, operator or release-run ID, and verification outcome. It must never record private keys, raw key bytes, private certificates, signing payload bytes, tokens, passwords, raw firmware payloads, or credential-bearing values.
- **D-11:** Provenance evidence should tie every retained artifact ref to the `//tools/bazel:phase17_release_candidate_artifacts` identity, build inputs, product/printer/board/MCU/bootloader metadata, source manifest refs, and artifact hashes.
- **D-12:** Comparison evidence should classify every archived-reference mismatch as exactly one of `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue`, with a reason, owner phase, affected artifact surface, and residual risk.

#### Aggregate and Final-Review Integration

- **D-13:** Phase 20 owns the release result manifest. Phase 19 may retain or index Phase 20 artifacts, and Phase 21 should consume Phase 20 result manifests as upstream release evidence before final readiness can pass.
- **D-14:** Do not make Phase 19 the authority for release pass/fail semantics. Aggregate CI can retain logs, snapshots, result manifests, and placeholders, but Phase 20's release result manifest remains the source of truth for release-candidate production status.
- **D-15:** Update wiring only as needed for discoverability and retention: Bazel labels, root aliases/docs filegroups, `tools/bazel/rust_workflow.sh`, `just phase20-verify`, and any Phase 19 index hook should point at Phase 20 artifacts without converting pending external release proof into a pass claim.
- **D-16:** Leave final readiness policy to Phase 21. Phase 20 should produce machine-readable release evidence that Phase 21 can validate, including passed, pending, blocked, failed, rejected-redaction, and rejected-overclaim states.

### the agent's Discretion

- Exact file names, schema field order, status spelling, target/macro names, generated artifact names, and helper boundaries are flexible if the result is deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated plan if the change remains cohesive. Split only if release identity, verifier, and integration work become too large for one clean execution pass.
- Prefer small JSON manifests, standard-library Python, targeted Bazel wiring, and focused unit tests over broad release automation rewrites.

### Deferred Ideas (OUT OF SCOPE)

- Full native Rust/Bazel release package graph can be expanded after this phase if the pragmatic Phase 20 path uses wrapped current release tooling or explicit release-environment inputs.
- External attestation tooling, SBOM export, and supply-chain policy engines can be added later if release governance requires them; Phase 20 should not add a new trust root unless the local evidence contract needs it.
- Final reference-demotion policy remains Phase 21 scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-01 | Release manager can build release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, and auxiliary firmware artifacts through Bazel-owned workflows. [VERIFIED: .planning/REQUIREMENTS.md] | Replace the empty `//tools/bazel:phase17_release_candidate_artifacts` target with a non-empty identity that points to real release outputs or explicit release-environment input manifests, while keeping `phase17_representative_release_smoke` separate. [VERIFIED: tools/bazel/BUILD.bazel; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| REL-02 | Release manager can verify release-candidate signing, provenance, build input identity, and artifact retention while keeping private signing keys outside the repository and planning artifacts. [VERIFIED: .planning/REQUIREMENTS.md] | Extend the Phase 17 evidence schema into a Phase 20 release result manifest with key identity refs, subject digests, build input identity, retention refs, timestamps, and verification outcomes, plus redaction guards. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| REL-03 | Maintainer can compare release-candidate artifact surfaces against the archived v1.0 reference evidence and classify every mismatch as pass, intentional delta, blocker, or deferred retained-code issue. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 17 and Phase 11 comparison vocabulary, require every mismatch row to have exactly one allowed class, and include owner phase, affected artifact surface, reason, and residual risk in the generated comparison report. [VERIFIED: tools/bazel/manifests/phase17_release_candidate_evidence_contract.json; tools/bazel/manifests/phase11_reference_comparisons.json] |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Planning and implementation must follow `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant managed standards pages before work continues. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md; standards/index.md]
- No active local Bright Builds override exists; the placeholder row in `standards-overrides.md` is not a real exception. [VERIFIED: standards-overrides.md]
- New verifier logic should keep pure decision checks separate from filesystem, subprocess, and clock effects. [VERIFIED: standards/core/architecture.md]
- New code should prefer early returns, visible `maybe_` names for optional internal values where practical, and split large mixed-responsibility functions/files. [VERIFIED: standards/core/code-shape.md]
- Pure verifier/business rules must have focused unit tests with clear Arrange, Act, Assert structure when non-trivial. [VERIFIED: standards/core/testing.md]
- Verification should prefer repo-owned entrypoints such as Bazel labels and `just` recipes, with relevant checks run before commit. [VERIFIED: standards/core/verification.md; justfile]
- Repo-local workflow enforcement says file-changing work should happen through GSD workflow artifacts unless the user explicitly bypasses it. [VERIFIED: AGENTS.md]
- Project skill directories `.claude/skills/` and `.agents/skills/` do not contain project `SKILL.md` files, so no repo-local skill alters Phase 20 planning. [VERIFIED: find .claude/skills .agents/skills -maxdepth 2 -name SKILL.md]

## Summary

Phase 20 is a closure phase for a known audit gap: Phase 17 created a release-candidate evidence contract but left `//tools/bazel:phase17_release_candidate_artifacts` as an empty filegroup, so no real release identity flows toward final review. [VERIFIED: .planning/v1.1-MILESTONE-AUDIT.md; tools/bazel/BUILD.bazel; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md] The correct plan is not to promote representative smoke fixtures; it is to add a Phase 20-owned release identity contract, a standard-library Python verifier, and a generated release result manifest under `build/ci-evidence/phase20/`. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

The recommended implementation is a hybrid release identity. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] Bazel should own the public identity target and any source-backed metadata/template artifacts that can be produced locally, while private signing and release-only build outputs remain explicit release-environment inputs referenced by safe metadata, hashes, and retention refs. [VERIFIED: ProjectOptions.cmake; utils/pack_fw.py; tools/bazel/phase17_release_candidate_evidence.py]

Phase 20 should keep authority local to the Phase 20 release result manifest and avoid moving release pass/fail semantics into Phase 19 aggregate CI or Phase 21 final readiness. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase19_aggregate_ci_evidence.py] Phase 19 can retain or index Phase 20 outputs, and Phase 21 should consume them later, but neither should reinterpret smoke outputs as production release evidence. [VERIFIED: .planning/phases/19-aggregate-cutover-evidence-ci/19-CONTEXT.md; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

**Primary recommendation:** Add a Phase 20 contract/verifier/test suite and Bazel/just wiring that makes `//tools/bazel:phase17_release_candidate_artifacts` non-empty through production-safe release input manifests, validates supplied release-run evidence, writes `build/ci-evidence/phase20/release-result-manifest.json`, and rejects empty, smoke, placeholder-only, redaction-failed, and overclaiming evidence. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase19_aggregate_ci_evidence.py]

## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Python standard library (`argparse`, `json`, `hashlib`, `re`, `shutil`, `datetime`, `pathlib`, `unittest`, `subprocess`) | Repo requires Python 3.8+; local probe found Python 3.14.4. [VERIFIED: README.md; python3 --version] | Contract validation, release evidence input parsing, redacted artifact writing, result manifest generation, and unit tests. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase19_aggregate_ci_evidence.py] | Phase 20 context explicitly prefers repo-native JSON contracts and Python standard-library verifier logic. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| Bazel `filegroup`, `genrule`, and repo `shell_binary` wrappers | Local probe found Bazel 9.1.1. [VERIFIED: bazel --version] | Own the public `//tools/bazel:phase17_release_candidate_artifacts` identity and expose `phase20_verify` / `phase20_verify_tests`. [VERIFIED: tools/bazel/BUILD.bazel; tools/bazel/shell_rules.bzl] | The project is Bazel-primary and prior phase verifiers use Bazel labels as stable workflow identities. [VERIFIED: .planning/PROJECT.md; tools/bazel/BUILD.bazel] |
| `just` facade | Local probe found just 1.48.0. [VERIFIED: just --version] | Add `just phase20-verify` so users run tests before the verifier through a stable command. [VERIFIED: justfile; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | The project requires discoverable `justfile` wrappers for common workflows. [VERIFIED: AGENTS.md; .planning/PROJECT.md] |
| Existing release artifact helpers | Repo-local. [VERIFIED: tools/bazel/artifact_rules.bzl; tools/bazel/artifact_packager.py; tools/bazel/artifact_manifest.py; tools/bazel/artifact_metadata_compare.py] | Preserve representative artifact metadata, hashes, BBF/DFU reference-boundary checks, and comparison helper patterns. [VERIFIED: tools/bazel/artifact_packager.py; tools/bazel/artifact_metadata_compare.py] | Phase 17 explicitly built on these helpers, and Phase 20 should not replace them while closing the empty-target gap. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |

### Supporting

| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| `utils/build.py` | Repo-local; requires Python `requests` before bootstrap/build. [VERIFIED: README.md; requirements.txt; python3 -c 'import requests'] | Reference firmware build wrapper and artifact staging to `build/products`. [VERIFIED: utils/build.py; README.md] | Use as release-environment source identity or wrapped command metadata; do not require it for local Phase 20 quick verification when dependencies are missing. [VERIFIED: environment probe; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| `utils/pack_fw.py` | Repo-local; Python `ecdsa` missing locally. [VERIFIED: utils/pack_fw.py; python3 -c 'import ecdsa'] | Reference BBF packaging and signing-sensitive behavior. [VERIFIED: utils/pack_fw.py; CMakeLists.txt] | Use only through approved release-run evidence or existing helper boundaries; never store private key material in repo artifacts. [VERIFIED: ProjectOptions.cmake; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| `utils/dfu.py` | Repo-local. [VERIFIED: utils/dfu.py] | DFU creation and structural format reference. [VERIFIED: utils/dfu.py; CMakeLists.txt] | Use for release-run command provenance or local structural helper references, not as proof that production release evidence exists. [VERIFIED: tools/bazel/artifact_packager.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| `jq` | Local probe found jq 1.7.1. [VERIFIED: jq --version] | Developer inspection of JSON manifests during planning and debugging. [VERIFIED: jq commands in research] | Useful but not required by the committed verifier; keep verifier stdlib-only. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Phase 20 JSON contract plus stdlib verifier | New external attestation/SBOM/trust-root tooling | Deferred by the Phase 20 context; adding a new trust root would broaden release governance beyond the gap closure. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| Explicit release-environment input manifests | Wrapping representative smoke artifacts in `phase17_release_candidate_artifacts` | The Phase 17 verifier already rejects smoke dependencies, and Phase 20 decisions require smoke fixtures to stay separate. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| Phase 20 as release authority | Phase 19 aggregate CI as release authority | Phase 20 decisions assign release pass/fail semantics to the Phase 20 release result manifest; Phase 19 may retain or index but must not decide release readiness. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase19_aggregate_ci_evidence.py] |

**Installation:**

```bash
# No new runtime package should be required for local Phase 20 verifier logic.
# Full release artifact production requires the repo bootstrap/release environment.
python3 utils/bootstrap.py
```

The local Phase 20 verifier should remain stdlib-only; full release output production depends on release-environment prerequisites such as Python packages, ARM toolchain, and signing key access. [VERIFIED: requirements.txt; environment probe; ProjectOptions.cmake]

**Version verification:** No npm package version check applies because Phase 20 should use Python stdlib plus repo-local tools. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase20_release_candidate_artifacts.py              # Phase 20 verifier/result writer [VERIFIED: Phase 17/19 script pattern]
├── phase20_release_candidate_artifacts_test.py         # stdlib unittest regression tests [VERIFIED: Phase 17/19 test pattern]
└── manifests/
    ├── phase20_release_candidate_artifacts_contract.json       # release identity/result contract [VERIFIED: Phase 17/19 manifest pattern]
    └── phase20_release_environment_inputs.template.json        # explicit release input template included by release identity [VERIFIED: Phase 20 D-02/D-08]

build/ci-evidence/phase20/
├── release-result-manifest.json                         # Phase 20 source of truth [VERIFIED: Phase 20 D-13/D-16]
├── normalized-release-results.json                      # row-level REL statuses [VERIFIED: Phase 17 generated output pattern]
├── redacted-signing-provenance-summary.json             # key identity/digest only [VERIFIED: Phase 20 D-10]
├── comparison-classification-report.json                # pass/intentional-delta/blocker/deferred rows [VERIFIED: Phase 20 D-12]
├── release-environment-input-template.json              # generated operator template [VERIFIED: Phase 20 D-08]
├── target-source-snapshot.json                          # resolved release identity target inventory [VERIFIED: Phase 20 D-01/D-05]
└── logs/
```

### Pattern 1: Hybrid Release Identity Target

**What:** Keep the public target name `//tools/bazel:phase17_release_candidate_artifacts`, but make it non-empty with production-safe release input artifacts or generated metadata outputs instead of local smoke outputs. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/BUILD.bazel]

**When to use:** Use this because the audit gap is specifically the empty Phase 17 artifact identity target. [VERIFIED: .planning/v1.1-MILESTONE-AUDIT.md]

**Example:**

```python
filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = [
        ":phase20_release_environment_input_manifest",
    ],
)
```

The actual label and helper names are discretionary, but the target must not include `:representative_release_artifacts`, `:phase17_representative_release_smoke`, or other local smoke labels. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

### Pattern 2: Phase 20 Release Result Manifest as Source of Truth

**What:** A generated `release-result-manifest.json` should report each REL row with proof class, status, artifact refs, digest, build input identity, signing key identity ref, retention refs, comparison class, verification outcome, and residual risk. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

**When to use:** Use for all Phase 20 pass/pending/blocked/failed/rejected states so Phase 21 can consume machine-readable upstream release evidence later. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; .planning/ROADMAP.md]

**Example:**

```json
{
  "id": "rel-bbf-firmware-package",
  "requirement_ids": ["REL-01", "REL-02", "REL-03"],
  "proof_class": "approved-release-run",
  "status": "pending-release-input",
  "bazel_label": "//tools/bazel:phase17_release_candidate_artifacts",
  "artifact_refs": [],
  "subject_digests": [],
  "build_input_identity": "",
  "key_identity_ref": "",
  "retention_refs": [],
  "verification_outcome": "pending-release-input"
}
```

This follows the Phase 17 row/result pattern while moving Phase 20 authority to `build/ci-evidence/phase20`. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

### Pattern 3: Proof Classes Prevent Overclaiming

**What:** Model proof class separately from status with values such as `release-candidate`, `approved-release-run`, `external-release-key-evidence`, `local-smoke`, and `placeholder`. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

**When to use:** Use proof classes when validating release evidence inputs, target contents, and result rows. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

**Planning implication:** A `passed` status should require an approved proof class plus complete metadata; `local-smoke`, `placeholder`, empty target, generated dry-run, and redaction-failed rows must never pass REL-01, REL-02, or REL-03. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase17_release_candidate_evidence_test.py]

### Pattern 4: Reuse Phase 17 Source and Security Guards

**What:** Reuse the Phase 17 source-ref, release evidence, forbidden field, forbidden text, overclaim, path, and smoke-target rejection concepts. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py]

**When to use:** Use for Phase 20 contract validation, release evidence input parsing, target source inventory, generated artifact scans, and regression tests. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

**Planning implication:** Update Phase 17 wiring tests if they currently fixture an empty target, because Phase 20 changes the expected release identity from intentionally empty to non-empty and production-safe. [VERIFIED: tools/bazel/phase17_release_candidate_evidence_test.py; .planning/v1.1-MILESTONE-AUDIT.md]

### Anti-Patterns to Avoid

- **Wrapping smoke artifacts:** `phase17_release_candidate_artifacts` must not depend on `:representative_release_artifacts`, `:phase17_representative_release_smoke`, or `//tools/bazel:phase3_verify`. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
- **Empty target remains acceptable:** Phase 20 should add tests that fail if `phase17_release_candidate_artifacts` has no production-safe `srcs`. [VERIFIED: .planning/v1.1-MILESTONE-AUDIT.md; tools/bazel/BUILD.bazel]
- **Placeholder-only pass:** Generated input templates or dry-run placeholders may be retained, but they cannot satisfy production release evidence rows. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
- **Raw payload or key retention:** Evidence should retain digests, key identity refs, metadata, and external refs, not private keys or raw firmware package bytes. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; ProjectOptions.cmake; utils/pack_fw.py]
- **Phase 19 semantic drift:** Do not make Phase 19 decide release pass/fail while adding retention/indexing hooks. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase19_aggregate_ci_evidence.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Release signing | A new signing implementation, committed private key, or fixture key promotion | Existing release signing path represented by `SIGNING_KEY` metadata, `utils/pack_fw.py`, and external release key identity refs [VERIFIED: ProjectOptions.cmake; utils/pack_fw.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | Private keys and payload bytes are explicitly forbidden in repo/planning artifacts. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| BBF/DFU packaging semantics | New local encoders | `utils/pack_fw.py`, `utils/dfu.py`, and existing artifact helper metadata boundaries [VERIFIED: utils/pack_fw.py; utils/dfu.py; tools/bazel/artifact_packager.py] | Existing helpers already encode reference-format and bootstrap-required boundaries. [VERIFIED: tools/bazel/artifact_packager.py] |
| Release comparison taxonomy | New mismatch vocabulary | Existing Phase 17/Phase 11 classes: `pass`, `intentional-delta`, `blocker`, `deferred-retained-code-issue` [VERIFIED: tools/bazel/manifests/phase17_release_candidate_evidence_contract.json; tools/bazel/manifests/phase11_reference_comparisons.json] | REL-03 requires every mismatch to use this exact classification family. [VERIFIED: .planning/REQUIREMENTS.md; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| CI artifact authority | Phase 19 release decision logic | Phase 20 release result manifest, with Phase 19 retaining/indexing only if needed [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | Phase 19 currently retains external placeholders and local quick artifacts, but does not own release semantics. [VERIFIED: tools/bazel/phase19_aggregate_ci_evidence.py] |
| Secret scanning | A prose review checklist only | Regex/field-name/phrase guards in the Phase 20 verifier plus tests [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase17_release_candidate_evidence_test.py] | Prior phases already enforce redaction and overclaim checks mechanically. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase19_aggregate_ci_evidence.py] |

**Key insight:** The high-risk work is not generating bytes locally; it is making the release identity target non-empty without letting smoke, placeholder, or secret-bearing evidence masquerade as production proof. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; .planning/v1.1-MILESTONE-AUDIT.md]

## Common Pitfalls

### Pitfall 1: Non-Empty Target Still Points to Smoke

**What goes wrong:** The empty filegroup is replaced with `:representative_release_artifacts` or `:phase17_representative_release_smoke`. [VERIFIED: tools/bazel/BUILD.bazel; tools/bazel/phase17_release_candidate_evidence.py]
**Why it happens:** Representative artifacts are already wired and buildable, so they are an easy but incorrect dependency. [VERIFIED: justfile; tools/bazel/manifests/representative_products.json]
**How to avoid:** Require target sources to be real release outputs or explicit release-environment input manifests with allowed proof classes, and keep smoke labels in a separate allowlist/rejectlist. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Warning signs:** `phase17_release_candidate_artifacts` contains `representative`, `smoke`, or `phase3_verify` labels. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py]

### Pitfall 2: Local Quick Mode Marks REL Rows Passed

**What goes wrong:** `phase20-verify` produces a green local run and marks release rows `passed` without supplied release artifacts or approved release input. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Why it happens:** Existing Phase 17 quick output can validate contract and source rows but leaves production rows pending by design. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md]
**How to avoid:** Make `release_inputs_supplied` and proof class explicit, and reject `passed` for placeholder, local-smoke, generated dry-run, or missing release input rows. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Warning signs:** A generated Phase 20 result manifest contains `passed` while artifact refs, subject digests, build input identity, key identity, retention refs, or verification outcome are empty. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

### Pitfall 3: Signing Evidence Leaks Secret Material

**What goes wrong:** Release evidence includes `private_key`, `signing_key_value`, raw key bytes, private certificates, tokens, passwords, or raw firmware payload fields. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Why it happens:** The reference packaging path has a `SIGNING_KEY` cache path and `utils/pack_fw.py` can read a PEM key when not using `--no-sign`. [VERIFIED: ProjectOptions.cmake; utils/pack_fw.py]
**How to avoid:** Record public key identity/fingerprint, signing mode, artifact digest, build input identity, retention refs, timestamp, operator/release run ID, and verification outcome only. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Warning signs:** Security scan finds private-key blocks, credential assignments, certificate private material, or raw payload marker names. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py]

### Pitfall 4: Comparison Report Omits a Surface

**What goes wrong:** `.bin`, `.bbf`, `.dfu`, resource, language, WUI, ESP, MMU, Dwarf, ModularBed, xBuddy Extension, package manifest, signing, provenance, retention, or comparison rows are missing. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/manifests/phase17_release_candidate_evidence_contract.json]
**Why it happens:** The representative product matrix is narrower than the full release-candidate surface. [VERIFIED: tools/bazel/manifests/representative_products.json; tools/bazel/manifests/phase17_release_candidate_evidence_contract.json]
**How to avoid:** Keep required surface constants in the Phase 20 verifier and test removals one surface at a time. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase17_release_candidate_evidence_test.py]
**Warning signs:** No source refs to Phase 7 generated outputs or Phase 10 auxiliary build/update rows appear in the Phase 20 contract. [VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json; tools/bazel/manifests/phase10_auxiliary_build_update.json]

### Pitfall 5: Phase 19 Accidentally Becomes Release Authority

**What goes wrong:** Aggregate CI retention status is interpreted as release-candidate pass/fail. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Why it happens:** Phase 19 already copies Phase 17 quick artifacts and external placeholders into an aggregate bundle. [VERIFIED: tools/bazel/phase19_aggregate_ci_evidence.py; tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json]
**How to avoid:** If Phase 19 is updated, limit it to retaining/indexing Phase 20 artifacts and keep Phase 20's `release-result-manifest.json` as the authoritative release status source. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
**Warning signs:** Phase 19 contract gains REL-01/REL-02/REL-03 pass/fail semantics instead of evidence retention rows. [VERIFIED: tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

## Code Examples

### Release Evidence Input Row

```json
{
  "release_run_id": "rc-2026-06-21-001",
  "proof_class": "approved-release-run",
  "artifact_surface": ".bbf",
  "product_profile": "all-supported-release-products",
  "builder_command": "bazel build //tools/bazel:phase17_release_candidate_artifacts",
  "build_input_identity": "git:<commit>; bazel:<workspace-status>",
  "subject_digests": [
    {"artifact_ref": "external://phase20/artifacts/coreone/firmware.bbf", "sha256": "<64 lowercase hex>"}
  ],
  "key_identity_ref": "release-key-fingerprint:sha256:<fingerprint>",
  "retention_refs": ["external://phase20/retention/rc-2026-06-21-001"],
  "verification_outcome": "approved-release-metadata",
  "mismatch_class": "pass",
  "mismatch_reason": "Release metadata matched archived reference classification.",
  "owner_phase": "20-release-candidate-artifact-production",
  "residual_risk": "Limited to supplied release-environment evidence."
}
```

This extends the Phase 17 release evidence fields with Phase 20 proof-class and subject-digest naming while preserving the same redaction boundary. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

### Proof Class Guard

```python
def require_pass_allowed(row: dict[str, object], row_name: str) -> None:
    status = require_string(row, "status", row_name)
    proof_class = require_string(row, "proof_class", row_name)
    if status != "passed":
        return
    if proof_class not in {"approved-release-run", "external-release-key-evidence", "release-candidate"}:
        raise VerificationError(f"{row_name} cannot pass with proof_class={proof_class!r}")
```

This is the Phase 20-specific version of the Phase 17 rule that `passed` release evidence must use approved evidence type and the real release identity label. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

### Tests-Before-Verifier Facade

```make
phase20-verify:
    bazel run //tools/bazel:phase20_verify_tests
    bazel run //tools/bazel:phase20_verify
```

This follows the existing Phase 17 and Phase 19 `justfile` pattern. [VERIFIED: justfile]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 17 created an honest empty `phase17_release_candidate_artifacts` target to avoid overclaiming release proof. [VERIFIED: tools/bazel/BUILD.bazel; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md] | Phase 20 should replace it with a non-empty hybrid release identity that resolves to production-safe outputs or explicit release-environment input artifacts. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | Phase 20 context gathered 2026-06-21. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | Planner must change Bazel wiring and tests without using smoke fixtures as proof. [VERIFIED: .planning/v1.1-MILESTONE-AUDIT.md] |
| Phase 17 quick evidence writes pending release rows under `build/ci-evidence/phase17`. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py] | Phase 20 should write a Phase 20 release result manifest under `build/ci-evidence/phase20` and make that manifest the release status source of truth. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | Phase 20 gap-closure scope. [VERIFIED: .planning/ROADMAP.md] | Phase 21 can later consume machine-readable Phase 20 outputs instead of prose. [VERIFIED: .planning/ROADMAP.md] |
| Phase 19 retains Phase 14-18 quick artifacts and external placeholders. [VERIFIED: tools/bazel/phase19_aggregate_ci_evidence.py; .planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md] | Phase 19 may index/retain Phase 20 artifacts, but Phase 20 remains the release authority. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | Phase 20 integration decision D-13/D-14. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | Planner should avoid broad Phase 19 semantic rewrites. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |

**Deprecated/outdated:**

- Treating `phase17_release_candidate_artifacts` as intentionally empty is now outdated for Phase 20 because the v1.1 audit explicitly identifies it as the REL-01 gap. [VERIFIED: .planning/v1.1-MILESTONE-AUDIT.md]
- Treating representative smoke artifacts as release proof remains forbidden. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

## Assumptions Log

All claims in this research were verified or cited in this session; no unverified claim tags are intentionally present. [VERIFIED: source audit performed in this session]

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| N/A | No assumed claims recorded. | N/A | N/A |

## Open Questions

1. **Which release-environment URI scheme and retention backend will release managers use?**
   - What we know: Phase 20 allows explicit release-environment input manifests and external refs without private payloads. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
   - What's unclear: The repo does not define the production artifact store, retention backend, or key-management naming scheme. [VERIFIED: rg release/signing refs; .planning/codebase/INTEGRATIONS.md]
   - Recommendation: Use `external://phase20/...` refs and require `retention_refs`, `subject_digests`, `key_identity_ref`, and `verification_outcome` fields; do not block local verification on the real backend. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

2. **Should Phase 19 retain Phase 20 outputs in this phase?**
   - What we know: Phase 20 decisions allow Phase 19 to retain or index Phase 20 artifacts, but forbid Phase 19 from owning release pass/fail semantics. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]
   - What's unclear: The roadmap success criteria for Phase 20 do not require a Phase 19 contract rewrite. [VERIFIED: .planning/ROADMAP.md]
   - Recommendation: Add only minimal discoverability/retention hooks if needed, such as docs aliases or an index row that points to `build/ci-evidence/phase20/release-result-manifest.json`; keep all REL status decisions in Phase 20. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 20 verifier/tests | yes | 3.14.4 [VERIFIED: python3 --version] | None for local verifier. |
| Bazel | Release identity target and verifier labels | yes | 9.1.1 [VERIFIED: bazel --version] | Direct `python3` verifier commands for debugging only; planner should still wire Bazel labels. [VERIFIED: tools/bazel/BUILD.bazel] |
| just | Developer facade | yes | 1.48.0 [VERIFIED: just --version] | Direct `bazel run` commands. [VERIFIED: justfile] |
| jq | Research/debugging JSON inspection | yes | 1.7.1 [VERIFIED: jq --version] | Not required by committed verifier. [VERIFIED: Phase 20 context prefers stdlib Python] |
| Git | Build input/provenance identity | yes | 2.53.0 [VERIFIED: git --version] | Release input can carry supplied build identity if local git metadata is unavailable. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| pre-commit | Repo hook checks | no | Missing on PATH [VERIFIED: command -v pre-commit] | Run targeted Python/Bazel/just checks; do not claim pre-commit was run. [VERIFIED: .pre-commit-config.yaml; standards/core/verification.md] |
| Python `requests` | `utils/build.py` bootstrap/build prerequisites | no | ModuleNotFoundError [VERIFIED: python3 -c 'import requests'] | Release environment or bootstrap must provide it for full builds. [VERIFIED: README.md; requirements.txt] |
| Python `ecdsa` | `utils/pack_fw.py` signed BBF path | no | ModuleNotFoundError [VERIFIED: python3 -c 'import ecdsa'] | Use explicit release-environment signing evidence locally; bootstrap/release env supplies package for real signing. [VERIFIED: requirements.txt; utils/pack_fw.py] |
| CMake | Reference firmware build | yes | 3.27.9 on PATH; repo bootstrap pins 3.28.3. [VERIFIED: cmake --version; AGENTS.md stack] | Release environment/bootstrap provides pinned CMake if needed. [VERIFIED: utils/bootstrap.py via AGENTS.md stack] |
| Ninja | Reference firmware build | yes | 1.13.2 on PATH; repo bootstrap pins 1.10.2. [VERIFIED: ninja --version; AGENTS.md stack] | Release environment/bootstrap provides pinned Ninja if needed. [VERIFIED: utils/bootstrap.py via AGENTS.md stack] |
| ARM `arm-none-eabi-gcc` | Full embedded firmware release build and resource conversion | no | Missing on PATH and `.dependencies/gcc-arm-none-eabi-13.2.1` absent. [VERIFIED: environment probe; ls .dependencies] | Release environment/bootstrap must provide it; Phase 20 local verifier should accept explicit release inputs. [VERIFIED: AGENTS.md stack; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| Private release signing key | Production signing proof | no by design | Not probed for secret safety. [VERIFIED: ProjectOptions.cmake; .planning/REQUIREMENTS.md] | Use key identity/fingerprint metadata and external release signing evidence only. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |

**Missing dependencies with no fallback:**

- Real production signing and full release artifact byte production are not locally available without a prepared release environment, pinned dependencies, and private signing access. [VERIFIED: environment probe; ProjectOptions.cmake; utils/pack_fw.py]

**Missing dependencies with fallback:**

- Local deterministic Phase 20 validation can proceed with Python stdlib, Bazel, and just by validating contracts, target wiring, templates, release input schemas, path guards, redaction guards, and no-overclaim semantics. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase17_release_candidate_evidence.py]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` plus Bazel `shell_binary` wrappers. [VERIFIED: tools/bazel/phase17_release_candidate_evidence_test.py; tools/bazel/phase19_aggregate_ci_evidence_test.py] |
| Config file | None for stdlib unittest; `pyproject.toml` configures pytest integration tests only. [VERIFIED: pyproject.toml] |
| Quick run command | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py && python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` after implementation. [VERIFIED: Phase 17/19 command pattern] |
| Full suite command | `just phase20-verify` after implementation. [VERIFIED: justfile pattern; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| REL-01 | `//tools/bazel:phase17_release_candidate_artifacts` is non-empty and resolves only to production-safe release outputs or explicit release-environment input manifests, never smoke labels. [VERIFIED: .planning/ROADMAP.md; tools/bazel/BUILD.bazel] | unit/wiring | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` | No - Wave 0 |
| REL-01 | Contract covers `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, Dwarf, ModularBed, xBuddy Extension, package manifest, signing summary, provenance summary, retention manifest, and comparison report. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | unit/contract | `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` | No - Wave 0 |
| REL-02 | Signing/provenance evidence requires key identity, build input identity, subject digests, retention refs, timestamps, operator/release-run ID, and verification outcome while rejecting private key/payload/credential markers. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | unit/security | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` | No - Wave 0 |
| REL-03 | Comparison report classifies every archived-reference mismatch as `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue` with reason, owner phase, affected surface, and residual risk. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] | unit/contract | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` | No - Wave 0 |
| REL-01/02/03 | Bazel labels, root aliases/docs filegroups, `rust_workflow.sh`, and `just phase20-verify` run tests before verifier. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; justfile] | integration/wiring | `just phase20-verify` | No - Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` plus direct `--contract-only`, `--security-only`, `--wiring-only`, and `--quick` modes. [VERIFIED: Phase 17/19 verifier mode pattern]
- **Per wave merge:** `bazel run //tools/bazel:phase20_verify_tests && bazel run //tools/bazel:phase20_verify`. [VERIFIED: tools/bazel/BUILD.bazel existing phase pattern]
- **Phase gate:** `just phase20-verify`, `bazel query "//tools/bazel:phase17_release_candidate_artifacts + //:phase17_release_candidate_artifacts"`, and `git diff --check`. [VERIFIED: Phase 17 verification command pattern; justfile]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` - Phase 20 contract for release identity, proof classes, result manifest, signing/provenance, retention, and comparison rows. [VERIFIED: file does not exist via find/rg]
- [ ] `tools/bazel/manifests/phase20_release_environment_inputs.template.json` - explicit source-backed release-environment input template included in the release identity target. [VERIFIED: Phase 20 D-02/D-08]
- [ ] `tools/bazel/phase20_release_candidate_artifacts.py` - stdlib verifier/result writer. [VERIFIED: file does not exist via find/rg]
- [ ] `tools/bazel/phase20_release_candidate_artifacts_test.py` - regression tests for empty target, smoke target, placeholder, redaction, proof class, and comparison classification rejection. [VERIFIED: file does not exist via find/rg]
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 20 labels, aliases, docs filegroup, dispatch, and facade. [VERIFIED: rg phase20 in wiring files]
- [ ] Phase 17 verifier/test fixtures may need updates so Phase 17 still rejects smoke labels but no longer treats an empty release target as acceptable after Phase 20. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase17_release_candidate_evidence_test.py]

## Security Domain

Security enforcement is enabled for this research because `.planning/config.json` does not set `security_enforcement: false`. [VERIFIED: .planning/config.json; researcher instructions] OWASP ASVS latest stable version is 5.0.0, and OWASP recommends versioned requirement references because identifiers can change. [CITED: https://owasp.org/www-project-application-security-verification-standard/] The ASVS 5.0 index includes V1 Encoding and Sanitization, V2 Validation and Business Logic, V5 File Handling, V8 Authorization, V11 Cryptography, V13 Configuration/Secret Management, V14 Data Protection, V15 Secure Coding and Architecture, and V16 Security Logging/Error Handling categories that map to this phase. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V1 Encoding and Sanitization | Yes | Avoid command-injection-prone shell strings; keep subprocess calls list-based where needed and keep verifier logic stdlib Python. [CITED: https://owasp.org/www-project-application-security-verification-standard/; VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| V2 Validation and Business Logic | Yes | Parse JSON evidence at boundaries, enforce required fields/enums/proof classes, and make illegal pass states unrepresentable in verifier logic. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase17_release_candidate_evidence.py] |
| V5 File Handling | Yes | Restrict generated artifacts to `build/ci-evidence/phase20/`, reject absolute paths and traversal, and allow only explicit external release refs. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| V8 Authorization | Yes at process-boundary level | Allow `passed` release status only for approved release evidence/proof classes; reject local smoke and placeholders. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| V11 Cryptography | Yes | Do not implement new signing; record key identity/fingerprint, signing mode, subject digests, and verification outcome without private key material. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: ProjectOptions.cmake; utils/pack_fw.py] |
| V13 Configuration / Secret Management | Yes | Treat signing keys and CI/release credentials as external secrets and reject secret-bearing fields or values in evidence. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| V14 Data Protection | Yes | Redact or reject tokens, passwords, private certificates, raw key bytes, raw payload bytes, crash dumps, and firmware package payload text. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase17_release_candidate_evidence.py] |
| V15 Secure Coding and Architecture | Yes | Keep pure validation separate from I/O, use focused unit tests, and avoid large mixed-responsibility verifier files when practical. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: standards/core/architecture.md; standards/core/code-shape.md] |
| V16 Security Logging and Error Handling | Yes | Write redacted logs and explicit failure reasons without leaking payloads or credentials. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase19_aggregate_ci_evidence.py] |

### Known Threat Patterns for Phase 20

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Smoke artifact promoted to release proof | Spoofing / Repudiation | Reject smoke labels and proof classes in `phase17_release_candidate_artifacts`; require production-safe release input manifests. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |
| Private key or payload leakage | Information Disclosure | Scan contracts, release evidence inputs, generated outputs, and logs for forbidden fields and text markers. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py] |
| Path traversal or output escape | Tampering / Information Disclosure | Require repo-relative paths under `build/ci-evidence/phase20/` or explicit `external://phase20/...` refs. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase19_aggregate_ci_evidence.py] |
| Placeholder or dry-run overclaim | Repudiation | Require proof class plus complete release metadata before `passed`; reject overclaim phrases. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase17_release_candidate_evidence.py] |
| Incomplete mismatch classification | Tampering / Process Integrity | Require exactly one allowed comparison class, reason, owner phase, affected artifact surface, and residual risk for every mismatch. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md` - locked Phase 20 decisions, discretion, deferred ideas, canonical refs, and code context. [VERIFIED: cat]
- `.planning/REQUIREMENTS.md` - REL-01, REL-02, REL-03 definitions. [VERIFIED: cat]
- `.planning/ROADMAP.md` - Phase 20 goal, dependencies, gap closure, and success criteria. [VERIFIED: cat]
- `.planning/v1.1-MILESTONE-AUDIT.md` - audit finding for the empty `phase17_release_candidate_artifacts` target. [VERIFIED: cat]
- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md` and `17-VERIFICATION.md` - existing release evidence contract boundary and empty-target limitation. [VERIFIED: cat]
- `.planning/phases/19-aggregate-cutover-evidence-ci/19-CONTEXT.md` and `19-VERIFICATION.md` - aggregate retention and no-overclaim boundary. [VERIFIED: cat]
- `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - current Bazel/just wiring and empty release identity. [VERIFIED: sed/rg]
- `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`, and `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - existing release evidence verifier, tests, schema, statuses, source refs, redaction guards, and smoke rejection. [VERIFIED: sed/jq/rg]
- `tools/bazel/phase19_aggregate_ci_evidence.py` and `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - aggregate retention/indexing pattern and Phase 17 pending release input placeholder. [VERIFIED: sed/jq/rg]
- `tools/bazel/artifact_rules.bzl`, `tools/bazel/artifact_packager.py`, `tools/bazel/artifact_manifest.py`, `tools/bazel/artifact_metadata_compare.py`, and `tools/bazel/manifests/representative_products.json` - existing representative artifact helper stack. [VERIFIED: sed/jq]
- `utils/build.py`, `utils/pack_fw.py`, `utils/dfu.py`, `CMakeLists.txt`, `ProjectOptions.cmake`, `README.md`, and `requirements.txt` - release build, signing, DFU, products, and dependency reference paths. [VERIFIED: sed/rg]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/testing.md`, `standards/core/verification.md`, and `standards/core/operability.md` - repo and standards constraints. [VERIFIED: cat]

### Secondary (MEDIUM confidence)

- Environment probes: `python3 --version`, `bazel --version`, `just --version`, `jq --version`, `git --version`, `cmake --version`, `ninja --version`, `command -v pre-commit`, Python `requests`/`ecdsa` imports, ARM GCC probes, and `.dependencies` listing. [VERIFIED: command outputs]
- OWASP ASVS project page - latest stable version and versioned-reference guidance. [CITED: https://owasp.org/www-project-application-security-verification-standard/]
- OWASP Cheat Sheet Series ASVS index - ASVS 5.0 category map used for security domain alignment. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Tertiary (LOW confidence)

- None. [VERIFIED: source hierarchy review]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - Phase 20 explicitly chooses repo-native JSON, Python stdlib, Bazel wiring, and just facade, and those patterns already exist in Phase 17/19. [VERIFIED: .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md; tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/phase19_aggregate_ci_evidence.py]
- Architecture: HIGH - The implementation shape is constrained by existing verifier/contract patterns and the specific empty-target audit gap. [VERIFIED: .planning/v1.1-MILESTONE-AUDIT.md; tools/bazel/BUILD.bazel]
- Pitfalls: HIGH - Smoke separation, redaction, path guards, pending external release inputs, and comparison taxonomy are already encoded in Phase 17. [VERIFIED: tools/bazel/phase17_release_candidate_evidence.py; tools/bazel/manifests/phase17_release_candidate_evidence_contract.json]
- Production release specifics: MEDIUM - The repo exposes signing/build entrypoints, but private key identity, artifact store, and release environment are intentionally external. [VERIFIED: ProjectOptions.cmake; utils/build.py; utils/pack_fw.py; .planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md]

**Research date:** 2026-06-21 [VERIFIED: environment_context]
**Valid until:** 2026-07-21 for local repo patterns; re-check before planning if release infrastructure, signing policy, Bazel version, or ASVS version changes. [VERIFIED: .planning/config.json; environment probe; CITED: https://owasp.org/www-project-application-security-verification-standard/]
