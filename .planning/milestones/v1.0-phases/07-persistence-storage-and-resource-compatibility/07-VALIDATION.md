---
phase: 07
slug: persistence-storage-and-resource-compatibility
status: complete
nyquist_compliant: true
wave_0_complete: true
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
| 07-W0-01 | Plan 01 | Wave 1 | IFCE-04 | T-07-01 | Config-store manifests name credential-bearing keys without secret values | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-W0-02 | Plan 01 | Wave 1 | IFCE-04 | T-07-02 | Storage and filesystem surfaces classify hardware/media proof as non-local evidence | static verifier + Rust unit tests | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-W0-03 | Plan 02 | Wave 1 | IFCE-05 | T-07-03 | Resource/generated-output manifests preserve tracked-vs-build-generated ownership and Phase 3 label coverage | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-W0-04 | Plan 04 | Wave 2 | IFCE-04, IFCE-05 | T-07-04 | Verifier rejects overclaims, missing lifecycle metadata, and unredacted evidence | Python verifier tests | `python3 tools/bazel/phase7_verify_test.py` | yes | green |
| 07-W0-05 | Plan 01 | Wave 1 | IFCE-04 | T-07-05 | Redacted storage migration catalog covers old EEPROM versions, current schema, settings import/export, credential redaction, selftest/calibration state, and journal hash facts | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-01-03 | Plan 01 | Wave 1 | IFCE-04 | T-07-05 | `tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json` includes `selftest-calibration-state`, `Selftest Result`, `selftest_result`, `calibration`, and `selftest` | fixture string check | `python3 -c "from pathlib import Path; p=Path('tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json'); text=p.read_text(); assert all(s in text for s in ['selftest-calibration-state', 'Selftest Result', 'selftest_result', 'calibration', 'selftest'])"` | yes | green |
| 07-02-01 | Plan 02 | Wave 1 | IFCE-05 | T-07-03 | Resource package members and runtime paths are source-backed without claiming runtime media or release parity | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-02-02 | Plan 02 | Wave 1 | IFCE-05 | T-07-03 | Generated-output ownership keeps check/update labels and tracked-vs-build-generated surfaces distinct | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-02-03 | Plan 02 | Wave 1 | IFCE-04, IFCE-05 | T-07-04 | Concern dispositions preserve known risks with regression guards and no silent intentional deltas | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-03-01 | Plan 03 | Wave 2 | IFCE-04 | T-07-01, T-07-02, T-07-05 | Rust storage domain types preserve schema, migration, journal hash, redaction, filesystem, and fixture invariants | Rust unit tests | `cargo test --all-features` | yes | green |
| 07-03-02 | Plan 03 | Wave 2 | IFCE-05 | T-07-03 | Rust resource domain types preserve runtime paths, generated ownership, and check/update label invariants | Rust unit tests | `cargo test --all-features` | yes | green |
| 07-04-01 | Plan 04 | Wave 2 | IFCE-04, IFCE-05 | T-07-04, T-07-05 | Verifier regression tests cover missing rows, lifecycle drift, redaction, API strings, unsafe code, generated labels, and overclaims | Python verifier tests | `python3 tools/bazel/phase7_verify_test.py` | yes | green |
| 07-04-02 | Plan 04 | Wave 2 | IFCE-04, IFCE-05 | T-07-01..T-07-05 | Static verifier checks manifests, catalog, source paths, Rust API surface, Bazel/just wiring, lifecycle, and overclaim guardrails | static verifier | `python3 tools/bazel/phase7_verify.py --quick` | yes | green |
| 07-05-01 | Plan 05 | Wave 3 | IFCE-04, IFCE-05 | T-07-05-01, T-07-05-02, T-07-05-05 | Bazel labels, root aliases, docs filegroup, storage migration fixture filegroup, workflow dispatch, and `just phase7-verify` are queryable/runnable | Bazel + facade | `bazel query "//tools/bazel:phase7_verify + //tools/bazel:phase7_verify_tests + //:phase7_verify + //:phase7_verify_tests + //:phase7_persistence_storage_resource_docs + //:phase7_storage_migration_fixtures"` | yes | green |
| 07-05-02 | Plan 05 | Wave 3 | IFCE-04, IFCE-05 | T-07-05-03, T-07-05-04 | Final validation records only passed local evidence and keeps hardware/media/generator/release proof non-local | aggregate | `just phase7-verify` | yes | green |
| 07-FINAL | Plan 05 | Wave 3 | IFCE-04, IFCE-05 | T-07-01..T-07-05 | Phase 7 verifier, Rust checks, Bazel/just labels, lifecycle, and schema drift all pass | aggregate | `just phase7-verify` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [x] `tools/bazel/phase7_verify.py` — static verifier for manifests, source paths, Rust API surface, redaction, no-unsafe scan, generated label wiring, concern dispositions, lifecycle metadata, and overclaim guards.
- [x] `tools/bazel/phase7_verify_test.py` — regression tests for missing rows, invalid lifecycle, unredacted credentials, missing source paths, missing Rust API strings, missing generated labels, and overclaims.
- [x] `tools/bazel/manifests/phase7_config_store.json` — current items, defaults, deprecated IDs, old EEPROM versions, migration windows, credential-bearing keys, and hash evidence.
- [x] `tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json` — synthetic/redacted fixture identities for old EEPROM versions, current schema, settings import/export, credential redaction, `selftest-calibration-state`, `Selftest Result`, `selftest_result`, `calibration`, `selftest`, and journal hash facts.
- [x] `tools/bazel/manifests/phase7_storage_media.json` — EEPROM driver, `/usb`, `/internal`, `/bbf`, `/semihosting`, root listing, libsysbase behavior, and non-local evidence classes.
- [x] `tools/bazel/manifests/phase7_resources.json` — resource image, bootloader image, ESP blobs, WUI assets, translations, QOI, MMU, puppy resources, hashes/revisions, and runtime paths.
- [x] `tools/bazel/manifests/phase7_generated_outputs.json` — tracked versus generated-at-build outputs and Phase 3 generated label coverage.
- [x] `tools/bazel/manifests/phase7_concern_dispositions.json` — Phase 7 concern dispositions from `.planning/codebase/CONCERNS.md`.
- [x] Rust domain extensions in `rust/crates/domain/src/storage.rs` and/or `rust/crates/domain/src/resource.rs`.
- [x] Bazel and just wiring for `phase7_verify`, `phase7_verify_tests`, root aliases, and `phase7-verify`.

