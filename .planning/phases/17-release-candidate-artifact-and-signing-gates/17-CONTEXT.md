---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 17-2026-06-19T13-57-17
generated_at: 2026-06-19T13:57:17.951Z
---

# Phase 17: Release Candidate Artifact and Signing Gates - Context

**Gathered:** 2026-06-19
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 17 turns release-candidate firmware artifacts, resources, language/WUI bundles, ESP/MMU/auxiliary packages, signing evidence, provenance, artifact retention, and archived v1.0 comparison into a durable Bazel-owned evidence gate. It should define a phase-owned contract, deterministic local/dry-run output, optional operator or release-run input validation, redacted retained artifacts, and local verification through the existing Bazel/just facade.

This phase does not approve retained-code acceptance, final reference demotion, or production release by itself. It also must not treat unsigned local smoke outputs, fixture package bytes, dry-run generated summaries, or absent release signing credentials as proof that production release-candidate artifacts are signed or release-ready. Missing release-run inputs should remain explicit pending release evidence with artifact surface, command, key identity evidence, source comparison, classification, and residual risk named.

</domain>

<decisions>
## Implementation Decisions

### Release Artifact Matrix

- **D-01:** Add a Phase 17-owned release-candidate evidence contract instead of mutating Phase 11, Phase 13, Phase 15, or Phase 16 manifests. The contract should name each required artifact family with requirement mapping, proof scope, expected artifact path, retained artifact kind, and residual cutover gates.
- **D-02:** Use row-level release qualification, not one umbrella release pass. Rows should cover `.bin`, `.bbf`, `.dfu`, map/provenance, resource image/package, language bundles, WUI assets, ESP packages, MMU packages, Dwarf/ModularBed/xBuddy Extension auxiliary firmware, package manifests, and artifact comparison reports.
- **D-03:** Local deterministic checks may create representative smoke artifacts and dry-run summaries, but real release-candidate rows can pass only from supplied release-run evidence or approved release environment artifacts. Use statuses such as `pending-release-input`, `release-run-required`, `external-signing-required`, `blocked-signing-key-unavailable`, `source-contract-passed`, `passed`, and `failed`.
- **D-04:** Preserve Phase 3 representative artifact helpers where useful. Phase 17 should build on `artifact_packager.py`, `artifact_manifest.py`, `artifact_metadata_compare.py`, `representative_products.json`, and `phase3_artifacts.sh` instead of replacing reference-format BBF/DFU generation.

### Signing and Provenance Hygiene

- **D-05:** Signing evidence records key identity, signing mode, command/source input identity, artifact digest, timestamp, retention path, and verification outcome. It must not include private signing keys, raw key bytes, certificates with private material, credential values, or signing payload bytes in source or planning artifacts.
- **D-06:** The evidence model should support external release-key evidence by name or fingerprint only. Local fixture/test-key evidence can validate schema and redaction behavior but cannot satisfy production signing proof.
- **D-07:** Provenance rows should verify build input identity, product/printer/board/MCU/bootloader metadata, package member names, source manifest references, and artifact hashes. They should avoid claiming byte-for-byte CMake release parity unless a real release comparison artifact is supplied.
- **D-08:** Verifier guards must reject committed or generated artifacts containing private key blocks, certificate private material, `signing_key_value`, firmware payload markers, raw `.bin`/`.bbf`/`.dfu` payload text, token/password markers, release readiness claims, signing proof overclaims, retained-code approval, or reference-demotion approval.

### Reference Comparison and Mismatch Classification

- **D-09:** Every release-candidate comparison row should cite archived v1.0 reference evidence and classify mismatches as exactly one of `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue`.
- **D-10:** Comparison output should identify artifact surface, product/profile, reference source, Rust/Bazel surface, normalized fields compared, artifact refs, mismatch class, owner phase, and residual risk. Binary payload bytes and signing secrets remain excluded from checked-in evidence.
- **D-11:** Reference comparison should use and extend the Phase 11 reference comparison and cutover readiness taxonomy rather than inventing a separate release vocabulary.
- **D-12:** Release-candidate comparison can satisfy `REL-03` only when every required surface is represented and every mismatch has one of the allowed classifications with a reason and owner.

### Artifact Retention and CI Integration

