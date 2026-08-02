---
phase: 34-final-readiness-and-demotion-dry-run
fixed_at: 2026-07-25T19:36:40Z
review_path: /Users/peterryszkiewicz/Repos/Prusa-Firmware-Buddy/.planning/phases/34-final-readiness-and-demotion-dry-run/34-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 34: Code Review Fix Report

**Fixed at:** 2026-07-25T19:36:40Z
**Source review:** `/Users/peterryszkiewicz/Repos/Prusa-Firmware-Buddy/.planning/phases/34-final-readiness-and-demotion-dry-run/34-REVIEW.md`
**Iteration:** 1

**Summary:**

- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### CR-01: Uncorroborated Phase 33 projections can open the demotion gate

**Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run.py`, `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
**Commit:** 991f4c3c2
**Status:** fixed: requires human verification
**Applied fix:** Added duplicate-rejecting normalized decision validation, Phase 33 schema and enum checks, ISO UTC timestamp validation, and exact readiness/demotion projection corroboration against matching decision IDs, metadata, and source refs. Added an isolated open-gate fixture and negative regression cases.

### CR-02: Nested register inputs can escape their allowed roots through symlinks

**Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run.py`, `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
**Commit:** 3523c1f55
**Status:** fixed
**Applied fix:** Applied resolved containment checks before loading every consumed nested Phase 33 register and the Phase 32 blocker register. Added separate symlink-escape regression coverage for all four files.

### WR-01: Missing or malformed approval files leave no durable blocked artifact

**Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run.py`, `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
**Commit:** 97fab7c39
**Status:** fixed
**Applied fix:** Separated demotion approval loading from the validated evidence load and retained a deterministic minimal blocked run manifest and dry-run result before returning the original validation error. Covered missing, invalid JSON, non-object, unsafe-ref, forbidden-field, forbidden-text, and symlink failures.

### WR-02: Sparse overlay matching ignores affected-gate and dangling references

**Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run.py`, `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
**Commit:** e144258d8
**Status:** fixed: requires human verification
**Applied fix:** Replaced source-only matching with exact source-ref and affected-gate joins plus stream consistency, detected duplicate blocker and decision IDs, and added bidirectional anti-joins that retain unmatched blockers and decisions as deterministic blocked ledger rows. Preserved the clean/no-blocker sparse-overlay state.

***

_Fixed: 2026-07-25T19:36:40Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
