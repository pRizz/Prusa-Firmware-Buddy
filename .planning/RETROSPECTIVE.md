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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | Multiple | 12 | Established source-backed parity evidence and archived a clean requirements/roadmap baseline. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Phase verifier suites plus 34 Phase 11 regression tests at archival | 30/30 v1 requirements mapped and complete | Standard-library verifier scripts and manifest checks for evidence gates. |

### Top Lessons (Verified Across Milestones)

1. Evidence status must distinguish local deterministic proof from non-local release approval.
2. Requirement, roadmap, validation, and manifest metadata should be reconciled before milestone archival, not after the next milestone starts.
