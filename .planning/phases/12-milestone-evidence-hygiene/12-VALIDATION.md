---
phase: 12
slug: milestone-evidence-hygiene
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-15
lifecycle_mode: yolo
phase_lifecycle_id: 12-2026-06-15T18-32-10
---

# Phase 12 - Validation Strategy

> Per-phase validation contract for milestone evidence hygiene.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | GSD planning artifact checks, Phase 11 Python verifier modes, JSON syntax checks, and git diff hygiene. |
| **Config file** | `.planning/config.json`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, Phase 5 validation metadata, and Phase 11 manifests. |
| **Quick run command** | `python3 tools/bazel/phase11_verify.py --quick` |
| **Full suite command** | Phase 12 verification command set in `12-VERIFICATION.md`. |
| **Estimated runtime** | Under 60 seconds for local Phase 11 verifier modes and planning metadata checks. |

## Sampling Rate

- **After Task 1:** Check BAZL-03/BAZL-05 requirement rows, Phase 9 progress, Phase 12 progress, and non-local gate preservation row.
- **After Task 2:** Check Phase 5 validation metadata and rerun `--requirements-only` plus `--cutover-only`.
- **After Task 3:** Check audit frontmatter/body and rerun the full Phase 12 verification command set.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 0 | BAZL-03, BAZL-05, IFCE-02, IFCE-03 | T-12-01-01 | Requirements and roadmap metadata match passed evidence without changing firmware behavior. | grep/diff | `rg --fixed-strings "| BAZL-03 | Phase 3 | Complete |" .planning/REQUIREMENTS.md && rg --fixed-strings "| 9. Network, Web Services, and Transfers | 4/4 | Complete | 2026-06-14 |" .planning/ROADMAP.md` | yes | green |
| 12-01-02 | 01 | 0 | RUST-03, RUST-04, CORE-01, CORE-02, VERF-01, VERF-04, VERF-05 | T-12-01-02 | Validation and cutover wording reflect passed local evidence while preserving reference-demotion blockers. | verifier | `python3 tools/bazel/phase11_verify.py --requirements-only && python3 tools/bazel/phase11_verify.py --cutover-only` | yes | green |
| 12-01-03 | 01 | 0 | BAZL-03, BAZL-05, RUST-03, RUST-04, CORE-01, CORE-02, IFCE-02, IFCE-03, VERF-01, VERF-04, VERF-05 | T-12-01-03 | Follow-up audit reports no metadata-drift tech debt and names preserved non-local gates. | verifier/diff | `python3 tools/bazel/phase11_verify.py --quick && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze --raw && git diff --check` | yes | green |

*Status: pending, green, red, flaky*

## Wave 0 Requirements

- [x] `.planning/REQUIREMENTS.md` - BAZL-03 and BAZL-05 complete with traceability rows.
- [x] `.planning/ROADMAP.md` - Phase 9 and Phase 12 progress rows complete with dates.
- [x] `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-VALIDATION.md` - status and task rows complete.
- [x] `tools/bazel/manifests/phase11_requirement_evidence.json` - stale aggregate wording removed.
- [x] `tools/bazel/manifests/phase11_cutover_readiness.json` - aggregate/security criteria source-backed locally while reference demotion remains blocked.
- [x] `.planning/v1.0-MILESTONE-AUDIT.md` - follow-up audit status passed.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Final production reference demotion | VERF-05 | Requires simulator, hardware, live service, release-candidate, retained-code acceptance, and maintainer approval evidence outside local metadata cleanup. | Do not demote CMake/C++ reference paths until the Phase 11 non-local evidence gates are attached and accepted. |

## Validation Sign-Off

- [x] All 3 tasks have automated verify commands.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all Phase 12 metadata cleanup references.
- [x] No watch-mode flags.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-15
