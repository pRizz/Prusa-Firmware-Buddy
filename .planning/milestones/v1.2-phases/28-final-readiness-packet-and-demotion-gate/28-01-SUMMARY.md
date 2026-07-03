---
phase: 28-final-readiness-packet-and-demotion-gate
plan: 28-01
subsystem: final-readiness-packet-and-demotion-gate
generated_by: gsd-executor
lifecycle_mode: yolo
phase_lifecycle_id: 28-2026-06-25T03-31-49
generated_at: 2026-06-25T04:32:07Z
tags:
  - final-readiness
  - demotion-gate
  - bazel
  - evidence
requires:
  - phase26-release-signing-upstream-evidence
  - phase27-retained-code-acceptance-decisions
provides:
  - phase28-final-readiness-packet-contract
  - phase28-final-readiness-packet-verifier
  - phase28-reference-demotion-authorization-record
affects:
  - BUILD.bazel
  - tools/bazel/BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - justfile
requirements:
  - READ-01
  - READ-02
  - READ-03
requirements_completed:
  - READ-01
  - READ-02
  - READ-03
requirements-completed:
  - READ-01
  - READ-02
  - READ-03
tech-stack:
  added:
    - Python Phase 28 verifier
    - Bazel shell targets
  patterns:
    - deterministic redacted CI evidence artifacts
    - explicit maintainer demotion decision gate
key-files:
  created:
    - tools/bazel/manifests/phase28_final_readiness_packet_contract.json
    - tools/bazel/phase28_final_readiness_packet.py
    - tools/bazel/phase28_final_readiness_packet_test.py
  modified:
    - BUILD.bazel
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - justfile
decisions:
  - Reference demotion remains blocked unless Phase 28 receives an explicit approved maintainer decision and final readiness is unblocked.
  - Final readiness evidence aggregation excludes the demotion criterion from readiness unblocking, but records it as a separate authorization gate.
metrics:
  completed_at: 2026-06-25T04:32:07Z
  task_count: 3
  files_created: 3
  files_modified: 4
---

# Phase 28 Plan 01: Final Readiness Packet Summary

Final readiness packet generation now aggregates Phase 26 upstream rows and the Phase 27 maintainer handoff into a redacted Phase 28 packet, while keeping reference demotion blocked until an explicit maintainer authorization input is supplied.

## Tasks Completed

| Task | Commit | Summary |
| ---- | ------ | ------- |
| 1 | 9eddc5a58 | Added the Phase 28 contract, contract-only CLI validation, and contract regression tests. |
| 2 | e68cbcd28 | Implemented Phase 28 quick packet generation, input validation, hard-blocker handling, output security scanning, and demotion decision validation. |
| 3 | 9b3fd6e31 | Wired Phase 28 into Bazel, `rust_workflow.sh`, root aliases, `just phase28-verify`, and wiring regression tests. |

## Outputs

- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` defines READ-01/02/03, canonical criteria, required inputs, hard-blocker policy, generated artifacts, and demotion decision metadata.
- `tools/bazel/phase28_final_readiness_packet.py` supports `--contract-only`, `--quick`, `--security-only`, and `--wiring-only`.
- `build/ci-evidence/phase28/` quick mode writes all planned generated artifacts, including `final-readiness-packet.json`, `reference-demotion-authorization-record.json`, and `redacted-readiness-report.md`.
- `just phase28-verify` runs Phase 28 tests first, then chains Phase 26 quick, Phase 27 quick, and Phase 28 quick verification through Bazel.

## Verification

Passed:

- `python3 tools/bazel/phase28_final_readiness_packet.py --contract-only`
- `python3 tools/bazel/phase28_final_readiness_packet_test.py` - 22 tests passed.
- `python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only`
- `python3 tools/bazel/phase28_final_readiness_packet.py --security-only`
- `just phase28-verify`
- `rg -n '"demotion_allowed"\s*:\s*true|"reference_demotion_authorization"\s*:\s*"approved"' build/ci-evidence/phase28` - no matches.
- Generated packet check: `final_readiness_status=blocked`, `reference_demotion_authorization=blocked`, `criteria_count=9`, `requirements_count=3`, `real_maintainer_demotion_approval_supplied=false`.
- Per-commit Rust sequence passed before each task commit: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, `cargo test --all-features`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Avoided redacted-report overclaim scanner false positive**
- **Found during:** Task 2 test verification.
- **Issue:** The report line for `final-reference-demotion-allowed:` caused the forbidden `demotion_allowed` assignment scanner to match the criterion suffix plus colon.
- **Fix:** Changed report criterion formatting to use `->` instead of `:`.
- **Files modified:** `tools/bazel/phase28_final_readiness_packet.py`
- **Commit:** e68cbcd28

**2. [Rule 1 - Bug] Fixed symlink escape regression fixture setup**
- **Found during:** Task 2 test verification.
- **Issue:** The symlink escape test attempted to recreate an existing output parent directory.
- **Fix:** Made the fixture parent creation idempotent.
- **Files modified:** `tools/bazel/phase28_final_readiness_packet_test.py`
- **Commit:** e68cbcd28

## Auth Gates

None.

## Known Stubs

None.

## Threat Flags

None. This plan added local evidence-contract validation and generated artifact writing only; it introduced no network endpoints, auth paths, file access beyond repo-contained evidence paths, or schema changes at trust boundaries.

## Shared State

Per orchestrator instruction, this executor did not update `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, or `.planning/config.json`. `.planning/config.json` remained an unrelated transient orchestrator modification and was not staged.

## Self-Check: PASSED

- Found created files: `tools/bazel/manifests/phase28_final_readiness_packet_contract.json`, `tools/bazel/phase28_final_readiness_packet.py`, `tools/bazel/phase28_final_readiness_packet_test.py`, and this summary.
- Found task commits: `9eddc5a58`, `e68cbcd28`, `9b3fd6e31`.
- Git status before summary commit showed only this summary plus the unrelated `.planning/config.json` orchestrator change.
