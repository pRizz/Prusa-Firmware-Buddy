# Phase 17: Release Candidate Artifact and Signing Gates - Research

**Researched:** 2026-06-19 [VERIFIED: current_date]
**Domain:** Bazel-owned release-candidate artifact evidence, signing/provenance gates, retained artifact references, and archived v1.0 comparison [VERIFIED: .planning/ROADMAP.md; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Confidence:** HIGH for local contract/verifier planning; MEDIUM for production release-run specifics because approved signing environment details are not present in the repo [VERIFIED: tools/bazel/phase16_live_network_evidence.py; ProjectOptions.cmake; environment probe]

<user_constraints>
## User Constraints (from CONTEXT.md)

The following constraints are copied from `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md`. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

### Locked Decisions

#### Release Artifact Matrix

- **D-01:** Add a Phase 17-owned release-candidate evidence contract instead of mutating Phase 11, Phase 13, Phase 15, or Phase 16 manifests. The contract should name each required artifact family with requirement mapping, proof scope, expected artifact path, retained artifact kind, and residual cutover gates.
- **D-02:** Use row-level release qualification, not one umbrella release pass. Rows should cover `.bin`, `.bbf`, `.dfu`, map/provenance, resource image/package, language bundles, WUI assets, ESP packages, MMU packages, Dwarf/ModularBed/xBuddy Extension auxiliary firmware, package manifests, and artifact comparison reports.
- **D-03:** Local deterministic checks may create representative smoke artifacts and dry-run summaries, but real release-candidate rows can pass only from supplied release-run evidence or approved release environment artifacts. Use statuses such as `pending-release-input`, `release-run-required`, `external-signing-required`, `blocked-signing-key-unavailable`, `source-contract-passed`, `passed`, and `failed`.
- **D-04:** Preserve Phase 3 representative artifact helpers where useful. Phase 17 should build on `artifact_packager.py`, `artifact_manifest.py`, `artifact_metadata_compare.py`, `representative_products.json`, and `phase3_artifacts.sh` instead of replacing reference-format BBF/DFU generation.

#### Signing and Provenance Hygiene

- **D-05:** Signing evidence records key identity, signing mode, command/source input identity, artifact digest, timestamp, retention path, and verification outcome. It must not include private signing keys, raw key bytes, certificates with private material, credential values, or signing payload bytes in source or planning artifacts.
- **D-06:** The evidence model should support external release-key evidence by name or fingerprint only. Local fixture/test-key evidence can validate schema and redaction behavior but cannot satisfy production signing proof.
- **D-07:** Provenance rows should verify build input identity, product/printer/board/MCU/bootloader metadata, package member names, source manifest references, and artifact hashes. They should avoid claiming byte-for-byte CMake release parity unless a real release comparison artifact is supplied.
- **D-08:** Verifier guards must reject committed or generated artifacts containing private key blocks, certificate private material, `signing_key_value`, firmware payload markers, raw `.bin`/`.bbf`/`.dfu` payload text, token/password markers, release readiness claims, signing proof overclaims, retained-code approval, or reference-demotion approval.

#### Reference Comparison and Mismatch Classification

- **D-09:** Every release-candidate comparison row should cite archived v1.0 reference evidence and classify mismatches as exactly one of `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue`.
- **D-10:** Comparison output should identify artifact surface, product/profile, reference source, Rust/Bazel surface, normalized fields compared, artifact refs, mismatch class, owner phase, and residual risk. Binary payload bytes and signing secrets remain excluded from checked-in evidence.
- **D-11:** Reference comparison should use and extend the Phase 11 reference comparison and cutover readiness taxonomy rather than inventing a separate release vocabulary.
- **D-12:** Release-candidate comparison can satisfy `REL-03` only when every required surface is represented and every mismatch has one of the allowed classifications with a reason and owner.

#### Artifact Retention and CI Integration

- **D-13:** Generated Phase 17 runtime artifacts should live under an ignored directory such as `build/ci-evidence/phase17`, following Phase 13 through Phase 16. Checked-in files define contracts, schema, verifier logic, redaction guards, and dry-run examples only.
- **D-14:** Generated outputs should include a machine-readable run manifest, normalized artifact results, redacted signing/provenance summary, comparison classification report, source contract snapshot, release operator input template, and log or external-artifact references.
- **D-15:** Phase 13's artifact-retention model remains the CI bridge. CI may retain Phase 17 generated summaries and manifest snapshots, but CI without release inputs or signing evidence must not become release proof.
- **D-16:** Artifact paths should be repo-relative under `build/ci-evidence/phase17` or explicit `external://phase17/...` references. Verifiers should reject path traversal and committed generated release artifacts.

#### Runner and Developer Workflow

- **D-17:** Add a dedicated standard-library Python release evidence verifier/collector, likely `tools/bazel/phase17_release_candidate_evidence.py`, with focused unit tests in `tools/bazel/phase17_release_candidate_evidence_test.py`.
- **D-18:** Expose Phase 17 through a checked-in contract manifest, Bazel `phase17_verify` / `phase17_verify_tests` labels, root docs/alias filegroups, `tools/bazel/rust_workflow.sh`, and `just phase17-verify`.
- **D-19:** Local phase verification should be deterministic: validate contract schema, required release rows, source refs, wiring, dry-run generated artifacts, redaction, path guards, mismatch classification, signing/provenance semantics, and overclaim guards without requiring private signing keys or full firmware builds.
- **D-20:** Keep orchestration thin and auditable: prefer JSON contracts, explicit status vocabularies, small Python helpers, `subprocess.run` without shell execution when external commands are needed, and focused stdlib tests over broad release automation rewrites.

#### Traceability and Prior Evidence

- **D-21:** Every Phase 17 row must map to `REL-01`, `REL-02`, and/or `REL-03` plus relevant archived v1.0 and Phase 11 evidence rows. Rows should cite Phase 3 artifact/generator evidence, Phase 7 resource evidence, Phase 10 auxiliary package evidence, Phase 13 CI retention, Phase 15 hardware boundaries, and Phase 16 live-service boundaries where applicable.
- **D-22:** Preserve Phase 15 and Phase 16 boundaries: hardware and live-service evidence may support readiness, but they do not satisfy release-candidate packaging, signing, provenance, or artifact comparison proof.
- **D-23:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 17-2026-06-19T13-57-17`.

### the agent's Discretion

- Exact scenario IDs, schema field order, status names, generated artifact file names, helper boundaries, and dry-run output shape are flexible if the result remains deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated implementation plan or several tasks inside one plan, but the roadmap expects one completed plan for this phase.
- Prefer contract-backed evidence and verifier tests over prose-only release checklists. Operator-facing release instructions are useful only when backed by machine-readable artifacts and verifier checks.

### Deferred Ideas (OUT OF SCOPE)

- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
- Real production release approval, post-cutover release dashboards, broader artifact analytics, and vendor/HAL replacement belong to future milestones after the Phase 17 evidence contract exists and maintainers accept release-run inputs.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-01 | Release manager can build release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, and auxiliary firmware artifacts through Bazel-owned workflows. [VERIFIED: .planning/REQUIREMENTS.md] | Use a row-level Phase 17 contract over the existing representative artifact labels, Phase 3 helpers, Phase 7 generated-output/resource rows, and Phase 10 auxiliary/MMU resource rows. [VERIFIED: tools/bazel/manifests/representative_products.json; tools/bazel/artifact_rules.bzl; tools/bazel/manifests/phase7_generated_outputs.json; tools/bazel/manifests/phase10_auxiliary_build_update.json] |
| REL-02 | Release manager can verify release-candidate signing, provenance, build input identity, and artifact retention while keeping private signing keys outside the repository and planning artifacts. [VERIFIED: .planning/REQUIREMENTS.md] | Use release evidence rows that accept external release-key identity by name/fingerprint and artifact digests only, plus redaction/path/overclaim scans copied from Phase 13/15/16 patterns. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase13_ci_evidence.py; tools/bazel/phase16_live_network_evidence.py; ProjectOptions.cmake; utils/pack_fw.py] |
| REL-03 | Maintainer can compare release-candidate artifact surfaces against archived v1.0 reference evidence and classify every mismatch as pass, intentional delta, blocker, or deferred retained-code issue. [VERIFIED: .planning/REQUIREMENTS.md] | Extend Phase 11 comparison/cutover vocabulary and require every Phase 17 comparison row to cite source refs, normalized fields, mismatch class, owner phase, and residual risk. [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; tools/bazel/manifests/phase11_cutover_readiness.json; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Planning and implementation must follow repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the relevant standards pages before work continues. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md]
- Bright Builds has no active local override in `standards-overrides.md`; the placeholder table is not an exception. [VERIFIED: standards-overrides.md]
- New logic should keep business decisions in a functional core and put I/O, filesystem, subprocess, clock, and environment effects in a thin imperative shell. [VERIFIED: standards/core/architecture.md]
- New verifier code should use early returns/guards, visible `maybe_` names for optional internal values when practical, and avoid large mixed-responsibility functions/files. [VERIFIED: standards/core/code-shape.md]
- Pure verifier/business logic must have focused unit tests, and non-trivial tests should clearly separate Arrange, Act, and Assert. [VERIFIED: standards/core/testing.md]
- Verification should prefer repo-owned entrypoints and run relevant checks before committing; Phase 17 should add tests-before-verifier Bazel and `just` wiring like Phases 13 through 16. [VERIFIED: standards/core/verification.md; justfile; tools/bazel/rust_workflow.sh]
- Python files should use repo-local snake_case naming and avoid swallowing errors; shell entrypoints should use `#!/usr/bin/env bash` and `set -euo pipefail`. [VERIFIED: AGENTS.md; tools/bazel/phase3_artifacts.sh; tools/bazel/rust_workflow.sh]
- Project-local skill directories `.claude/skills/` and `.agents/skills/` do not contain `SKILL.md` files, so no project skills alter this research. [VERIFIED: find . -maxdepth 4 -path './.claude/skills/*/SKILL.md'; find . -maxdepth 4 -path './.agents/skills/*/SKILL.md]

## Summary

Phase 17 should be planned as a contract-backed release evidence gate, not as a local production release builder. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] The contract should enumerate release artifact families row by row, write deterministic local/dry-run outputs under `build/ci-evidence/phase17`, and keep production pass status dependent on supplied release-run evidence or approved release-environment artifact refs. [VERIFIED: tools/bazel/manifests/phase16_live_network_evidence_contract.json; tools/bazel/phase16_live_network_evidence.py; .gitignore]

The strongest implementation pattern is the Phase 16 evidence runner with Phase 13 retention semantics and Phase 3 artifact helpers. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase13_ci_evidence.py; tools/bazel/artifact_packager.py] Phase 17 should add `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json`, `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`, Bazel shell labels, root aliases/docs filegroups, `rust_workflow.sh` dispatch, and `just phase17-verify`. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/BUILD.bazel; BUILD.bazel; justfile]

