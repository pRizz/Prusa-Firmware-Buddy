---
phase: 11
slug: parity-pyramid-and-cutover-evidence
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-14
phase_lifecycle_id: 11-2026-06-14T18-48-49
lifecycle_mode: yolo
---

# Phase 11 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib verifier tests plus Bazel `shell_binary` labels plus existing Rust workflow checks |
| **Config file** | `.planning/config.json`, `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `justfile`, and `Cargo.toml` |
| **Quick run command** | `python3 tools/bazel/phase11_verify.py --quick` |
| **Full suite command** | `just phase11-verify` |
| **Estimated runtime** | ~90 seconds for local deterministic checks after Bazel and Rust caches are warm |

---

## Sampling Rate

- **After every task commit:** Run the most focused Phase 11 verifier mode for the touched manifest or verifier path; run affected Rust checks when `rust/crates/domain` changes.
- **After every plan wave:** Run `python3 tools/bazel/phase11_verify_test.py`, `python3 tools/bazel/phase11_verify.py --quick`, and affected Rust checks when Rust domain files changed.
- **Before phase verification:** `just phase11-verify` must be green, lifecycle validation must pass, and simulator, hardware, manual, live network, release-candidate, and reference-demotion evidence must remain outside local green claims unless actual artifacts exist.
- **Max feedback latency:** 120 seconds for local deterministic checks after tool caches are warm.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 11-01 | 1 | VERF-01 | T-11-01-01..T-11-01-05 | Parity pyramid rows name proof scope and do not claim local proof for simulator, hardware, manual, or retained-code-only evidence | manifest/source audit | `python3 tools/bazel/phase11_verify.py --pyramid-only` | no - W0 | pending |
| 11-02-01 | 11-02 | 2 | VERF-04 | T-11-02-01..T-11-02-05 | Every v1 requirement is mapped to source artifacts, status, intentional-delta state, and any non-local blocker | manifest/source audit | `python3 tools/bazel/phase11_verify.py --requirements-only` | no - W0 | pending |
| 11-03-01 | 11-03 | 2 | VERF-03 | T-11-03-01..T-11-03-05 | Reference comparison rows use normalized semantic comparisons unless byte identity has a named fixture and normalization rule | manifest/source audit | `python3 tools/bazel/phase11_verify.py --comparison-only` | no - W0 | pending |
| 11-03-02 | 11-03 | 2 | VERF-01, VERF-03 | T-11-03-01..T-11-03-05 | Optional Rust evidence contracts reject invalid proof scopes, statuses, and comparison contracts without unsafe code | Rust unit/API check | `python3 tools/bazel/phase11_verify.py --rust-only` | no - W0 | pending |
| 11-04-01 | 11-04 | 3 | VERF-04, VERF-05 | T-11-04-01..T-11-04-06 | Cutover readiness stays blocked until local gates pass, non-local evidence is named, retained code is justified, and overclaim scans are clean | manifest/security audit | `python3 tools/bazel/phase11_verify.py --cutover-only --security-only` | no - W0 | pending |
| 11-05-01 | 11-05 | 4 | VERF-01, VERF-03, VERF-04, VERF-05 | T-11-05-01..T-11-05-05 | Bazel labels, root aliases, and `just phase11-verify` expose deterministic Phase 11 verification with tests before aggregate verification | build graph smoke | `python3 tools/bazel/phase11_verify.py --wiring-only` | no - W0 | pending |
| 11-05-02 | 11-05 | 4 | VERF-01, VERF-03, VERF-04, VERF-05 | T-11-05-01..T-11-05-05 | Aggregate verifier, validation, and lifecycle checks prove local evidence while preserving non-local cutover blockers | aggregate verifier | `just phase11-verify` | no - W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase11_parity_pyramid.json` - covers VERF-01 evidence layers and proof scopes.
- [ ] `tools/bazel/manifests/phase11_requirement_evidence.json` - covers all v1 requirements and pending requirement handling.
- [ ] `tools/bazel/manifests/phase11_reference_comparisons.json` - covers VERF-03 reference comparison surfaces.
- [ ] `tools/bazel/manifests/phase11_cutover_readiness.json` - covers VERF-05 demotion criteria and cutover blockers.
- [ ] `tools/bazel/manifests/phase11_retained_code_justifications.json` - covers accepted, blocked, and deferred retained-code islands.
- [ ] `tools/bazel/phase11_verify.py` and `tools/bazel/phase11_verify_test.py` - enforce schemas, source paths, coverage, overclaims, secrets, wiring, lifecycle, and validation text.
- [ ] Bazel labels, root aliases, `rust_workflow.sh` dispatch if needed, and `just phase11-verify`.
- [ ] Optional `rust/crates/domain/src/cutover.rs` plus `lib.rs` exports if typed cutover/evidence invariants are added.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hardware smoke gates for safety, motion, media, auxiliary controllers, MMU, RS485, toolchanger, and release-candidate approval | VERF-01, VERF-04, VERF-05 | Requires physical printers, connected peripherals, or approved hardware-lab artifacts | Record required artifact names in Phase 11 evidence manifests and keep cutover blocked until maintainers attach or approve those artifacts. |
| Simulator flows for GUI, network, storage, protocol traces, and auxiliary-controller behavior | VERF-01, VERF-03, VERF-04 | Requires configured simulator scenarios and produced logs/traces | Treat simulator rows as non-local until actual simulator outputs are referenced by evidence rows. |
| Live network/TLS/API proof against Prusa Connect or service-compatible test endpoints | VERF-01, VERF-03, VERF-04 | Requires controlled service credentials, network setup, and redaction review | Name the required proof and redaction policy; do not store tokens, certificate bytes, passwords, or private keys. |
| Final CMake/C++ reference path demotion | VERF-05 | Requires maintainer approval after all local and non-local gates are satisfied | Keep demotion blocked in `phase11_cutover_readiness.json` unless every cutover criterion is satisfied and approved. |

---

## Threat Coverage

| Threat Group | Coverage |
|--------------|----------|
| `T-11-01-01`..`T-11-01-05` | Parity pyramid rows require evidence class, proof scope, source artifacts, lifecycle metadata, and honest local/non-local classification. |
| `T-11-02-01`..`T-11-02-05` | Requirement evidence rows prevent missing v1 requirements, stale pending status, roadmap-only proof, and unmapped intentional deltas. |
| `T-11-03-01`..`T-11-03-05` | Reference comparison rows require semantic comparison type, fixture or normalization rule, reference surface, and no byte-identity overclaim. |
| `T-11-04-01`..`T-11-04-06` | Cutover readiness and retained-code rows block premature demotion, anonymous retained code, secret-bearing artifacts, and known-concern omissions. |
| `T-11-05-01`..`T-11-05-05` | Aggregate verifier and facade wiring expose test-first verification, lifecycle validation, source path checks, and overclaim/security scans. |

---

## Validation Sign-Off

- [x] All planned task groups have automated verifier commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verification.
- [x] Wave 0 lists all missing validation references.
- [x] No watch-mode flags.
- [x] Feedback latency target remains < 120 seconds for local deterministic checks after warm-up.
- [x] `nyquist_compliant: true` set in frontmatter for the draft validation contract.

**Approval:** draft for Phase 11 planning; local sign-off remains pending until Wave 0 artifacts and final verification are complete.