- **D-13:** Generated Phase 17 runtime artifacts should live under an ignored directory such as `build/ci-evidence/phase17`, following Phase 13 through Phase 16. Checked-in files define contracts, schema, verifier logic, redaction guards, and dry-run examples only.
- **D-14:** Generated outputs should include a machine-readable run manifest, normalized artifact results, redacted signing/provenance summary, comparison classification report, source contract snapshot, release operator input template, and log or external-artifact references.
- **D-15:** Phase 13's artifact-retention model remains the CI bridge. CI may retain Phase 17 generated summaries and manifest snapshots, but CI without release inputs or signing evidence must not become release proof.
- **D-16:** Artifact paths should be repo-relative under `build/ci-evidence/phase17` or explicit `external://phase17/...` references. Verifiers should reject path traversal and committed generated release artifacts.

### Runner and Developer Workflow

- **D-17:** Add a dedicated standard-library Python release evidence verifier/collector, likely `tools/bazel/phase17_release_candidate_evidence.py`, with focused unit tests in `tools/bazel/phase17_release_candidate_evidence_test.py`.
- **D-18:** Expose Phase 17 through a checked-in contract manifest, Bazel `phase17_verify` / `phase17_verify_tests` labels, root docs/alias filegroups, `tools/bazel/rust_workflow.sh`, and `just phase17-verify`.
- **D-19:** Local phase verification should be deterministic: validate contract schema, required release rows, source refs, wiring, dry-run generated artifacts, redaction, path guards, mismatch classification, signing/provenance semantics, and overclaim guards without requiring private signing keys or full firmware builds.
- **D-20:** Keep orchestration thin and auditable: prefer JSON contracts, explicit status vocabularies, small Python helpers, `subprocess.run` without shell execution when external commands are needed, and focused stdlib tests over broad release automation rewrites.

### Traceability and Prior Evidence

