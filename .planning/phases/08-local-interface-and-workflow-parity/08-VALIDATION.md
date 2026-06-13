---
phase: 08
slug: local-interface-and-workflow-parity
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-13
lifecycle_mode: yolo
phase_lifecycle_id: 8-2026-06-13T16-58-45
---

# Phase 08 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python standard-library verifier tests, Rust `cargo test --all-features` for `buddy-domain`, Bazel `shell_binary` wrappers, and `just` facade |
| **Config file** | `Cargo.toml`, `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `justfile`, `.planning/config.json` |
| **Quick run command** | `python3 tools/bazel/phase8_verify.py --quick` |
| **Full suite command** | `just phase8-verify` |
| **Estimated runtime** | Under 10 seconds for the static verifier path after Wave 0; Rust full checks remain broader pre-commit gates |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase8_verify.py --quick` once the verifier exists, plus focused Rust tests for touched `buddy-domain` code.
- **After every plan wave:** Run `python3 tools/bazel/phase8_verify_test.py`, `python3 tools/bazel/phase8_verify.py --all`, and Bazel query for new Phase 8 labels once labels exist.
- **Before `/gsd-verify-work`:** `just phase8-verify`, Rust pre-commit checks, lifecycle validation, and schema/source drift validation must be green.
- **Max feedback latency:** Keep the local static verifier path under 10 seconds; classify simulator, physical display, touch, long-run UI, and hardware flows as non-local evidence unless actually run.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-W0-01 | Plan TBD | Wave 0 | IFCE-01 | T-08-01 | Screen stack bootstrap/home behavior is manifest-covered with source paths and Rust surface | static verifier + Rust unit | `python3 tools/bazel/phase8_verify.py --quick` and `cargo test --all-features` | no; Wave 0 files required | pending |
| 08-W0-02 | Plan TBD | Wave 0 | IFCE-01 | T-08-02 | Dialog, menu, wizard, print-control, setup/selftest/calibration, warning, redscreen, and Connect registration entry rows exist | static verifier | `python3 tools/bazel/phase8_verify.py --quick` | no; Wave 0 files required | pending |
| 08-W0-03 | Plan TBD | Wave 0 | IFCE-01 | T-08-03 | 240x320 and 480x320 layout, localization, print preview, and progress contracts are explicit | static verifier + Rust unit | `python3 tools/bazel/phase8_verify.py --quick` and `cargo test --all-features` | no; Wave 0 files required | pending |
| 08-W0-04 | Plan TBD | Wave 0 | IFCE-01 | T-08-04 | CL-008 and crash dump warning surfaces are explicitly dispositioned without secret or memory bytes | verifier regression tests | `python3 tools/bazel/phase8_verify_test.py` | no; Wave 0 files required | pending |
| 08-W0-05 | Plan TBD | Wave 0 | IFCE-01 | T-08-05 | Bazel labels, root aliases, `rust_workflow.sh`, `just phase8-verify`, lifecycle metadata, validation artifact, and overclaim guards are present | Bazel/facade/static verifier | `bazel query "//tools/bazel:phase8_verify + //tools/bazel:phase8_verify_tests + //:phase8_verify + //:phase8_verify_tests"` and `just phase8-verify` | no; Wave 0 files required | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/phase8_verify.py` - validates manifests, source paths, Rust API surface, no unsafe pure domain code, concern dispositions, lifecycle, validation artifact, Bazel/just wiring, and overclaim guards.
- [ ] `tools/bazel/phase8_verify_test.py` - regression tests for missing rows, missing source paths, invalid lifecycle, invalid evidence class, missing display class, missing CL-008, missing crash dump warning, secret markers, missing Rust API strings, missing labels, and overclaims.
- [ ] `tools/bazel/manifests/phase8_gui_workflows.json` - screen stacks, dialogs, menus, wizards, print controls, setup/selftest/calibration flows, Connect registration entry surfaces, warnings, redscreens, and errors.
- [ ] `tools/bazel/manifests/phase8_display_layouts.json` - 240x320 and 480x320 layout, localized text, font/resource visibility, truncation, print preview, progress, and error/warning text rows.
- [ ] `tools/bazel/manifests/phase8_concern_dispositions.json` - CL-008, crash dump warning, generated GUI resource drift inherited from Phase 7, and any IFCE-01-specific concern discovered during planning.
- [ ] `rust/crates/domain/src/gui.rs` and `rust/crates/domain/src/lib.rs` exports - pure GUI/display/evidence domain types and errors.
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` Phase 8 labels/recipes.
- [ ] `.planning/phases/08-local-interface-and-workflow-parity/08-VALIDATION.md` - Nyquist contract with local/non-local evidence boundaries and phase lifecycle ID.

---

## Manual-Only Verifications

These remain non-local evidence classes: `manual-hardware-required`, `hardware-smoke`, and `simulator-flow`.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Physical LCD rendering and touch/encoder timing | IFCE-01 | Requires supported printer hardware or a validated display/touch simulator flow | Run later simulator or hardware smoke across representative 240x320 and 480x320 products; record screenshots/logs as non-local evidence. |
| Long-run GUI event-loop stability | IFCE-01 | Requires simulator or hardware soak with UI actions and printer-state changes | Run later long-run UI navigation and print-control flow; record whether event dispatch remains responsive. |
| Full display-state fixture comparison across product matrix | IFCE-01, VERF-03 | Broader parity/cutover evidence belongs to Phase 11 unless a narrow Phase 8 fixture is created | Run Phase 11 display-state fixture comparison after Phase 8, Phase 9, and Phase 10 surfaces are complete. |
| Network service behavior behind Connect registration or PrusaLink surfaces | IFCE-02, IFCE-03 | Phase 8 owns local entry surfaces only; service behavior belongs to Phase 9 | Verify service behavior in Phase 9, while Phase 8 records only local GUI entry coverage. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verification.
- [ ] Wave 0 covers missing verifier, manifest, Rust, Bazel, and just surfaces.
- [ ] No watch-mode flags.
- [ ] Feedback latency under 10 seconds for static Phase 8 verifier.
- [ ] `nyquist_compliant: true` set in frontmatter after execution proves coverage.

**Approval:** pending Phase 8 implementation and verification.
