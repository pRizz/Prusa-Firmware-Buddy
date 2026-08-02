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

## Milestone: v1.2 — Cutover Evidence Execution and Acceptance

**Shipped:** 2026-07-02
**Phases:** 8 | **Plans:** 9 | **Tasks:** 9 task groups

### What Was Built

- Simulator, hardware/media/safety, and live-service evidence execution contracts that validate real operator packets while keeping quick outputs blocked placeholders.
- Release/signing/provenance evidence handling and canonical upstream result rows for every cutover gate.
- Retained-code acceptance, residual-risk, exception, and final-readiness decision inputs with hard-blocker precedence and secret-safe retained outputs.
- Final readiness packet generation that links upstream rows, decisions, exceptions, residual risks, blockers, and artifact refs.
- Upstream evidence flow closure from Phase 23-25 rows through Phase 26 into Phase 28 readiness packets.
- Requirement-neutral metadata cleanup that reconciled summary extraction, validation metadata, Phase 25 verification shape, state metadata, and the v1.2 milestone audit.

### What Worked

- Separating quick/default placeholders from real evidence packets prevented local verifier runs from becoming false release approval.
- Carrying upstream rows through Phase 26 and Phase 28 made cross-phase evidence flow inspectable instead of prose-only.
- Machine-readable maintainer inputs kept retained-code acceptance, final readiness, exceptions, residual risk, and reference demotion as explicit decisions.
- The Phase 30 metadata pass caught audit and summary-extraction drift before archival.

### What Was Inefficient

- v1.2 still needed a dedicated Phase 30 because helper extraction keys, validation metadata, state prose, and audit wording drifted across phases.
- The milestone entry auto-extractor pulled one low-level review note into accomplishments, which required manual archive curation.
- Real external evidence remains outside the repository, so the milestone proves execution surfaces and fail-closed behavior rather than final production approval.

### Patterns Established

- Treat evidence execution as retained input proof with strict schema, artifact, source-ref, redaction, and lifecycle validation.
- Preserve final readiness as an aggregation and decision surface, not a replacement for maintainer approval.
- Keep reference demotion separate from readiness and blocked unless explicit valid demotion input is supplied after readiness is otherwise unblocked.
- Run a final metadata cleanup and audit refresh before milestone archival when many phase artifacts evolved independently.

### Key Lessons

1. Cross-phase evidence rows need first-class tests and archive evidence; otherwise old pending defaults can hide real upstream state.
2. Summary metadata should expose a stable machine-readable completion key from the start of a milestone.
3. Milestone archive generation still needs human curation for accomplishments and project evolution sections.
4. Final cutover remains a decision process: even complete evidence plumbing must not imply reference demotion approval.

### Cost Observations

- Model mix: not measured in repo-local metadata.
- Sessions: multiple GSD phase sessions across 8 phases.
- Notable: verifier code stayed deterministic and cheap to reason about, but full pre-commit Rust verification remains expensive enough to plan around milestone commits.

---

## Milestone: v1.3 — Cutover Approval and Reference Demotion Trial

**Shipped:** 2026-08-02
**Phases:** 11 | **Plans:** 37 | **Tasks:** 86

### What Was Built

- Secret-safe final evidence intake over simulator, hardware/media/safety, live-service, and release/signing packets.
- A canonical blocker register and explicit retained-code, residual-risk, exception, readiness, and reference-demotion decision inputs.
- Exact typed decision reconciliation into a readiness ledger that rejects stale, ambiguous, conflicting, malformed, and hard-blocker authority.
- Attempt-correlated Phase 34/35 publication that replaces stale approval with durable blocked authority on every upstream or installation failure.
- A completed file-length campaign covering 92 oversized owned files, with exactly 841 permanent exceptions and zero managed findings.
- Terminal roadmap, requirements, state, inventory, Nyquist, verification, and audit consistency enforced by a pure policy and bounded adapters.

### What Worked