The key risk is overclaiming: local smoke artifacts, unsigned outputs, fixture bytes, and missing release credentials must not become proof of production signing or release readiness. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py; .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md]

**Primary recommendation:** Implement one integrated Phase 17 plan that adds a JSON release evidence contract, stdlib Python verifier/collector, focused unittest coverage, Bazel/just wiring, and deterministic redacted dry-run outputs while accepting real release-run/signing/comparison evidence only by safe metadata reference. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py]

## Standard Stack

### Core

| Tool/Library | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Python stdlib (`argparse`, `json`, `hashlib`, `re`, `shutil`, `datetime`, `pathlib`, `unittest`, `subprocess`) | Repo requires Python 3.8+; local probe found Python 3.14.4. [VERIFIED: README.md via AGENTS.md stack; python3 --version] | Contract validation, redacted artifact writing, optional operator/release evidence parsing, unit tests, and safe command invocation. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py] | Phase 17 context explicitly asks for a standard-library Python helper, and Phase 13/15/16 already use this model. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase13_ci_evidence.py; tools/bazel/phase15_hardware_evidence.py; tools/bazel/phase16_live_network_evidence.py] |
| Bazel `shell_binary` wrappers | Local probe found Bazel 9.1.1. [VERIFIED: bazel --version] | Expose `phase17_verify` and `phase17_verify_tests` through repo-owned workflow labels. [VERIFIED: tools/bazel/BUILD.bazel; BUILD.bazel] | Existing phases expose verifier/test entrypoints through `tools/bazel/rust_workflow.sh` and root aliases. [VERIFIED: tools/bazel/rust_workflow.sh; justfile] |
| `just` facade | Local probe found just 1.48.0. [VERIFIED: just --version] | Developer command `just phase17-verify` should run tests before verifier. [VERIFIED: justfile] | The project requires a discoverable `justfile` facade. [VERIFIED: .planning/PROJECT.md; AGENTS.md] |
| Existing artifact helpers | Repo-local. [VERIFIED: tools/bazel/artifact_packager.py; tools/bazel/artifact_manifest.py; tools/bazel/artifact_metadata_compare.py] | Produce/normalize representative `.bin`, `.bbf`, `.dfu`, map/provenance/resource/package metadata and compare metadata surfaces. [VERIFIED: tools/bazel/artifact_packager.py; tools/bazel/artifact_manifest.py; tools/bazel/artifact_metadata_compare.py] | Phase 17 context says to build on these instead of replacing BBF/DFU generation. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |

