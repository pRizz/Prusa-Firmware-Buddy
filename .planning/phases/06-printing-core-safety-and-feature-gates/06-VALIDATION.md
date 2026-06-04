---
phase: 06
slug: printing-core-safety-and-feature-gates
status: complete
nyquist_compliant: true
wave_0_complete: true
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

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | Precondition | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|--------------|--------|
| 06-01-01 | 01 | 0 | CORE-03, CORE-04, CORE-05 | T-06-01-01 to T-06-01-04 | Verifier schema gates reject missing lifecycle, requirement, source-path, evidence-class, concern, and overclaim data. | static verifier bootstrap | `python3 -m py_compile tools/bazel/phase6_verify.py && python3 tools/bazel/phase6_verify.py --help` | none | green |
| 06-01-02 | 01 | 0 | CORE-03, CORE-04, CORE-05 | T-06-01-01 to T-06-01-05 | Printing, safety, feature, and concern manifests carry required rows before Rust policies depend on them. | manifest verifier | `python3 tools/bazel/phase6_verify.py --manifests-only` | 06-01-01 creates verifier | green |
| 06-01-03 | 01 | 0 | CORE-03, CORE-04, CORE-05 | T-06-01-06 | Aggregate Phase 6 verification is reachable through direct Python, Bazel, and `just`. | integration/static | `python3 tools/bazel/phase6_verify.py --quick && bazel query "//tools/bazel:phase6_verify + //:phase6_verify" && just --list` | 06-01-01 and 06-01-02 complete | green |
| 06-02-01 | 02 | 1 | CORE-03 | T-06-02-01 to T-06-02-05 | Print state, fixture identity, routing, and file/serial separation reject impossible transitions without rewriting Marlin. | Rust unit | `cargo test --all-features -p buddy-domain print` | 06-01 complete for shared verifier and manifest context | green |
| 06-02-02 | 02 | 1 | CORE-03 | T-06-02-04 | CORE-03 manifest rows bind Rust print surfaces to retained Marlin/Buddy oracle paths. | manifest verifier + Rust unit | `python3 tools/bazel/phase6_verify.py --printing-only && cargo test --all-features -p buddy-domain print` | Wave 0 verifier and manifests exist | green |
| 06-04-01 | 04 | 1 | CORE-05 | T-06-04-01 to T-06-04-05 | ProductProfile-keyed feature facts reject unsupported combinations and keep auxiliary runtime parity out of scope. | Rust unit | `cargo test --all-features -p buddy-domain feature` | 06-01 complete for shared verifier and manifest context | green |
| 06-04-02 | 04 | 1 | CORE-05 | T-06-04-02 to T-06-04-04 | CORE-05 manifest rows bind Rust gate surfaces to CMake, preset, Marlin, TMC, and MMU concern references. | manifest verifier + Rust unit | `python3 tools/bazel/phase6_verify.py --features-only && cargo test --all-features -p buddy-domain feature` | Wave 0 verifier and manifests exist | green |
| 06-03-01 | 03 | 2 | CORE-04 | T-06-03-01 to T-06-03-05 | Safety flows classify local policy decisions separately from simulator, hardware-smoke, and manual evidence. | Rust unit | `cargo test --all-features -p buddy-domain safety` | 06-01 and 06-02 complete for shared domain exports | green |
| 06-03-02 | 03 | 2 | CORE-04 | T-06-03-01 to T-06-03-04 | CORE-04 manifest rows bind Rust safety surfaces to retained fatal, watchdog, crash-dump, emergency, and probe paths. | manifest verifier + Rust unit | `python3 tools/bazel/phase6_verify.py --safety-only && cargo test --all-features -p buddy-domain safety` | Wave 0 verifier and manifests exist; 06-03-01 creates safety API | green |
| 06-05-01 | 05 | 3 | CORE-03, CORE-04, CORE-05 | T-06-05-01 to T-06-05-04 | Hardened quick verification enforces Rust API shape, unsafe posture, facade wiring, validation contract, and overclaim guard. | static verifier + aggregate quick gate | `python3 -m py_compile tools/bazel/phase6_verify.py && python3 tools/bazel/phase6_verify.py --quick` | 06-02, 06-03, and 06-04 complete | green |
| 06-05-02 | 05 | 3 | CORE-03, CORE-04, CORE-05 | T-06-05-05 | Nyquist sign-off records actual command outcomes and only sets compliance after this all-11-task map is complete. | validation sign-off + aggregate gate | `python3 tools/bazel/phase6_verify.py --quick && just phase6-verify` | 06-05-01 complete; map contains task IDs 06-01-01 through 06-05-02 | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [x] `tools/bazel/phase6_verify.py` - validates schema, lifecycle id, requirements, source paths, evidence classes, concern dispositions, Rust API shape, Bazel/just labels, and overclaim guard.
- [x] `tools/bazel/manifests/phase6_printing_core.json` - covers CORE-03 print fixture/contract rows.
- [x] `tools/bazel/manifests/phase6_safety_gates.json` - covers CORE-04 safety policy/evidence rows.
- [x] `tools/bazel/manifests/phase6_feature_gates.json` - covers CORE-05 feature-gate rows derived from reference sources.
- [x] `tools/bazel/manifests/phase6_concern_dispositions.json` - covers known concern dispositions and intentional deltas.
- [x] `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, root `BUILD.bazel`, and `justfile` expose Phase 6 verification labels and recipes.

---

## Final Automated Evidence

| Command | Outcome |
|---------|---------|
| `python3 tools/bazel/phase6_verify.py --quick` | passed; printed `Phase 6 printing core safety and feature gate verification passed` |
| `just phase6-verify` | passed; Bazel built and ran `//tools/bazel:phase6_verify`, which printed `Phase 6 printing core safety and feature gate verification passed` |
| `cargo fmt --all -- --check` | passed directly and through `just phase6-verify` / `phase6_verify.py --all` |
| `cargo clippy --all-targets --all-features -- -D warnings` | passed directly and through `just phase6-verify` / `phase6_verify.py --all` |
| `cargo build --all-targets --all-features` | passed directly and through `just phase6-verify` / `phase6_verify.py --all` |
| `cargo test --all-features` | passed directly and through `just phase6-verify` / `phase6_verify.py --all` |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Actual thermal, motion, watchdog, crash recovery, emergency stop, and hardware safe-output behavior | CORE-04 | Host tests and static manifests cannot prove MCU/HAL/RTOS/hardware effects. | Record required `simulator-flow`, `hardware-smoke`, or `manual-hardware-required` evidence rows in Phase 6 manifests and defer physical proof to the parity pyramid unless a plan provisions it. |
| Full Marlin planner and TMC motion-driver equivalence | CORE-03, CORE-05 | Phase 6 uses retained Marlin/TMC reference contracts and does not rewrite the full planner or drivers. | Keep retained source paths in print/feature manifests and verify Rust policies only claim fixture-backed behavior. |
| Auxiliary controller and MMU runtime behavior parity | CORE-05 | Phase 6 only needs printing/safety gate facts; behavior parity remains Phase 10. | Keep auxiliary behavior rows out of Phase 6 except narrow gate facts required by printing or safety policies. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** passed - local automated Phase 6 gate is green; non-local safety evidence remains classified in the Manual-Only Verifications table.
