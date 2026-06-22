# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Rust Port Evidence Foundation

**Shipped:** 2026-06-15
**Phases:** 12 | **Plans:** 38 | **Tasks:** 81

### What Was Built

- Reference baseline, safety envelope, and known-concern ledger for the Rust rewrite.
- Bazel and `just` workflow foundation for build, generator, verifier, and artifact surfaces.
- Typed Rust evidence contracts for product profiles, runtime boundaries, printing, safety, storage/resources, GUI, network, and auxiliary-controller domains.
- Source-backed manifests, verifier scripts, regression tests, Bazel labels, and facade commands for subsystem parity evidence.
- Phase 11 cutover evidence that maps all 30 v1 requirements to local proof, retained-code posture, comparison rows, and named non-local blockers.
- Phase 12 evidence hygiene that reconciled planning metadata and preserved non-local gates without overclaiming local proof.

### What Worked

- Keeping non-local proof explicit prevented the local verifier from becoming a false cutover approval.
- Typed Rust domain contracts made evidence rows more precise than plain planning text.
- Small verifier scripts with negative tests caught stale status strings, bad evidence paths, and overclaim risks.
- Phase-level summaries and validation files gave the milestone audit enough structure to close metadata drift cleanly.

### What Was Inefficient

- Several source-backed proof slices needed later cleanup because early metadata and validation formats drifted across phases.
- Summary extraction produced noisy low-level review-fix items, so milestone history still needs human curation.
- Phase 2 and Phase 4 legacy validation metadata remains less complete than later Nyquist records, even though verification passed.

### Patterns Established

- Treat simulator, hardware, live-service, release-candidate, signing, retained-code acceptance, and maintainer approval as distinct evidence classes.
- Use manifest-backed verifier scripts as the durable bridge between planning requirements and enforceable build/review gates.
- Keep sensitive storage, credential, certificate, and payload evidence name-only unless a redacted fixture is deliberately created.
- Archive milestone requirements before deleting the live requirements file so the next milestone starts from a clean scope.

### Key Lessons

1. Local source-backed evidence is valuable, but it must name the exact non-local gate it does not satisfy.
2. Requirement traceability needs a verifier-readable owner and status for every row before milestone audit, not after.
3. Review and summary artifacts should separate user-visible accomplishments from low-level fix notes.
4. Future milestones should make CI, simulator, hardware, release, and maintainer-review gates executable as early as possible.

### Cost Observations

- Model mix: not measured in repo-local metadata.
- Sessions: multiple GSD phase sessions across 12 phases.
- Notable: deterministic local verifiers were cheap to rerun and made Phase 12 cleanup much safer than manual audit alone.

---

## Milestone: v1.1 — Cutover Evidence Hardening

**Shipped:** 2026-06-22
**Phases:** 10 | **Plans:** 13 | **Tasks:** 30

### What Was Built

- CI-owned aggregate cutover evidence workflow, manifest output, artifact retention, and Bazel/just verifier facades.
- Simulator, hardware/safety/media, live-service, and release-candidate evidence contracts with quick artifacts, explicit real-input paths, and no-overclaim guards.
- Release artifact identity backed by Phase 20 release-environment input and result manifests instead of an empty placeholder target.
- Retained-code and final cutover review gates that consume machine-readable upstream results and keep `demotion_allowed` blocked without valid inputs.
- Phase 22 reconciliation across requirements, validation metadata, roadmap state, and audit readiness, followed by a passed milestone audit rerun.

### What Worked

- Keeping quick evidence separate from real external proof prevented CI, smoke fixtures, and template rows from passing release or hardware gates.
- Reusing phase-owned contracts and small Python verifiers made later aggregation and audit reruns practical.
- Redaction, path-containment, and secret-field checks caught the most likely evidence-retention mistakes before artifacts could be trusted.
- The Phase 19/21/22 gap-closure sequence converted the audit findings into verifiable gates instead of prose-only assurances.

### What Was Inefficient

- Early v1.1 metadata still needed a dedicated reconciliation phase because requirement traceability, validation records, and roadmap progress drifted independently.
- Some milestone summaries pulled low-level review-fix notes into user-facing accomplishment lists, requiring manual curation at archive time.
- The evidence framework is now broad enough that future milestones should avoid adding more gate categories without first proving how they feed aggregate readiness.

### Patterns Established

- Represent external proof as pending input rows with strict schemas, artifact refs, and secret/path guards.
- Allow local quick modes to create reviewable scaffolding only when they cannot satisfy production evidence.
- Require final cutover decisions to consume upstream machine-readable results instead of trusting source-contract links alone.
- Run a source-backed audit readiness check before archival so the milestone audit can be rerun from durable evidence.

### Key Lessons

1. A checked requirement can mean "gate capability exists"; final cutover still needs separate evidence-result and approval inputs.
2. Aggregate evidence needs both retained artifacts and clear pending/blocked rows, otherwise external dependencies disappear from review.
3. Release identity targets must reject smoke proof and template rows explicitly; naming alone is not a sufficient guard.
4. Milestone archive summaries need curated engineering outcomes, not raw review-fix or audit-note lines.

### Cost Observations

- Model mix: not measured in repo-local metadata.
- Sessions: multiple GSD phase sessions across 10 phases.
- Notable: small verifier and manifest changes stayed cheap to rerun, but cross-phase metadata reconciliation carried a visible coordination cost.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | Multiple | 12 | Established source-backed parity evidence and archived a clean requirements/roadmap baseline. |
| v1.1 | Multiple | 10 | Converted non-local cutover blockers into durable evidence gates and archived a passed audit rerun. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Phase verifier suites plus 34 Phase 11 regression tests at archival | 30/30 v1 requirements mapped and complete | Standard-library verifier scripts and manifest checks for evidence gates. |
| v1.1 | Phase verifier suites plus aggregate, release, final-readiness, and metadata reconciliation tests | 18/18 v1.1 gate-capability requirements mapped and complete | Standard-library evidence contracts, redaction/path guards, result manifests, and audit-readiness checks. |

### Top Lessons (Verified Across Milestones)

1. Evidence status must distinguish local deterministic proof from non-local release approval.
2. Requirement, roadmap, validation, and manifest metadata should be reconciled before milestone archival, not after the next milestone starts.
3. Final cutover approval should consume upstream machine-readable results, not prose links to contract files.