### Supporting

| Tool/Library | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| `utils/pack_fw.py` | Repo-local Python script; active local Python is missing `ecdsa`. [VERIFIED: utils/pack_fw.py; python3 -c 'import ecdsa; print(ecdsa.__version__)'] | Reference BBF packaging and signing-sensitive behavior; `--no-sign` is the developer/local representative path. [VERIFIED: utils/pack_fw.py; tools/bazel/artifact_packager.py; .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md] | Use through existing helpers or release-run evidence; do not use local fixture signing as production proof. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| `utils/dfu.py` | Repo-local Python script. [VERIFIED: utils/dfu.py] | Reference DFU creation and structural suffix/CRC behavior. [VERIFIED: utils/dfu.py; tools/bazel/artifact_packager.py] | Use existing DFU path/status outputs for representative checks; production DFU evidence should arrive as release-run artifact refs. [VERIFIED: .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| ARM GCC/binutils | Repo bootstrap expects `.dependencies/gcc-arm-none-eabi-13.2.1`; local probe did not find `arm-none-eabi-gcc`. [VERIFIED: AGENTS.md stack; arm-none-eabi-gcc --version; .dependencies/gcc-arm-none-eabi-13.2.1/bin/arm-none-eabi-gcc --version] | Full firmware and MMU conversion release builds. [VERIFIED: src/resources/CMakeLists.txt; AGENTS.md stack] | Phase 17 local verifier should not require it; approved release-run evidence or bootstrap must provide it for actual release artifact rows. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; src/resources/CMakeLists.txt] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Stdlib Python verifier | Rust verifier in `buddy-domain` | Rust is valuable for pure domain invariants, but Phase 17 context asks for a thin stdlib Python evidence verifier and existing phase runners already use that pattern. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py] |
| Existing Phase 3 artifact helpers | New BBF/DFU encoder | A new encoder would duplicate signing/package edge cases and contradict the Phase 17 decision to preserve reference-format helper boundaries. [VERIFIED: tools/bazel/artifact_rules.bzl; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| External release evidence refs | Committed release payloads | Committed `.bin`/`.bbf`/`.dfu` payload bytes and private key material are explicitly forbidden for source/planning artifacts. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py] |

**Installation:** No new packages should be installed for the Phase 17 local verifier path. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] Full reference-format BBF/signing or firmware build runs require the repo bootstrap/release environment to provide dependencies such as `ecdsa` and ARM toolchain binaries. [VERIFIED: utils/pack_fw.py; src/resources/CMakeLists.txt; environment probe]

**Version verification:** No npm package version check applies because the recommended stack uses Python stdlib plus existing repo tools. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase17_release_candidate_evidence.py              # stdlib contract verifier and dry-run collector [VERIFIED: phase16 pattern]
├── phase17_release_candidate_evidence_test.py         # stdlib unittest regression coverage [VERIFIED: phase16 pattern]
└── manifests/
    └── phase17_release_candidate_evidence_contract.json # row-level release artifact/signing/comparison contract [VERIFIED: phase15/16 pattern]

