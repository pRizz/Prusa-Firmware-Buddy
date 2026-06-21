---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 20-2026-06-21T12-40-17
generated_at: 2026-06-21T12:45:35.072Z
---

# Phase 20: Release Candidate Artifact Production - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Replace the empty `//tools/bazel:phase17_release_candidate_artifacts` release identity with a production-safe release artifact surface that can represent real release-candidate firmware, resource, signing, provenance, retention, and comparison outputs. This phase closes the REL-01/REL-02/REL-03 gap identified by the v1.1 audit without treating representative smoke fixtures, dry-run summaries, or local placeholder evidence as production release proof.

</domain>

<decisions>
## Implementation Decisions

### Artifact Identity Target

- **D-01:** Replace the empty `tools/bazel/BUILD.bazel` `phase17_release_candidate_artifacts` filegroup with a non-empty release identity that resolves to production-safe release outputs or explicit release-environment input artifacts.
- **D-02:** Prefer a hybrid release identity: Bazel should own the artifact identity and any locally producible unsigned or metadata outputs, while private signing and release-only infrastructure remain represented through explicit release-environment input manifests.
- **D-03:** Do not make representative smoke fixtures production evidence. `phase17_representative_release_smoke`, `representative_release_artifacts`, `phase3_verify`, and other local smoke labels stay separate and must remain rejected as sources for `phase17_release_candidate_artifacts`.
- **D-04:** The release identity should cover the surfaces already named by Phase 17: `.bin`, `.bbf`, `.dfu`, map/provenance, resource image/package, language bundle, WUI assets, ESP package, MMU package, Dwarf firmware, ModularBed firmware, xBuddy Extension firmware, package manifest, signing summary, provenance summary, retention manifest, and comparison report.

### Production Proof Boundary

- **D-05:** Add Phase 20-owned contract and verifier logic that distinguishes production release evidence from smoke evidence through explicit proof classes such as release candidate, approved release run, external release key evidence, local smoke, and placeholder.
- **D-06:** Local deterministic verification may validate schemas, target wiring, generated input templates, path guards, redaction guards, and placeholder handling, but it must not mark release rows passed unless real release outputs or approved release-environment inputs are supplied.
- **D-07:** Verifier tests must prove that smoke labels, empty filegroups, generated dry-run placeholders, and local representative products cannot satisfy `REL-01`, `REL-02`, or `REL-03`.
- **D-08:** Generated Phase 20 runtime artifacts should live under `build/ci-evidence/phase20/`; checked-in source should define contracts, verifier logic, templates, target wiring, and regression tests only.

### Signing, Provenance, and Comparison Metadata

- **D-09:** Keep the repo-native JSON contract and Python standard-library verifier as the authoritative evidence shape. Use attestation-style field names for subject digests, build input identity, builder command, run identity, key identity reference, and verification outcome, but do not introduce a new external attestation trust root in this phase.
- **D-10:** Signing evidence records public key identity or fingerprint, signing mode, artifact digest, build input identity, retention refs, timestamp, operator or release-run ID, and verification outcome. It must never record private keys, raw key bytes, private certificates, signing payload bytes, tokens, passwords, raw firmware payloads, or credential-bearing values.
- **D-11:** Provenance evidence should tie every retained artifact ref to the `//tools/bazel:phase17_release_candidate_artifacts` identity, build inputs, product/printer/board/MCU/bootloader metadata, source manifest refs, and artifact hashes.
- **D-12:** Comparison evidence should classify every archived-reference mismatch as exactly one of `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue`, with a reason, owner phase, affected artifact surface, and residual risk.

### Aggregate and Final-Review Integration

