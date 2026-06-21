# Requirements: Prusa Firmware Buddy Rust Port — v1.1 Cutover Evidence Hardening

**Defined:** 2026-06-15
**Core Value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

## v1.1 Requirements

These requirements convert the non-local v1.0 cutover blockers into durable evidence gates. They do not redefine the v1.0 parity contracts archived in `.planning/milestones/v1.0-REQUIREMENTS.md`.

### CI Evidence

- [x] **CIEV-01**: Maintainer can run the aggregate cutover verifier in CI for every pull request that changes Rust, Bazel, verifier, manifest, or release-evidence surfaces.
- [x] **CIEV-02**: Maintainer can inspect a machine-readable CI evidence manifest that records gate status, owning phase, command, artifact path, and failure reason for each cutover gate.
- [x] **CIEV-03**: Maintainer can download retained CI artifacts for verifier logs, manifest snapshots, normalized comparison outputs, and redacted evidence summaries without relying on local workspace state.

### Simulator Evidence

- [x] **SIM-01**: Maintainer can run simulator evidence flows for startup, task readiness, watchdog-visible startup behavior, and representative G-code execution against the Rust+Bazel evidence surface.
- [x] **SIM-02**: Maintainer can run simulator evidence flows for GUI navigation, storage/resource access, transfers, and selected failure flows with reference-compatible pass/fail semantics.
- [ ] **SIM-03**: Maintainer can map simulator evidence results back to the v1.0 requirement IDs and cutover criteria without marking hardware-only behavior as simulator-proven.

### Hardware and Safety Evidence

- [x] **HARD-01**: Maintainer can execute a hardware smoke matrix for supported printer families, boards, storage media, and auxiliary-controller combinations required for cutover readiness.
- [x] **HARD-02**: Maintainer can record hardware safety evidence for watchdog, thermal/motion safety, emergency stop, safe-output, crash recovery, UI input, MMU, RS485, and toolchanger scenarios.
- [x] **HARD-03**: Maintainer can review hardware evidence artifacts that identify device, firmware build, operator, timestamp, scenario, result, and residual risk without exposing secrets or unsafe operational data.

### Live Network Evidence

- [x] **LIVE-01**: Maintainer can run live or controlled-service evidence for Prusa Connect registration, telemetry, WebSocket commands, token/fingerprint behavior, and proxy limitations.
- [x] **LIVE-02**: Maintainer can run live or controlled-service evidence for PrusaLink/WUI HTTP API, digest/API-key auth, SNTP, mDNS, syslog, metrics, and transfer behavior.
- [x] **LIVE-03**: Maintainer can verify TLS, certificate, credential-redaction, negative protocol, long-transfer, and crash-dump upload evidence without committing secrets, tokens, or private certificates.

### Release Candidate Evidence

- [x] **REL-01**: Release manager can build release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, and auxiliary firmware artifacts through Bazel-owned workflows.
- [x] **REL-02**: Release manager can verify release-candidate signing, provenance, build input identity, and artifact retention while keeping private signing keys outside the repository and planning artifacts.
- [x] **REL-03**: Maintainer can compare release-candidate artifact surfaces against the archived v1.0 reference evidence and classify every mismatch as pass, intentional delta, blocker, or deferred retained-code issue.

### Cutover Review

- [x] **REV-01**: Maintainer can review retained-code acceptance packets for every C, C++, ASM, generated, vendor, HAL, RTOS, network, filesystem, and signing surface that remains at cutover.
- [ ] **REV-02**: Maintainer can approve or reject final reference-demotion criteria through an explicit checklist that links CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence.
- [ ] **REV-03**: Maintainer can produce a final cutover readiness report that marks reference demotion allowed only when all required gates pass or have documented maintainer-approved exceptions.

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
| New printer UX or firmware behavior | v1.1 is evidence hardening; new behavior would obscure cutover approval. |
| Final reference demotion without maintainer approval | The milestone creates reviewable gates; actual demotion remains gated by pass evidence and approval. |
| Committing private signing keys, tokens, certificates, or service secrets | Evidence artifacts must remain redacted and reproducible without secret leakage. |
| Replacing retained third-party code solely for cleanup | v1.1 records acceptance or blockers; replacement belongs to post-cutover or separately scoped work. |
| Treating simulator evidence as hardware evidence | Hardware-only safety and media behavior must remain separately classified. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CIEV-01 | Phase 19 | Complete |
| CIEV-02 | Phase 19 | Complete |
| CIEV-03 | Phase 19 | Complete |
| SIM-01 | Phase 19 | Complete |
| SIM-02 | Phase 19 | Complete |
| SIM-03 | Phase 14 | Pending |
| HARD-01 | Phase 19 | Complete |
| HARD-02 | Phase 19 | Complete |
| HARD-03 | Phase 19 | Complete |
| LIVE-01 | Phase 19 | Complete |
| LIVE-02 | Phase 19 | Complete |
| LIVE-03 | Phase 19 | Complete |
| REL-01 | Phase 20 | Complete |
| REL-02 | Phase 20 | Complete |
| REL-03 | Phase 20 | Complete |
| REV-01 | Phase 18 | Complete |
| REV-02 | Phase 21 | Pending |
| REV-03 | Phase 21 | Pending |

**Coverage:**

- v1.1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0

______________________________________________________________________

*Requirements defined: 2026-06-15*
*Last updated: 2026-06-21 after v1.1 milestone audit gap planning*