build/ci-evidence/phase17/
├── run-manifest.json                                  # generated, ignored machine-readable run summary [VERIFIED: phase16 pattern]
├── normalized-artifact-results.json                   # generated normalized release rows [VERIFIED: phase16 pattern]
├── redacted-signing-provenance-summary.json           # generated secret-safe summary [VERIFIED: phase13/16 pattern]
├── comparison-classification-report.json              # generated mismatch classifications [VERIFIED: 17-CONTEXT.md]
├── release-operator-input.json                        # generated evidence input template [VERIFIED: 17-CONTEXT.md]
├── source-contract-snapshots/
└── logs/
```

### Pattern 1: Contract-First Evidence Gate

**What:** A checked-in JSON contract defines required rows, status vocabulary, artifact kinds, source refs, proof scopes, redaction boundaries, expected artifact paths, and residual cutover gates. [VERIFIED: tools/bazel/manifests/phase16_live_network_evidence_contract.json; tools/bazel/phase16_live_network_evidence.py]

**When to use:** Use this for all Phase 17 release artifact, signing/provenance, and comparison surfaces because every required surface must be represented and independently classified. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; .planning/REQUIREMENTS.md]

**Planning implication:** Add constants in the verifier for `REQUIRED_REQUIREMENT_IDS`, required row IDs/surfaces, allowed statuses, required artifact kinds, operator/release input fields, forbidden marker regexes, and overclaim phrases. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]

### Pattern 2: Local Dry-Run Is Not Production Proof

**What:** Quick mode should validate schema/source refs/wiring/security and write deterministic artifacts, but release rows default to `pending-release-input`, `release-run-required`, `external-signing-required`, or similar non-pass states unless approved release evidence is supplied. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py]

**When to use:** Use for artifact families requiring real release outputs, signing key identity, build input identity, provenance, and reference comparison. [VERIFIED: .planning/REQUIREMENTS.md; ProjectOptions.cmake; utils/pack_fw.py]

**Planning implication:** Tests should assert that `--quick` with no release evidence produces pending/source-contract statuses, and that a `passed` result is accepted only from a complete release evidence row with safe artifact refs. [VERIFIED: tools/bazel/phase16_live_network_evidence_test.py]

### Pattern 3: Safe External Artifact References

**What:** Accept repo-relative refs under `build/ci-evidence/phase17` or explicit `external://phase17/...` refs, and reject absolute paths, `..`, symlink escapes, and committed generated release payloads. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py]

**When to use:** Use for release-run logs, retained release artifact names, signing/provenance summaries, CI artifact names, and comparison reports. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

**Planning implication:** Copy Phase 16 `require_repo_relative_under`, `contained_output_dir`, and `validate_artifact_refs` behavior, adjusted to `DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase17")`. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]

### Pattern 4: Source Ref Resolution by `file#row-id`

**What:** Phase 16 verifies JSON source refs by resolving `file#row-id` and confirming the row exists. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]

**When to use:** Use it for Phase 11 rows, Phase 3/7/10 manifests, Phase 13/15/16 contracts, and any Phase 17 cross-reference needed for traceability. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/manifests/phase11_reference_comparisons.json]

**Planning implication:** Require every contract row to cite at least one source ref and validate that each ref resolves locally before writing generated outputs. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]

### Anti-Patterns to Avoid

- **Umbrella release pass:** One aggregate status hides which artifact family blocks REL-01/REL-02/REL-03; use row-level status and mismatch class instead. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
- **Local fixture signing as production proof:** `test-key` and `unsigned-local` may validate schema and redaction but cannot satisfy release signing proof. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/artifact_manifest.py]
- **Raw payload/checksum dumps in evidence:** Store names, sizes, hashes, package member names, and artifact refs; do not store firmware bytes or raw `.bin`/`.bbf`/`.dfu` payload text. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py]
- **Byte-parity overclaim:** Phase 11 comparison rows are normalized semantic comparisons unless a deterministic fixture and normalization rule are named. [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json; tools/bazel/manifests/phase11_reference_comparisons.json]
- **Mutating archived v1.0 evidence:** Phase 17 should cite archived v1.0 and Phase 11 evidence, not edit it. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; .planning/ROADMAP.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| BBF/DFU reference packaging | A new local BBF or DFU encoder | `artifact_packager.py`, `artifact_manifest.py`, `artifact_metadata_compare.py`, `utils/pack_fw.py --no-sign`, and `utils/dfu.py` through existing Bazel helpers [VERIFIED: tools/bazel/artifact_packager.py; tools/bazel/artifact_rules.bzl] | Existing helpers encode bootstrap-required/ci-only/reference-only status boundaries and prevent non-reference local encoders from satisfying release artifact proof. [VERIFIED: .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md] |
| Release signing | A custom signing workflow or committed test key | External release signing evidence by key name/fingerprint and artifact digest only [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; ProjectOptions.cmake; utils/pack_fw.py] | Private key bytes and signing payloads are forbidden, and local fixture/test-key evidence cannot satisfy production proof. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| Artifact retention model | New CI artifact semantics | Phase 13 retention shape plus `build/ci-evidence/phase17` outputs [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json; tools/bazel/phase13_ci_evidence.py] | Phase 13 already defines retained manifest snapshots, normalized comparison output, redacted summaries, and CI artifact retention boundaries. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] |
| Reference comparison taxonomy | A separate release vocabulary | Phase 11 comparison and cutover readiness vocabulary plus required Phase 17 mismatch classes [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; tools/bazel/manifests/phase11_cutover_readiness.json; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] | Phase 11 already names release metadata, signing-sensitive status names, byte-identity guardrails, and reference-demotion blockers. [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; tools/bazel/manifests/phase11_cutover_readiness.json] |
| Secret scanning | A prose-only checklist | Regex/phrase guard tests in the Phase 17 verifier [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py] | Prior phases prove the expected pattern: fail on private-key blocks, credential fields, firmware payload markers, and overclaim phrases before writing/retaining artifacts. [VERIFIED: tools/bazel/phase16_live_network_evidence_test.py] |

**Key insight:** Phase 17 is an evidence-governance layer over release artifacts, not a replacement for release infrastructure; the valuable code is the contract, validation, redaction, and traceability logic. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py]

## Common Pitfalls