- **D-13:** Phase 20 owns the release result manifest. Phase 19 may retain or index Phase 20 artifacts, and Phase 21 should consume Phase 20 result manifests as upstream release evidence before final readiness can pass.
- **D-14:** Do not make Phase 19 the authority for release pass/fail semantics. Aggregate CI can retain logs, snapshots, result manifests, and placeholders, but Phase 20's release result manifest remains the source of truth for release-candidate production status.
- **D-15:** Update wiring only as needed for discoverability and retention: Bazel labels, root aliases/docs filegroups, `tools/bazel/rust_workflow.sh`, `just phase20-verify`, and any Phase 19 index hook should point at Phase 20 artifacts without converting pending external release proof into a pass claim.
- **D-16:** Leave final readiness policy to Phase 21. Phase 20 should produce machine-readable release evidence that Phase 21 can validate, including passed, pending, blocked, failed, rejected-redaction, and rejected-overclaim states.

### the agent's Discretion

- Exact file names, schema field order, status spelling, target/macro names, generated artifact names, and helper boundaries are flexible if the result is deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated plan if the change remains cohesive. Split only if release identity, verifier, and integration work become too large for one clean execution pass.
- Prefer small JSON manifests, standard-library Python, targeted Bazel wiring, and focused unit tests over broad release automation rewrites.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and audit gap

- `.planning/ROADMAP.md` - Phase 20 goal, dependencies, success criteria, and gap-closure text.
- `.planning/REQUIREMENTS.md` - `REL-01`, `REL-02`, and `REL-03` release-candidate evidence requirements.
- `.planning/STATE.md` - current milestone state, blockers, and release/signing concerns.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, and Bright Builds constraints.
- `.planning/v1.1-MILESTONE-AUDIT.md` - audit finding that `phase17_release_candidate_artifacts` is empty and no real release output flows into final review.

### Prior phase decisions and verification

- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md` - release artifact matrix, signing/provenance hygiene, comparison taxonomy, smoke separation, and Phase 17 workflow identity.
- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md` - passed Phase 17 verification and the remaining release artifact limitation.
- `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-CONTEXT.md` - final review evidence inputs, demotion guard, and release row links.
- `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VERIFICATION.md` - passed Phase 18 verification and upstream result-manifest gap.
- `.planning/phases/19-aggregate-cutover-evidence-ci/19-CONTEXT.md` - aggregate CI retention, no-overclaim semantics, and Phase 20 out-of-scope boundary.
- `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md` - passed Phase 19 verification and retained Phase 17 pending release input.

### Existing release, verifier, and artifact surfaces

- `tools/bazel/BUILD.bazel` - empty `phase17_release_candidate_artifacts`, smoke target separation, Phase 17-19 verifier labels, and representative release artifact rules.
- `BUILD.bazel` - root alias for `phase17_release_candidate_artifacts` and phase docs/verification facade pattern.
- `tools/bazel/rust_workflow.sh` - phase verifier dispatch pattern to extend with Phase 20.
- `justfile` - developer facade pattern and existing `phase17-verify`, `phase17-release-artifacts-smoke`, and `phase19-verify` recipes.
- `tools/bazel/phase17_release_candidate_evidence.py` - release contract verifier, workflow identity validation, redaction guards, source-ref validation, and smoke rejection behavior.
- `tools/bazel/phase17_release_candidate_evidence_test.py` - regression tests for wiring order, missing release label, and smoke-target rejection.
- `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - release rows, required artifact outputs, release input schema, status vocabulary, signing/provenance/comparison fields, and local smoke identities.
- `tools/bazel/phase19_aggregate_ci_evidence.py` - aggregate artifact retention, expected artifact enforcement, external input placeholders, and status collection.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - current Phase 14-18 aggregate retention and pending release input model.
- `.github/workflows/ci-evidence.yml` - thin CI wrapper that uploads generated evidence bundles.

### Release package reference paths

- `tools/bazel/artifact_rules.bzl` - existing representative artifact rule and output naming pattern.
- `tools/bazel/artifact_manifest.py` - normalized artifact manifest fields, evidence classes, signing modes, and digest generation.
- `tools/bazel/artifact_packager.py` - current package-surface artifact helper and BBF/DFU generation boundary.
- `tools/bazel/artifact_metadata_compare.py` - artifact metadata comparison helper.
- `tools/bazel/manifests/representative_products.json` - representative product matrix and artifact output expectations.
- `utils/build.py` - current firmware build and artifact staging wrapper.
- `utils/pack_fw.py` - BBF packaging and signing-sensitive reference path.
- `utils/dfu.py` - DFU generation reference path.
- `ProjectOptions.cmake` - supported printer, board, MCU, bootloader, and feature option matrix.

### Standards and repo guidance

- `AGENTS.md` - repo-local GSD and Bright Builds workflow rules.
- `AGENTS.bright-builds.md` - managed Bright Builds sync, verification, and standards-routing rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `standards/core/architecture.md` - functional-core/imperative-shell and domain modeling guidance.
- `standards/core/code-shape.md` - early returns, `maybe_`, and size guidance.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit-test and Arrange/Act/Assert expectations.
- `standards/languages/rust.md` - Rust standards if Phase 20 adds or changes Rust domain types.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase17_release_candidate_evidence.py` already defines required release surfaces, release input fields, status vocabulary, forbidden secret/payload markers, workflow identity validation, and smoke-label rejection.
- `tools/bazel/phase17_release_candidate_evidence_test.py` already proves the Phase 17 verifier rejects a release-candidate target that wraps `:representative_release_artifacts`.
- `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` already names the artifact outputs and metadata expected from a production release run.
- `tools/bazel/phase19_aggregate_ci_evidence.py` already copies expected phase artifacts into an aggregate evidence bundle and marks missing artifacts as failures.
- `tools/bazel/artifact_rules.bzl`, `artifact_packager.py`, `artifact_manifest.py`, and `artifact_metadata_compare.py` provide existing package, manifest, digest, and comparison helpers that can be reused or mirrored.