---

## Final Automated Evidence

`just phase7-verify` is deterministic static verifier/test/Rust evidence. It does not run full generator update/check labels, simulator flows, physical media checks, hardware smoke, or release artifact byte parity.

| Command | Outcome | Evidence Scope |
|---------|---------|----------------|
| `python3 tools/bazel/phase7_verify.py --quick` | passed | Static manifests, catalog, source paths, Rust API strings, Bazel/just surface, lifecycle, and overclaim checks |
| `python3 tools/bazel/phase7_verify_test.py` | passed; 13 tests | Python verifier regression suite |
| `bazel run //tools/bazel:phase7_verify_tests` | passed; 13 tests | Bazel-exposed verifier regression suite |
| `bazel run //tools/bazel:phase7_verify` | passed | Bazel-exposed aggregate verifier with Rust toolchain checks through `--all` |
| `just phase7-verify` | passed | Developer facade running verifier tests before aggregate verifier |
| `cargo fmt --all -- --check` | passed | Rust formatting check |
| `cargo clippy --all-targets --all-features -- -D warnings` | passed | Rust lint check with warnings denied |
| `cargo build --all-targets --all-features` | passed | Rust build for all targets and features |
| `cargo test --all-features` | passed | Rust unit/doc test suite for all features |

---

## Manual-Only Verifications

These remain non-local evidence classes: `manual-hardware-required`, `hardware-smoke`, and `simulator-flow`.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Actual USB media mount/read/write timing | IFCE-04 | Requires printer hardware or simulator/media harness | Run later Phase 11 media smoke with `/usb` insert, mount, read, write, eject, and error-path steps. |
| Internal flash wear and filesystem power-loss behavior | IFCE-04 | Requires hardware or dedicated simulator fault injection | Run later Phase 11 storage fault flow; Phase 7 only records non-local evidence class. |
| Full LittleFS/font/translation generator execution | IFCE-05 | Local session lacks `littlefs-python`, pinned `.dependencies/cmake-3.28.3`, and `pre-commit` | Run repo bootstrap first, then execute generated check/update labels or pre-commit hooks in an explicit generator verification pass. |
| Full release artifact byte parity | IFCE-05 | Broader release/cutover evidence, signing and product matrix sensitive | Keep to Phase 11 unless a normalized Phase 7 fixture is explicitly created. |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verification.
- [x] Wave 0 covers all missing verifier, manifest, Rust, Bazel, and just surfaces.
- [x] No watch-mode flags.
- [x] Feedback latency under 10 seconds for static Phase 7 verifier.
- [x] `nyquist_compliant: true` set in frontmatter after execution proves coverage.

**Approval:** automated evidence complete; manual-only evidence remains deferred to later simulator, generator, media, hardware, or release-parity gates.
