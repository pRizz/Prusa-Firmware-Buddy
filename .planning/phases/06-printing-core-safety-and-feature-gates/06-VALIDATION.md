---
phase: 06
slug: printing-core-safety-and-feature-gates
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-04
---

# Phase 6 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Rust `cargo test` through Bazel/just, plus Python stdlib phase verifier |
| **Config file** | `Cargo.toml`, `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `justfile` |
| **Quick run command** | `python3 tools/bazel/phase6_verify.py --quick` |
| **Full suite command** | `just phase6-verify` |
| **Estimated runtime** | ~60 seconds after Wave 0 creates the verifier |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase6_verify.py --quick` once the verifier exists.
- **After every plan wave:** Run `just phase6-verify`.
- **Before `/gsd-verify-work`:** `just phase6-verify` must be green and all non-local simulator/hardware/manual evidence must be listed in Phase 6 artifacts.
- **Max feedback latency:** 60 seconds for local checks after Wave 0.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | CORE-03 | T-06-01 | Manifest rows cannot accept missing or stale reference paths for print behavior. | static verifier | `python3 tools/bazel/phase6_verify.py --quick` | no, W0 | pending |
| 06-01-02 | 01 | 1 | CORE-04 | T-06-02 | Safety rows must carry explicit local or non-local evidence classes and cannot overclaim hardware proof. | static verifier | `python3 tools/bazel/phase6_verify.py --quick` | no, W0 | pending |
| 06-01-03 | 01 | 1 | CORE-05 | T-06-03 | Feature gates are keyed by validated product profiles and reject unsupported combinations. | Rust unit | `cargo test --all-features` | no, W0 | pending |
| 06-01-04 | 01 | 1 | CORE-03, CORE-04, CORE-05 | T-06-04 | Aggregate Phase 6 verification is reachable through Bazel and just. | integration/static | `just phase6-verify` | no, W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/phase6_verify.py` - validates schema, lifecycle id, requirements, source paths, evidence classes, concern dispositions, Rust API shape, Bazel/just labels, and overclaim guard.
- [ ] `tools/bazel/manifests/phase6_printing_core.json` - covers CORE-03 print fixture/contract rows.
- [ ] `tools/bazel/manifests/phase6_safety_gates.json` - covers CORE-04 safety policy/evidence rows.
- [ ] `tools/bazel/manifests/phase6_feature_gates.json` - covers CORE-05 feature-gate rows derived from reference sources.
- [ ] `tools/bazel/manifests/phase6_concern_dispositions.json` - covers known concern dispositions and intentional deltas.
- [ ] `rust/crates/domain/src/print.rs` - pure print transition and command route policies with tests.
- [ ] `rust/crates/domain/src/safety.rs` - pure safety policy classification and evidence types with tests.
- [ ] `rust/crates/domain/src/feature.rs` - Phase 6 feature gates keyed by validated product profiles.
- [ ] `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, root `BUILD.bazel`, and `justfile` expose Phase 6 verification labels and recipes.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Actual thermal, motion, watchdog, crash recovery, emergency stop, and hardware safe-output behavior | CORE-04 | Host tests and static manifests cannot prove MCU/HAL/RTOS/hardware effects. | Record required `simulator-flow`, `hardware-smoke`, or `manual-hardware-required` evidence rows in Phase 6 manifests and defer physical proof to the parity pyramid unless a plan provisions it. |
| Full Marlin planner and TMC motion-driver equivalence | CORE-03, CORE-05 | Phase 6 uses retained Marlin/TMC reference contracts and does not rewrite the full planner or drivers. | Keep retained source paths in print/feature manifests and verify Rust policies only claim fixture-backed behavior. |
| Auxiliary controller and MMU runtime behavior parity | CORE-05 | Phase 6 only needs printing/safety gate facts; behavior parity remains Phase 10. | Keep auxiliary behavior rows out of Phase 6 except narrow gate facts required by printing or safety policies. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