### Pitfall 1: Dry-Run Artifacts Accidentally Become Release Proof

**What goes wrong:** A local `--quick` run produces smoke artifacts and marks release rows `passed`. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Why it happens:** Representative Phase 3 outputs exist locally and can look release-like even when they are `local-smoke`, `unsigned-local`, `bootstrap-required`, `ci-only`, or `reference-only`. [VERIFIED: tools/bazel/manifests/representative_products.json; .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md]
**How to avoid:** Default release rows to pending or release-required statuses and accept `passed` only from complete release-run evidence with allowed evidence type and safe refs. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]
**Warning signs:** The generated run manifest contains `passed` for signing/provenance rows when no release evidence input was supplied. [VERIFIED: tools/bazel/phase16_live_network_evidence_test.py]

### Pitfall 2: Signing Evidence Leaks Key Material or Payload Bytes

**What goes wrong:** Evidence stores private key blocks, `signing_key_value`, certificate private material, raw payload text, or raw `.bin`/`.bbf`/`.dfu` bytes. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Why it happens:** `SIGNING_KEY` is a path to a private EC key and `utils/pack_fw.py` reads the key unless `--no-sign` is used. [VERIFIED: ProjectOptions.cmake; utils/pack_fw.py]
**How to avoid:** Store release key identity by safe name/fingerprint, artifact digest, timestamp, command/source input identity, retention path, and verification outcome only. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Warning signs:** Security scan finds private-key markers, credential assignments, or firmware payload markers in contract, generated outputs, or planning artifacts. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py]

### Pitfall 3: Missing Resource/Auxiliary Surfaces

**What goes wrong:** The contract covers `.bin`/`.bbf`/`.dfu` but omits resources, language bundles, WUI, ESP, MMU, Dwarf, ModularBed, xBuddy Extension, or package manifests. [VERIFIED: .planning/REQUIREMENTS.md; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Why it happens:** The representative product matrix is narrower than the full release-candidate artifact surface. [VERIFIED: tools/bazel/manifests/representative_products.json; .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md]
**How to avoid:** Add required surface IDs/constants and tests that remove one surface at a time and fail with the missing surface name. [VERIFIED: tools/bazel/phase16_live_network_evidence_test.py]
**Warning signs:** No row cites `phase7_generated_outputs.json`, `src/resources/CMakeLists.txt`, `phase10_auxiliary_build_update.json`, or `phase10_auxiliary_controllers.json`. [VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json; tools/bazel/manifests/phase10_auxiliary_build_update.json; tools/bazel/manifests/phase10_auxiliary_controllers.json]

### Pitfall 4: Release Comparison Uses the Wrong Classification Vocabulary

**What goes wrong:** Comparison rows use ad hoc statuses such as `ok`, `waived`, or `different`. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Why it happens:** Release comparison is tempting to model separately from Phase 11. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**How to avoid:** Require exactly `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue` for mismatch classification, plus reason and owner. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Warning signs:** The comparison report has unclassified rows or classifications that do not map to REL-03. [VERIFIED: .planning/REQUIREMENTS.md]

### Pitfall 5: CI Artifact Retention Is Treated as Release Approval

**What goes wrong:** CI retains Phase 17 summaries and someone reads that as signed release approval. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**Why it happens:** Phase 13 retention proves downloadability and redaction, not production signing or release-manager approval. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
**How to avoid:** Keep generated summaries explicit about supplied inputs, pending rows, signing mode, and residual gates. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]
**Warning signs:** Redacted summary text contains "release readiness proven", "release-candidate passed locally", or "signing proof complete" without supplied release evidence. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]

## Code Examples

### Contract Row Shape

```json
{
  "id": "rel-artifact-bbf-package",
  "requirement_ids": ["REL-01", "REL-02", "REL-03"],
  "artifact_surface": "bbf",
  "proof_scope": "release-run-artifact",
  "mode": "release-or-approved-dry-run-input",
  "expected_artifact_path": "build/ci-evidence/phase17/logs/rel-artifact-bbf-package.log",
  "retained_artifact_kind": "release-log-reference",
  "allowed_statuses": [
    "pending-release-input",
    "release-run-required",
    "external-signing-required",
    "blocked-signing-key-unavailable",
    "passed",
    "failed"
  ],
  "source_contract_refs": [
    "tools/bazel/manifests/phase11_reference_comparisons.json#ref-release-metadata"
  ],
  "mismatch_classes": ["pass", "intentional-delta", "blocker", "deferred-retained-code-issue"],
  "redaction_required": true
}
```