### Established Patterns

- Checked-in JSON contracts define evidence authority; generated run manifests, summaries, source snapshots, operator templates, and logs stay under ignored `build/ci-evidence/phaseXX` paths.
- Prior verifiers use explicit constants for required row IDs, required fields, output roots, source refs, forbidden markers, status vocabularies, and wiring strings.
- Prior phases strictly separate local deterministic checks from simulator, hardware, live-service, release, signing, retained-code, and maintainer-review proof.
- Python tests use standard-library `unittest`, temporary repo roots, explicit fixture writes, and Arrange/Act/Assert comments.

### Integration Points

- Update `tools/bazel/BUILD.bazel` so `phase17_release_candidate_artifacts` is non-empty and production-safe, and add Phase 20 verifier/test labels if the plan creates a Phase 20 verifier.
- Update root `BUILD.bazel` with Phase 20 docs and verification aliases.
- Update `tools/bazel/rust_workflow.sh` and `justfile` with `phase20_verify` / `phase20-verify` entrypoints.
- Add a Phase 20 checked-in contract and verifier under `tools/bazel/manifests/` and `tools/bazel/` if needed to enforce the new release identity and result manifest.
- Generate runtime evidence under `build/ci-evidence/phase20/`, with optional Phase 19 retention/indexing of Phase 20 outputs.

</code_context>

<specifics>
## Specific Ideas

- Release managers should be able to answer which artifact surface was produced or supplied, which requirement it satisfies, which Bazel identity owns it, which build inputs and artifact digests were recorded, which signing key identity was used, where the retained evidence lives, and how every reference mismatch was classified.
- Private signing material remains outside the repo. Evidence should use key identity, fingerprint, external artifact refs, and verification outcomes instead of key bytes or payload copies.
- Local smoke products remain useful for testing packaging mechanics, but they should be visibly named as smoke evidence and never flow into the production release identity.
- A future Phase 21 final-readiness workflow should be able to consume Phase 20 result manifests without reinterpreting prose or trusting external refs blindly.

</specifics>

<deferred>
## Deferred Ideas

- Full native Rust/Bazel release package graph can be expanded after this phase if the pragmatic Phase 20 path uses wrapped current release tooling or explicit release-environment inputs.
- External attestation tooling, SBOM export, and supply-chain policy engines can be added later if release governance requires them; Phase 20 should not add a new trust root unless the local evidence contract needs it.
- Final reference-demotion policy remains Phase 21 scope.

</deferred>

---

*Phase: 20-release-candidate-artifact-production*
*Context gathered: 2026-06-21*
