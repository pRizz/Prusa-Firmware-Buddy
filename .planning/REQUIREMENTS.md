# Requirements: Prusa Firmware Buddy Rust Port — v1.2 Cutover Evidence Execution and Acceptance

**Defined:** 2026-06-23
**Core Value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

## v1.2 Requirements

These requirements execute the real external evidence and acceptance flows created in v1.1. They do not redefine the v1.0 parity contracts or v1.1 gate-capability contracts.

### Evidence Execution

- [x] **EVID-01**: Maintainer can supply real simulator evidence results for startup, G-code, GUI, storage, transfer, and selected failure flows.
- [ ] **EVID-02**: Maintainer can supply real hardware/media/safety evidence for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios.
- [ ] **EVID-03**: Maintainer can supply real live-service evidence for Connect, WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows.
- [ ] **EVID-04**: Release manager can supply release/signing/provenance evidence from real release-environment outputs without exposing private keys or secrets.

### Acceptance Decisions

- [ ] **ACPT-01**: Maintainer can review upstream result rows for every required cutover gate.
- [ ] **ACPT-02**: Maintainer can accept, reject, or exception retained-code packets with residual-risk rationale.
- [ ] **ACPT-03**: Maintainer can approve or block final readiness using machine-readable decision inputs.

### Final Readiness

- [ ] **READ-01**: Maintainer can generate a final cutover readiness packet that links all external evidence, acceptance decisions, exceptions, and residual risks.
- [ ] **READ-02**: Final readiness remains blocked by default unless all required evidence passes or has explicit approved exceptions.
- [ ] **READ-03**: Reference demotion remains a separate explicit maintainer approval and is not automatic.

## Future Requirements

Deferred to later milestones.

### Post-Cutover Hardening

- **FUT-01**: Maintainer can replace retained vendor or HAL components with Rust alternatives after cutover evidence shows replacement risk is lower than retention risk.
- **FUT-02**: Maintainer can add long-run soak dashboards and trend analytics after first durable hardware and simulator gates exist.
- **FUT-03**: Maintainer can expand printer UX or firmware behavior beyond parity after the Rust+Bazel firmware is accepted as the production baseline.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Automatic reference demotion | Final demotion requires explicit maintainer approval even when evidence is green. |
| New printer UX or firmware behavior | v1.2 executes cutover evidence and acceptance, not new feature development. |
| Redefining v1.0 parity contracts | v1.0 is the archived behavior baseline; this milestone supplies external proof and decisions. |
| Reworking v1.1 gate schemas without a failed evidence row | The default posture is execution, not another framework-hardening milestone. |
| Committing private signing keys, tokens, certificates, service payloads, or crash dumps | Evidence must remain secret-safe and reviewable through sanitized artifacts or external references. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| EVID-01 | Phase 23 | Complete |
| EVID-02 | Phase 24 | Pending |
| EVID-03 | Phase 25 | Pending |
| EVID-04 | Phase 26 | Pending |
| ACPT-01 | Phase 26 | Pending |
| ACPT-02 | Phase 27 | Pending |
| ACPT-03 | Phase 27 | Pending |
| READ-01 | Phase 28 | Pending |
| READ-02 | Phase 28 | Pending |
| READ-03 | Phase 28 | Pending |

**Coverage:**

- v1.2 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0
- Duplicate mappings: 0

______________________________________________________________________

*Requirements defined: 2026-06-23*
*Last updated: 2026-06-23 after Phase 23 completion*