This shape follows Phase 16 scenario fields but replaces live-service concepts with release artifact/signing/comparison surfaces. [VERIFIED: tools/bazel/manifests/phase16_live_network_evidence_contract.json; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

### Safe Artifact Ref Validation

```python
def validate_artifact_refs(artifact_refs, row_name):
    if not isinstance(artifact_refs, list) or not artifact_refs:
        raise VerificationError(f"{row_name} artifact_refs must be a non-empty list")
    parsed_refs = []
    for index, artifact_ref in enumerate(artifact_refs):
        ref_name = f"{row_name} artifact_refs[{index}]"
        if not isinstance(artifact_ref, str) or not artifact_ref:
            raise VerificationError(f"{ref_name} must be a non-empty string")
        if artifact_ref.startswith(("external://phase17/", "artifact://phase17/")):
            parsed_refs.append(artifact_ref)
            continue
        require_repo_relative_under(artifact_ref, DEFAULT_OUTPUT_DIR, ref_name)
        parsed_refs.append(artifact_ref)
    return parsed_refs
```

This should be adapted from the Phase 16 artifact-ref guard and scoped to `build/ci-evidence/phase17`. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

### Tests-Before-Verifier Wiring

```make
phase17-verify:
    bazel run //tools/bazel:phase17_verify_tests
    bazel run //tools/bazel:phase17_verify
```

This mirrors the established Phase 13 through Phase 16 `justfile` pattern. [VERIFIED: justfile]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 3 representative artifact smoke checks proved local package-surface scaffolding only. [VERIFIED: .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md] | Phase 17 should add release-candidate evidence rows that can ingest approved release-run artifact/signing/provenance inputs. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] | Phase 17 context gathered 2026-06-19. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] | Planner must separate local smoke from production release evidence. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| Phase 11 named release-candidate/signing-sensitive proof as non-local blockers. [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json; .planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md] | Phase 17 should formalize those blockers into machine-readable release artifact, signing, provenance, retention, and comparison gates. [VERIFIED: .planning/ROADMAP.md; .planning/REQUIREMENTS.md] | v1.1 roadmap Phase 17. [VERIFIED: .planning/ROADMAP.md] | Planner should cite Phase 11 rows rather than redefining release readiness. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| Phase 13 retained CI artifacts but left release proof pending. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] | Phase 17 should retain redacted run manifests, source snapshots, summaries, and external refs without treating CI-only outputs as release proof. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] | Phase 13 completed 2026-06-16; Phase 17 starts after Phase 16. [VERIFIED: .planning/ROADMAP.md; .planning/STATE.md] | Planner should reuse retention mechanics and add release-input semantics. [VERIFIED: tools/bazel/phase13_ci_evidence.py; tools/bazel/phase16_live_network_evidence.py] |

**Deprecated/outdated:** Do not use local `utils/pack_fw.py --no-sign` output as signing proof; Phase 3 explicitly scoped it as developer/local representative evidence. [VERIFIED: tools/bazel/phase3_artifacts.sh; .planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md]

## Assumptions Log

All claims in this research were verified or cited in this session; no `[ASSUMED]` claims are intentionally present. [VERIFIED: source audit performed in this session]

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| N/A | No assumed claims recorded. | N/A | N/A |

## Open Questions

1. **Which approved release environment will supply production signing evidence?**
   - What we know: Local checks must not require private signing keys and production pass rows require supplied release-run evidence. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]
   - What's unclear: The repo does not name the release signing environment, operator approval path, or exact key identity registry. [VERIFIED: ProjectOptions.cmake; .planning/codebase/INTEGRATIONS.md]
   - Recommendation: Planner should add an operator/release input template with safe fields and keep production rows pending until maintainers provide the source of truth. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

2. **Should Phase 17 run any full firmware build locally?**
   - What we know: Local environment has Bazel, Python, and just, but active Python lacks `ecdsa` and the ARM toolchain is missing from PATH and `.dependencies`. [VERIFIED: environment probe]
   - What's unclear: Whether the actual implementation environment will have bootstrap dependencies installed when Phase 17 executes. [VERIFIED: environment probe]
   - Recommendation: Planner should keep `just phase17-verify` deterministic without full firmware builds and treat full builds as release-run evidence inputs. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

3. **How many product/profile rows are required for release-candidate proof?**
   - What we know: Context requires row coverage for all listed artifact families, and representative products currently include MINI boot/noboot, MK4 boot, MINI resource package, and an auxiliary manifest-only row. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md; tools/bazel/manifests/representative_products.json]
   - What's unclear: The exact release matrix for every supported product/profile in the approved release environment is not encoded in a Phase 17 contract yet. [VERIFIED: .planning/ROADMAP.md; tools/bazel/manifests/representative_products.json]
   - Recommendation: Planner should require explicit contract rows for every required surface and allow exact scenario IDs/schema order to follow implementation discretion. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 17 verifier/tests and existing artifact helpers | yes | 3.14.4 [VERIFIED: python3 --version] | None needed for local verifier. |
