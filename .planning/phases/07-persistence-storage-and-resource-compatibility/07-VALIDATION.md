---
phase: 07
slug: persistence-storage-and-resource-compatibility
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-06
lifecycle_mode: yolo
phase_lifecycle_id: 7-2026-06-06T04-24-25
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bazel `shell_binary` wrappers, Python standard-library verifier tests, and Rust cargo checks |
| **Config file** | `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `justfile`, `Cargo.toml`, `pyproject.toml` |
| **Quick run command** | `python3 tools/bazel/phase7_verify.py --quick` |
| **Full suite command** | `just phase7-verify` |
| **Estimated runtime** | Under 10 seconds for static verifier path after Wave 0; Rust full checks remain broader pre-commit gates |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase7_verify.py --quick` when the verifier exists, plus the focused Rust test command for touched Rust modules.
- **After every plan wave:** Run `bazel run //tools/bazel:phase7_verify_tests` and `python3 tools/bazel/phase7_verify.py --all` once labels exist.
- **Before `/gsd-verify-work`:** `just phase7-verify`, Rust pre-commit checks, lifecycle validation, and schema-drift validation must be green.
- **Max feedback latency:** Keep the local static verifier path under 10 seconds; classify heavy generator/media/hardware flows as non-local evidence.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-W0-01 | TBD | 0 | IFCE-04 | T-07-01 | Config-store manifests name credential-bearing keys without secret values | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | no W0 | pending |
| 07-W0-02 | TBD | 0 | IFCE-04 | T-07-02 | Storage and filesystem surfaces classify hardware/media proof as non-local evidence | static verifier + Rust unit tests | `python3 tools/bazel/phase7_verify.py --quick` | no W0 | pending |
| 07-W0-03 | TBD | 0 | IFCE-05 | T-07-03 | Resource/generated-output manifests preserve tracked-vs-build-generated ownership and Phase 3 label coverage | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | no W0 | pending |
| 07-W0-04 | TBD | 0 | IFCE-04, IFCE-05 | T-07-04 | Verifier rejects overclaims, missing lifecycle metadata, and unredacted evidence | Python verifier tests | `python3 tools/bazel/phase7_verify_test.py` | no W0 | pending |
| 07-FINAL | TBD | final | IFCE-04, IFCE-05 | T-07-01..T-07-04 | Phase 7 verifier, Rust checks, Bazel/just labels, lifecycle, and schema drift all pass | aggregate | `just phase7-verify` | no W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/phase7_verify.py` — static verifier for manifests, source paths, Rust API surface, redaction, no-unsafe scan, generated label wiring, concern dispositions, lifecycle metadata, and overclaim guards.
- [ ] `tools/bazel/phase7_verify_test.py` — regression tests for missing rows, invalid lifecycle, unredacted credentials, missing source paths, missing Rust API strings, missing generated labels, and overclaims.
- [ ] `tools/bazel/manifests/phase7_config_store.json` — current items, defaults, deprecated IDs, old EEPROM versions, migration windows, credential-bearing keys, and hash evidence.
- [ ] `tools/bazel/manifests/phase7_storage_media.json` — EEPROM driver, `/usb`, `/internal`, `/bbf`, `/semihosting`, root listing, libsysbase behavior, and non-local evidence classes.
- [ ] `tools/bazel/manifests/phase7_resources.json` — resource image, bootloader image, ESP blobs, WUI assets, translations, QOI, MMU, puppy resources, hashes/revisions, and runtime paths.
- [ ] `tools/bazel/manifests/phase7_generated_outputs.json` — tracked versus generated-at-build outputs and Phase 3 generated label coverage.
- [ ] `tools/bazel/manifests/phase7_concern_dispositions.json` — Phase 7 concern dispositions from `.planning/codebase/CONCERNS.md`.
- [ ] Rust domain extensions in `rust/crates/domain/src/storage.rs` and/or `rust/crates/domain/src/resource.rs`.
- [ ] Bazel and just wiring for `phase7_verify`, `phase7_verify_tests`, root aliases, and `phase7-verify`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Actual USB media mount/read/write timing | IFCE-04 | Requires printer hardware or simulator/media harness | Run later Phase 11 media smoke with `/usb` insert, mount, read, write, eject, and error-path steps. |
| Internal flash wear and filesystem power-loss behavior | IFCE-04 | Requires hardware or dedicated simulator fault injection | Run later Phase 11 storage fault flow; Phase 7 only records non-local evidence class. |
| Full LittleFS/font/translation generator execution | IFCE-05 | Local session lacks `littlefs-python`, pinned `.dependencies/cmake-3.28.3`, and `pre-commit` | Run repo bootstrap first, then execute generated check/update labels or pre-commit hooks in an explicit generator verification pass. |
| Full release artifact byte parity | IFCE-05 | Broader release/cutover evidence, signing and product matrix sensitive | Keep to Phase 11 unless a normalized Phase 7 fixture is explicitly created. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verification.
- [ ] Wave 0 covers all missing verifier, manifest, Rust, Bazel, and just surfaces.
- [ ] No watch-mode flags.
- [ ] Feedback latency under 10 seconds for static Phase 7 verifier.
- [ ] `nyquist_compliant: true` set in frontmatter after execution proves coverage.

**Approval:** pending
