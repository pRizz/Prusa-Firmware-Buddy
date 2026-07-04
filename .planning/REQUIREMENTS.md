# Requirements: Prusa Firmware Buddy Rust Port - v1.3 Cutover Approval and Reference Demotion Trial

**Defined:** 2026-07-02
**Core Value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

## v1.3 Requirements

These requirements consume the v1.2 evidence and decision machinery with real sanitized inputs. They do not redefine v1.0 parity contracts, expand v1.1 gate schemas, or perform post-cutover retained-code replacement unless a narrow blocker prevents the cutover decision.

### Evidence Intake

- [x] **INTAKE-01**: Maintainer can supply final simulator evidence packets for startup, G-code, GUI, storage, transfer, and selected failure flows using sanitized real-run inputs.
- [x] **INTAKE-02**: Maintainer can supply final hardware/media/safety evidence packets for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios.
- [x] **INTAKE-03**: Maintainer can supply final live-service evidence packets for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows.
- [x] **INTAKE-04**: Release manager can supply final release/signing/provenance evidence from real release-environment outputs without exposing private keys, tokens, certificates, service payloads, raw crash dumps, or other secret-bearing data.

### Evidence Triage

- [x] **TRIAGE-01**: Maintainer can aggregate all consumed simulator, hardware/media/safety, live-service, release/signing, upstream-result, retained-code, and readiness rows into a single blocker register.
- [x] **TRIAGE-02**: Maintainer can classify each failed, missing, stale, malformed, redaction-failed, or exceptioned row with owner, severity, affected gate, required next action, and decision impact.
- [x] **TRIAGE-03**: Maintainer can prove quick/default placeholder outputs, smoke fixtures, and local-only dry-run rows are rejected as final cutover proof.

### Maintainer Decisions

- [x] **DECIDE-01**: Maintainer can record retained-code acceptance, rejection, or approved exception decisions with residual-risk rationale and owner signoff.
- [x] **DECIDE-02**: Maintainer can record final-readiness approval or block decisions using machine-readable inputs that consume the triaged evidence rows and approved exceptions.
- [x] **DECIDE-03**: Maintainer can record reference-demotion approval or rejection as a separate explicit decision that cannot be inferred from green evidence alone.

### Readiness and Demotion Trial

- [ ] **READY-01**: Maintainer can generate a final readiness packet from real consumed evidence rows, retained-code decisions, approved exceptions, residual risks, blockers, and artifact references.
- [ ] **READY-02**: Final readiness remains blocked when required evidence is absent, failed, stale, malformed, redaction-failed, underclassified, or not covered by an explicit approved exception.
- [ ] **READY-03**: Reference-demotion dry run proves demotion remains blocked without a valid explicit demotion approval and opens only when readiness is otherwise unblocked and the approval input is valid.

### Cutover Decision

- [ ] **CUTOVER-01**: Maintainer can produce a cutover decision artifact with one explicit verdict: approved, blocked, or approved with explicit exceptions.
- [ ] **CUTOVER-02**: Cutover decision artifact links every blocker, exception, residual risk, evidence packet, retained-code decision, readiness result, and demotion decision needed to audit the verdict.
- [ ] **CUTOVER-03**: Cutover decision artifact routes the next milestone to production cutover when approved, or to targeted blocker repair when blocked or approved with exceptions that require follow-up.

## Future Requirements

Deferred to later milestones.

### Post-Cutover Execution and Hardening

- **POST-01**: Maintainer can execute production reference demotion after v1.3 produces an approved cutover decision.
- **POST-02**: Maintainer can replace retained vendor, HAL, or upstream components with Rust alternatives after cutover evidence shows replacement risk is lower than retention risk.
- **POST-03**: Maintainer can add long-run soak dashboards and trend analytics after durable hardware and simulator evidence exists.
- **POST-04**: Maintainer can expand printer UX or firmware behavior beyond parity after the Rust+Bazel firmware is accepted as the production baseline.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Automatic reference demotion | Reference demotion requires a separate explicit maintainer decision even when all evidence is green. |
| New printer UX or firmware behavior | v1.3 is a cutover approval trial, not new product development. |
| Broad redesign of v1.0 parity contracts or v1.1/v1.2 evidence schemas | The milestone should consume existing evidence machinery unless a failed real row exposes a narrow defect that blocks the decision. |
| Replacing retained vendor, HAL, or upstream code as general hardening | Replacement belongs after a cutover decision or a concrete decision-blocking defect. |
| Long-run dashboards and trend analytics | Valuable after durable evidence exists, but not required to produce the first go/no-go decision. |
| Committing private signing keys, tokens, certificates, service payloads, raw crash dumps, or other secret-bearing artifacts | Evidence must remain secret-safe and reviewable through sanitized artifacts or external references. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INTAKE-01 | Phase 31 | Complete |
| INTAKE-02 | Phase 31 | Complete |
| INTAKE-03 | Phase 31 | Complete |
| INTAKE-04 | Phase 31 | Complete |
| TRIAGE-01 | Phase 32 | Complete |
| TRIAGE-02 | Phase 32 | Complete |
| TRIAGE-03 | Phase 32 | Complete |
| DECIDE-01 | Phase 33 | Complete |
| DECIDE-02 | Phase 33 | Complete |
| DECIDE-03 | Phase 33 | Complete |
| READY-01 | Phase 34 | Pending |
| READY-02 | Phase 34 | Pending |
| READY-03 | Phase 34 | Pending |
| CUTOVER-01 | Phase 35 | Pending |
| CUTOVER-02 | Phase 35 | Pending |
| CUTOVER-03 | Phase 35 | Pending |

**Coverage:**

- v1.3 requirements: 16 total
- Mapped to phases: 16
- Complete: 10
- Pending: 6
- Unmapped: 0
- Duplicate mappings: 0

______________________________________________________________________

*Requirements defined: 2026-07-02*
*Last updated: 2026-07-04 after Phase 33 completion*