- Exact typed identities prevented similar-looking evidence or decisions from authorizing the wrong blocker row.
- Publishing blocking authority before payloads made failed cutover attempts safe without misreporting operational success.
- Keeping raw filesystem and Markdown parsing outside pure policies made mutation testing comprehensive and diagnostics deterministic.
- The shrink-only file-length ledger allowed a large refactor campaign to converge without broadening exceptions.
- Independent verification followed by a fresher audit and pre-archive rerun produced a trustworthy terminal handoff.

### What Was Inefficient

- Initial Phase 41 verification exposed three terminal projections that the first checker version did not independently parse, requiring Plan 41-04.
- Summary one-line extraction still surfaced low-level review-fix notes, so milestone accomplishments required manual curation.
- Five summaries lacked explicit task totals; exact milestone statistics had to be derived from the 37 PLAN task blocks.
- The milestone completion helper could not update one customized STATE field automatically, requiring a bounded manual state refresh.
- The 280-commit, 580-file change range made archive review and final verification materially heavier than earlier milestones.

### Patterns Established

- Parse terminal planning projections once into immutable records before applying one pure fail-closed policy.
- Use isolated mutation probes for every duplicated count, status, inventory, freshness, and authority projection.
- Publish safe blocking authority first and correlate every subsequent artifact to the exact workflow attempt.
- Treat plan task blocks as the task-count authority when summary metadata is incomplete.
- Require independent verification, a newer audit, and a final pre-archive pass in that order.

### Key Lessons

1. Terminal metadata must be verified as behavior, not trusted because each document looks plausible in isolation.
2. Exact identity and attempt correlation are reusable defenses against stale or adjacent authorization.
3. Large refactor campaigns need monotonic ledgers and stable public facades to remain reviewable.
4. Archive generators need curated accomplishment and task-count inputs even when the underlying lifecycle data is complete.
5. Production cutover and reference demotion remain decisions; complete evidence machinery cannot authorize either by implication.

### Cost Observations

- Model mix: not measured in repo-local metadata.
- Sessions: multiple GSD phase sessions across 11 phases.
- Notable: 280 commits over 30 elapsed days changed 580 files; deterministic focused suites and terminal consistency checks kept the archive boundary auditable despite the scale.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | Multiple | 12 | Established source-backed parity evidence and archived a clean requirements/roadmap baseline. |
| v1.1 | Multiple | 10 | Converted non-local cutover blockers into durable evidence gates and archived a passed audit rerun. |
| v1.2 | Multiple | 8 | Executed evidence and acceptance flows, closed upstream row propagation into final readiness, and archived a passed audit. |
| v1.3 | Multiple | 11 | Reconciled real evidence and explicit decisions into fail-closed cutover routing, eliminated temporary file-length debt, and enforced terminal metadata coherence. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Phase verifier suites plus 34 Phase 11 regression tests at archival | 30/30 v1 requirements mapped and complete | Standard-library verifier scripts and manifest checks for evidence gates. |
| v1.1 | Phase verifier suites plus aggregate, release, final-readiness, and metadata reconciliation tests | 18/18 v1.1 gate-capability requirements mapped and complete | Standard-library evidence contracts, redaction/path guards, result manifests, and audit-readiness checks. |
| v1.2 | Phase verifier suites plus focused Phase 23-29 evidence, decision, final-readiness, and metadata cleanup checks | 10/10 v1.2 execution and acceptance requirements mapped and complete | Standard-library evidence execution validators, retained output writers, upstream row ingestion, and final readiness packet generation. |
| v1.3 | 96 Phase 41 tests, 323 cross-phase audit tests, 136 Rust tests, and six Bazel terminal targets at archival | 16/16 v1.3 requirements coherent with 11/11 phases and 37/37 plan summaries | Standard-library typed adapters, pure terminal policy, mutation probes, and attempt-correlated authority checks. |

### Top Lessons (Verified Across Milestones)

1. Evidence status must distinguish local deterministic proof from non-local release approval.
2. Requirement, roadmap, validation, and manifest metadata should be reconciled before milestone archival, not after the next milestone starts.
3. Final cutover approval should consume upstream machine-readable results, not prose links to contract files.
4. Milestone archive summaries need curated outcome language because raw extractors can surface implementation-detail bug notes.
5. Terminal planning projections need isolated mutation tests and enforced verification/audit freshness ordering.