| Bazel | `phase17_verify` / `phase17_verify_tests` labels | yes | 9.1.1 [VERIFIED: bazel --version] | Use direct `python3` commands only for debugging; plan should still wire Bazel. [VERIFIED: tools/bazel/rust_workflow.sh] |
| just | Developer facade | yes | 1.48.0 [VERIFIED: just --version] | Direct `bazel run` commands. [VERIFIED: justfile] |
| Git | Source state and optional evidence provenance fields | yes | 2.53.0 [VERIFIED: git --version] | Omit commit metadata from dry-run if unavailable, but do not omit artifact/source refs. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| Cargo/Rust | Existing Rust workspace checks if touched | yes | cargo 1.91.1 [VERIFIED: cargo --version] | Avoid Rust changes for Phase 17 unless necessary. [VERIFIED: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| Python `ecdsa` package | Real `utils/pack_fw.py` signing/reference BBF generation | no | ModuleNotFoundError [VERIFIED: python3 -c 'import ecdsa; print(ecdsa.__version__)'] | Use local `unsigned-local`/dry-run status or approved release environment evidence. [VERIFIED: tools/bazel/artifact_packager.py; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md] |
| ARM `arm-none-eabi-gcc` / binutils | Full firmware builds and MMU hex-to-bin conversion | no | Missing on PATH and under `.dependencies/gcc-arm-none-eabi-13.2.1` [VERIFIED: environment probe] | Use release-run evidence or run repo bootstrap before full release artifact generation. [VERIFIED: AGENTS.md stack; src/resources/CMakeLists.txt] |
| Node | GSD tooling lifecycle metadata | yes | v24.13.0 [VERIFIED: node --version] | None needed. |

**Missing dependencies with no fallback:** None for the local Phase 17 contract/verifier/dry-run plan. [VERIFIED: environment probe; .planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md]

**Missing dependencies with fallback:** `ecdsa` and ARM toolchain are missing locally, so real reference-format signing/full firmware builds must come from bootstrap or an approved release environment and remain explicit release-run input. [VERIFIED: environment probe; utils/pack_fw.py; src/resources/CMakeLists.txt]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` through Bazel `shell_binary` wrappers. [VERIFIED: tools/bazel/phase16_live_network_evidence_test.py; tools/bazel/BUILD.bazel] |
| Config file | None for stdlib unittest; `pyproject.toml` only configures pytest integration tests. [VERIFIED: pyproject.toml; tools/bazel/phase16_live_network_evidence_test.py] |
| Quick run command | `bazel run //tools/bazel:phase17_verify_tests && bazel run //tools/bazel:phase17_verify` after implementation. [VERIFIED: justfile phase13/14/15/16 pattern] |
| Full suite command | `just phase17-verify` after implementation. [VERIFIED: justfile phase13/14/15/16 pattern] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| REL-01 | Contract requires rows for `.bin`, `.bbf`, `.dfu`, map/provenance, resources, language, WUI, ESP, MMU, auxiliary firmware, manifests, and comparison reports. [VERIFIED: .planning/REQUIREMENTS.md; 17-CONTEXT.md] | unit/contract | `python3 tools/bazel/phase17_release_candidate_evidence_test.py` | No - Wave 0 |
| REL-02 | Signing/provenance rows require key identity, signing mode, command/source input identity, artifact digest, timestamp, retention path, and verification outcome while rejecting private key/payload/credential markers. [VERIFIED: 17-CONTEXT.md] | unit/security | `python3 tools/bazel/phase17_release_candidate_evidence_test.py` | No - Wave 0 |
| REL-03 | Comparison rows require archived v1.0/Phase 11 refs and mismatch class exactly `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue`. [VERIFIED: 17-CONTEXT.md; tools/bazel/manifests/phase11_reference_comparisons.json] | unit/contract | `python3 tools/bazel/phase17_release_candidate_evidence_test.py` | No - Wave 0 |
| REL-01/02/03 | Bazel root aliases, docs filegroup, `rust_workflow.sh`, and `just phase17-verify` run tests before verifier. [VERIFIED: justfile; tools/bazel/rust_workflow.sh; tools/bazel/BUILD.bazel] | wiring | `bazel run //tools/bazel:phase17_verify_tests && bazel run //tools/bazel:phase17_verify` | No - Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 tools/bazel/phase17_release_candidate_evidence_test.py` plus `python3 tools/bazel/phase17_release_candidate_evidence.py --contract-only`, `--security-only`, `--wiring-only`, and `--quick`. [VERIFIED: tools/bazel/phase16_live_network_evidence.py]
- **Per wave merge:** `bazel run //tools/bazel:phase17_verify_tests && bazel run //tools/bazel:phase17_verify`. [VERIFIED: justfile phase13/14/15/16 pattern]
- **Phase gate:** `just phase17-verify` with generated `build/ci-evidence/phase17` artifacts inspected for pending release inputs and redaction cleanliness. [VERIFIED: justfile; tools/bazel/phase16_live_network_evidence.py]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - covers REL-01/REL-02/REL-03. [VERIFIED: phase17 file missing via find]
- [ ] `tools/bazel/phase17_release_candidate_evidence.py` - contract/security/wiring/quick verifier. [VERIFIED: phase17 file missing via rg]
- [ ] `tools/bazel/phase17_release_candidate_evidence_test.py` - stdlib unit regression suite. [VERIFIED: phase17 file missing via rg]
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring for Phase 17 labels. [VERIFIED: current files contain phase13-16 labels but no phase17 labels]

## Security Domain

Security enforcement is enabled for research purposes because `.planning/config.json` does not explicitly set `security_enforcement: false`. [VERIFIED: .planning/config.json; researcher instructions] OWASP ASVS is currently published with stable version 5.0.0, and OWASP recommends including the version element when referencing ASVS identifiers. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | No for the local verifier; release operator identity is metadata, not an auth/session system in this phase. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; 17-CONTEXT.md] | Require operator/release evidence fields such as operator, timestamp, evidence type, and artifact refs; do not implement authentication in Phase 17. [VERIFIED: tools/bazel/phase16_live_network_evidence.py] |
| V3 Session Management | No. Phase 17 does not add sessions or cookies. [VERIFIED: 17-CONTEXT.md] | Not applicable. |
| V4 Access Control | Yes at evidence-boundary level because release-run pass status must be limited to approved release evidence inputs. [VERIFIED: 17-CONTEXT.md] | Enforce allowed proof scopes/evidence types and reject local `passed` defaults. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py] |
| V5 Validation, Sanitization, and Encoding | Yes for JSON contract parsing, source refs, artifact refs, timestamps, status vocabularies, and path validation. [CITED: https://devguide.owasp.org/en/03-requirements/05-asvs/; VERIFIED: tools/bazel/phase16_live_network_evidence.py] | Parse all boundary data, require enums/required fields, validate ISO-8601 UTC timestamps, and reject path traversal/symlink escape. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py] |
| V6 Stored Cryptography | Yes for release signing evidence, but only as external key identity/digest verification metadata. [CITED: https://devguide.owasp.org/en/03-requirements/05-asvs/; VERIFIED: 17-CONTEXT.md; utils/pack_fw.py] | Do not hand-roll signing; do not store private keys; record release key identity/fingerprint and artifact digest only. [VERIFIED: 17-CONTEXT.md; ProjectOptions.cmake] |
| V8 Data Protection | Yes for preventing private keys, credentials, certificates with private material, crash dumps, and firmware payload bytes from retained artifacts. [CITED: https://devguide.owasp.org/en/03-requirements/05-asvs/; VERIFIED: tools/bazel/phase16_live_network_evidence.py] | Regex/phrase scans over contracts, generated outputs, and evidence inputs. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py] |
| V12 Files and Resources | Yes for artifact path controls and resource package evidence. [CITED: https://devguide.owasp.org/en/03-requirements/05-asvs/; VERIFIED: src/resources/CMakeLists.txt; tools/bazel/phase16_live_network_evidence.py] | Restrict outputs to `build/ci-evidence/phase17` or `external://phase17/...`, reject traversal, and do not commit generated payloads. [VERIFIED: 17-CONTEXT.md; .gitignore] |

### Known Threat Patterns for Phase 17

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Private signing key, certificate private material, token, password, or firmware payload leakage in evidence | Information Disclosure | Reject forbidden text markers before accepting operator/release evidence and after writing generated artifacts. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py] |
| Path traversal or symlink escape from artifact refs/output dir | Tampering / Information Disclosure | Enforce repo-relative paths under `build/ci-evidence/phase17`, allow only explicit external refs, and check resolved output paths. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/phase16_live_network_evidence_test.py] |
| Local dry-run overclaiming production release/signing approval | Repudiation / Process Integrity | Maintain explicit status vocabulary, reject overclaim strings, and require supplied release evidence for pass rows. [VERIFIED: 17-CONTEXT.md; tools/bazel/phase16_live_network_evidence.py] |
| Command injection through release helper execution | Tampering / Elevation of Privilege | Use `subprocess.run([...], shell=False)` if invoking helpers, and keep shell orchestration thin. [VERIFIED: 17-CONTEXT.md; tools/bazel/phase16_live_network_evidence_test.py] |
| Incomplete mismatch classification | Repudiation / Process Integrity | Require exactly one mismatch class, reason, owner phase, source refs, and residual risk for each comparison row. [VERIFIED: 17-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md` - locked Phase 17 decisions, discretion, deferred scope, lifecycle ID, and canonical refs. [VERIFIED: cat]
- `.planning/REQUIREMENTS.md` - REL-01, REL-02, REL-03 requirement text. [VERIFIED: cat]
- `.planning/ROADMAP.md` - Phase 17 goal, dependencies, success criteria, and roadmap position. [VERIFIED: cat]
- `.planning/PROJECT.md` and `.planning/STATE.md` - project constraints, current status, and evidence-hardening posture. [VERIFIED: cat]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/*.md`, `standards/languages/rust.md` - repo and Bright Builds rules. [VERIFIED: cat]
- `tools/bazel/phase16_live_network_evidence.py` and `tools/bazel/phase16_live_network_evidence_test.py` - closest verifier/test template. [VERIFIED: sed]
- `tools/bazel/phase13_ci_evidence.py` and `tools/bazel/manifests/phase13_ci_evidence_contract.json` - CI retention and redaction model. [VERIFIED: sed]
- `tools/bazel/artifact_packager.py`, `tools/bazel/artifact_manifest.py`, `tools/bazel/artifact_metadata_compare.py`, `tools/bazel/artifact_rules.bzl`, `tools/bazel/manifests/representative_products.json` - artifact helper stack. [VERIFIED: sed/cat]
- `tools/bazel/manifests/phase11_reference_comparisons.json` and `tools/bazel/manifests/phase11_cutover_readiness.json` - release metadata, byte-identity, secret, and demotion guardrails. [VERIFIED: sed]
- `tools/bazel/manifests/phase7_generated_outputs.json`, `src/resources/CMakeLists.txt`, `tools/bazel/manifests/phase10_auxiliary_build_update.json`, and `tools/bazel/manifests/phase10_auxiliary_controllers.json` - resource/language/WUI/ESP/MMU/auxiliary release surfaces. [VERIFIED: sed/rg]

### Secondary (MEDIUM confidence)

- `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONCERNS.md` - codebase map for release artifacts, signing keys, CI, testing, and security concerns. [VERIFIED: sed/rg]
- Environment probes: `python3 --version`, `bazel --version`, `just --version`, `cargo --version`, `git --version`, `node --version`, Python `ecdsa` import, and ARM GCC probes. [VERIFIED: command outputs]
- OWASP ASVS official project page and OWASP Developer Guide ASVS category overview. [CITED: https://owasp.org/www-project-application-security-verification-standard/; https://devguide.owasp.org/en/03-requirements/05-asvs/]

### Tertiary (LOW confidence)

- None. [VERIFIED: source hierarchy review]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - Phase 17 context specifies stdlib Python and existing Bazel/just patterns; local tools are available for contract verification. [VERIFIED: 17-CONTEXT.md; environment probe]
- Architecture: HIGH - Phase 13/15/16 runners and contracts provide a direct implementation template. [VERIFIED: tools/bazel/phase13_ci_evidence.py; tools/bazel/phase15_hardware_evidence.py; tools/bazel/phase16_live_network_evidence.py]
- Pitfalls: HIGH - Prior phases already encode redaction, overclaim, source-ref, path, and non-local proof boundaries. [VERIFIED: tools/bazel/phase16_live_network_evidence.py; tools/bazel/manifests/phase11_cutover_readiness.json]
- Production release-run specifics: MEDIUM - repo encodes signing path and artifact surfaces, but approved release environment/key identity source is not present. [VERIFIED: ProjectOptions.cmake; utils/pack_fw.py; .planning/codebase/INTEGRATIONS.md]

**Research date:** 2026-06-19 [VERIFIED: current_date]
**Valid until:** 2026-07-19 for local repo patterns; re-check before planning if release infrastructure, signing policy, Bazel version, or ASVS version changes. [VERIFIED: .planning/config.json; environment probe; CITED: https://owasp.org/www-project-application-security-verification-standard/]