- **D-21:** Every Phase 17 row must map to `REL-01`, `REL-02`, and/or `REL-03` plus relevant archived v1.0 and Phase 11 evidence rows. Rows should cite Phase 3 artifact/generator evidence, Phase 7 resource evidence, Phase 10 auxiliary package evidence, Phase 13 CI retention, Phase 15 hardware boundaries, and Phase 16 live-service boundaries where applicable.
- **D-22:** Preserve Phase 15 and Phase 16 boundaries: hardware and live-service evidence may support readiness, but they do not satisfy release-candidate packaging, signing, provenance, or artifact comparison proof.
- **D-23:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 17-2026-06-19T13-57-17`.

### the agent's Discretion

- Exact scenario IDs, schema field order, status names, generated artifact file names, helper boundaries, and dry-run output shape are flexible if the result remains deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated implementation plan or several tasks inside one plan, but the roadmap expects one completed plan for this phase.
- Prefer contract-backed evidence and verifier tests over prose-only release checklists. Operator-facing release instructions are useful only when backed by machine-readable artifacts and verifier checks.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 17 goal, dependency, success criteria, and v1.1 roadmap position.
- `.planning/REQUIREMENTS.md` - `REL-01`, `REL-02`, and `REL-03` acceptance requirements.
- `.planning/STATE.md` - current milestone state, blockers, and Phase 17 starting point.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, and Bright Builds constraints.
- `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md` - CI evidence contract, artifact retention, and pending release proof boundaries.
- `.planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md` - passed Phase 13 local verification boundary.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md` - hardware evidence contract and release-boundary decisions.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-VERIFICATION.md` - passed Phase 15 verification and residual release risks.
- `.planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md` - live-service evidence contract and release-boundary decisions.
- `.planning/phases/16-live-network-and-transfer-qualification/16-VERIFICATION.md` - passed Phase 16 verification and residual release/signing risks.

### Archived v1.0 cutover and artifact evidence

- `.planning/milestones/v1.0-REQUIREMENTS.md` - archived v1.0 requirement surface that Phase 17 must not redefine.
- `.planning/milestones/v1.0-ROADMAP.md` - archived v1.0 phase history and evidence foundation.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - v1.0 audit outcome and preserved release-candidate/signing gates.
- `.planning/milestones/v1.0-phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md` - reference artifact metadata capture expectations.
- `.planning/milestones/v1.0-phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md` - baseline artifact matrix.
- `.planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-CONTEXT.md` - artifact and generator parity decisions.
- `.planning/milestones/v1.0-phases/03-artifact-and-generator-parity/03-VERIFICATION.md` - Phase 3 release artifact metadata and generated-output evidence boundary.
- `.planning/milestones/v1.0-phases/07-persistence-storage-and-resource-compatibility/07-VERIFICATION.md` - resource and storage-media release boundary.
- `.planning/milestones/v1.0-phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md` - auxiliary firmware and update proof boundaries.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md` - parity pyramid, release-candidate proof, retained-code, reference comparison, and overclaim decisions.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md` - passed Phase 11 local evidence boundary.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-CONTEXT.md` - metadata hygiene and no-overclaim constraints for archived evidence.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-VERIFICATION.md` - v1.0 archive-clean verification record.

### Existing verifier, manifest, artifact, and release patterns

- `tools/bazel/phase16_live_network_evidence.py` - latest evidence verifier template for contracts, dry-run artifacts, operator input validation, path guards, security scans, and wiring checks.
- `tools/bazel/phase16_live_network_evidence_test.py` - latest stdlib regression-test pattern for evidence contract behavior.
- `tools/bazel/manifests/phase16_live_network_evidence_contract.json` - generated artifact and residual release gate model to mirror.
- `tools/bazel/phase15_hardware_evidence.py` - hardware evidence verifier and external input validation pattern.
- `tools/bazel/phase13_ci_evidence.py` - CI evidence writer, artifact sanitizer, and overclaim scan pattern.
- `tools/bazel/manifests/phase13_ci_evidence_contract.json` - artifact-retention and generated-output contract shape.
- `tools/bazel/phase11_verify.py` - aggregate cutover verifier, proof-scope taxonomy, retained non-local blocker pattern, and no-overclaim guard.
- `tools/bazel/phase11_verify_test.py` - Phase 11 verifier regression-test pattern.
- `tools/bazel/manifests/phase11_parity_pyramid.json` - release-candidate layer row and cutover proof-scope taxonomy.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - reference-demotion blocker and release-candidate gate model.
- `tools/bazel/manifests/phase11_reference_comparisons.json` - release artifact metadata and release metadata comparison rows.
- `tools/bazel/manifests/phase11_requirement_evidence.json` - requirement-to-evidence mapping pattern with pending release-candidate statuses.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - retained-code evidence requirements for release artifacts, resources, and auxiliary firmware.
- `tools/bazel/artifact_packager.py` - deterministic package-surface artifact helper and reference-format BBF/DFU generation boundary.
- `tools/bazel/artifact_manifest.py` - normalized artifact manifest writer and signing mode vocabulary.
- `tools/bazel/artifact_metadata_compare.py` - artifact metadata comparison helper.
- `tools/bazel/artifact_rules.bzl` - Bazel release artifact rule surface.
- `tools/bazel/manifests/representative_products.json` - representative product matrix and artifact output expectations.
- `tools/bazel/phase3_artifacts.sh` - existing artifact verification dispatch.
- `tools/bazel/BUILD.bazel` - Bazel shell_binary wiring for phase verifiers and release artifacts.
- `BUILD.bazel` - root aliases and docs filegroups.
- `tools/bazel/rust_workflow.sh` - Rust/phase verifier dispatch pattern.
- `justfile` - developer facade recipes and existing phase verification entrypoints.

### Resource, auxiliary, and generated-output source evidence

- `tools/bazel/manifests/phase7_generated_outputs.json` - generated resource, package metadata, language, WUI, ESP, and package-output source refs.
- `tools/bazel/manifests/phase7_storage_media.json` - storage/media evidence boundary for release package outputs.
- `tools/bazel/manifests/phase10_auxiliary_build_update.json` - auxiliary build, update, prebuilt firmware, crash-dump, and release artifact boundaries.
- `tools/bazel/manifests/phase10_auxiliary_controllers.json` - Dwarf, ModularBed, xBuddy Extension, and MMU package rows.
- `.planning/codebase/INTEGRATIONS.md` - firmware artifacts, resources, CI, signing, credentials, and service integration context.
- `.planning/codebase/TESTING.md` - repo-native test, simulator, CTest, pytest, and CI verification surfaces.
- `.planning/codebase/CONCERNS.md` - release artifact, generated asset drift, signing, retained-code, and secret-handling concerns.
- `utils/build.py` - current firmware build and artifact staging wrapper.
- `utils/pack_fw.py` - current BBF packaging and signing-sensitive reference path.
- `utils/dfu.py` - current DFU generation reference path.
- `utils/translations_and_fonts/` - language/font/resource generation pipeline.
- `src/resources/` - packaged resources, WUI assets, ESP blobs, and firmware resource source tree.
- `lib/Prusa-Firmware-MMU/` - retained MMU firmware/package source.
- `src/puppy/` and `src/puppies/` - auxiliary-controller firmware and package surfaces.

### Repo and standards guidance

- `AGENTS.md` - repo-local GSD workflow and Bright Builds routing rules.
- `AGENTS.bright-builds.md` - managed Bright Builds workflow, sync, verification, and standards-routing rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `standards/core/architecture.md` - functional-core/imperative-shell and domain modeling guidance.
- `standards/core/code-shape.md` - early returns, `maybe_`, and size guidance.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit-test and Arrange/Act/Assert expectations.
- `standards/languages/rust.md` - Rust standards if Phase 17 adds or changes Rust domain types.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase16_live_network_evidence.py` and `tools/bazel/phase16_live_network_evidence_test.py` provide the nearest complete template for a phase-owned evidence contract, deterministic quick mode, operator input validation, path traversal guard, security/overclaim scan, generated artifacts, Bazel labels, and `just` facade wiring.
- `tools/bazel/phase15_hardware_evidence.py` and `tools/bazel/phase13_ci_evidence.py` provide additional evidence-runner patterns for external-input rows, artifact retention, redacted summaries, and CI-safe manifests.
- `tools/bazel/artifact_packager.py`, `tools/bazel/artifact_manifest.py`, `tools/bazel/artifact_metadata_compare.py`, `tools/bazel/artifact_rules.bzl`, and `tools/bazel/manifests/representative_products.json` already model representative release artifact outputs, metadata, package members, evidence classes, and signing modes.
- `tools/bazel/manifests/phase11_reference_comparisons.json` already has rows for product artifact metadata and release metadata comparison, including release-candidate artifact and signing-sensitive status boundaries.
- `tools/bazel/manifests/phase7_generated_outputs.json` and `tools/bazel/manifests/phase10_auxiliary_build_update.json` provide source-backed rows for resources, WUI assets, ESP blobs, language packages, MMU, and auxiliary firmware surfaces.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` already expose phase verifiers through the established Bazel and developer-command pattern.

### Established Patterns

- Checked-in JSON manifests define durable evidence contracts; generated run manifests, log references, normalized outputs, redacted summaries, and snapshots live under ignored `build/` paths.
- Phase verifiers use explicit constants for required IDs, required fields, source refs, generated output roots, forbidden markers, lifecycle IDs, status values, and wiring strings.
- Prior phases strictly separate local deterministic checks from simulator, hardware, live-service, release, signing, retained-code, and maintainer-review proof.
- Python verifier tests use stdlib `unittest`, temporary roots, explicit fixture writes/copies, and Arrange/Act/Assert comments.
- Artifact helpers already distinguish `unsigned-local`, `test-key`, `external-release-key`, and `not-applicable`; Phase 17 should use that vocabulary rather than inventing new signing labels.

### Integration Points

- Add Phase 17 release candidate evidence contract under `tools/bazel/manifests/`.
- Add Phase 17 verifier/collector and tests under `tools/bazel/`.
- Add Bazel labels in `tools/bazel/BUILD.bazel`, root aliases/docs filegroups in `BUILD.bazel`, dispatch cases in `tools/bazel/rust_workflow.sh`, and `just phase17-verify`.
- Use `.planning/phases/17-release-candidate-artifact-and-signing-gates/` for research, plan, summary, verification, and lifecycle artifacts.
- Keep generated Phase 17 evidence under `build/ci-evidence/phase17/` or explicit external artifact refs.

</code_context>

<specifics>
## Specific Ideas

- Maintainers should be able to answer "which release artifact surface failed, which requirement does it block, which reference evidence was compared, which signing/provenance evidence was supplied, which artifact proves it, and what residual risk remains" from the generated manifest alone.
- Phase 17 should provide release-operator evidence input modes so approved release-run artifacts and external signing evidence can be supplied later without changing the contract.
- The local `just phase17-verify` path should validate contracts, generated dry-run artifacts, redaction, overclaim guards, source refs, mismatch classification, signing/provenance semantics, and wiring while clearly marking release rows as pending release input when no release artifact is supplied.
- Do not mutate archived v1.0 artifacts. Cite archived evidence and layer Phase 17 release-candidate proof on top.
- Keep raw firmware package payloads, raw `.bin`/`.bbf`/`.dfu` bytes, private keys, signing-key values, private certificates, tokens, passwords, and release credentials out of committed source and planning artifacts.

</specifics>

<deferred>
## Deferred Ideas

- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
- Real production release approval, post-cutover release dashboards, broader artifact analytics, and vendor/HAL replacement belong to future milestones after the Phase 17 evidence contract exists and maintainers accept release-run inputs.

</deferred>

---

*Phase: 17-release-candidate-artifact-and-signing-gates*
*Context gathered: 2026-06-19*
