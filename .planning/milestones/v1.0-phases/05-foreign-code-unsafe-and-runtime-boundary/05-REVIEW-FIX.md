---
phase: 05-foreign-code-unsafe-and-runtime-boundary
fixed_at: 2026-06-03T21:06:03Z
review_path: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 05: Code Review Fix Report

**Fixed at:** 2026-06-03T21:06:03Z
**Source review:** .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 6
- Fixed: 6
- Skipped: 0

## Fixed Issues

### CR-01: Safe MMIO API Allows Arbitrary Volatile Reads And Writes

**Files modified:** `rust/crates/board-adapter/src/mmio.rs`
**Commit:** 24be55c83
**Applied fix:** Replaced safe arbitrary register construction with `unsafe new_unchecked`, made volatile `read` and `write` unsafe, and updated MMIO constructor tests.

### WR-01: Feature-Gated TaskDeps Are Modeled As Unconditional Dependencies

**Files modified:** `rust/crates/runtime-adapter/src/task.rs`
**Commit:** deb982398
**Applied fix:** Added profile-aware dependency mask calculation that drops `puppies_ready` for non-puppy profiles and added puppy/non-puppy regression tests.

### WR-02: H503 Linker Contract Reports The Included Script As The Active Script

**Files modified:** `rust/crates/runtime-adapter/src/linker.rs`
**Commit:** 45193a588
**Applied fix:** Selected H503 boot/noboot wrapper scripts as active linker scripts while keeping `stm32h503.ld` as the included common script.

### WR-03: Idle Task Memory Contract Understates The Retained Stack Size

**Files modified:** `rust/crates/runtime-adapter/src/static_memory.rs`
**Commit:** 867debf51
**Applied fix:** Derived idle task stack depth from retained `configMINIMAL_STACK_SIZE` values for F4/G0 and H503 profiles with regression coverage.

### WR-04: Enabled Timer Task Memory Can Represent A Zero-Depth Stack

**Files modified:** `rust/crates/runtime-adapter/src/timer.rs`
**Commit:** b3b479e77
**Applied fix:** Made enabled timer task memory construction fallible and reject zero stack words with a targeted unit test.

### WR-05: Unsafe Scanner Can Fail On Harmless Comments Or Strings

**Files modified:** `tools/bazel/phase5_verify.py`
**Commit:** 33f45dc67
**Applied fix:** Stripped Rust comments and string literals before unsafe scanning and added verifier self-regression checks for false positives and real unsafe syntax.

## Verification

- `cargo test --all-features -p buddy-board-adapter -p buddy-runtime-adapter`
- `python3 tools/bazel/phase5_verify.py --all`
- `python3 -m py_compile tools/bazel/phase5_verify.py`

---

_Fixed: 2026-06-03T21:06:03Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
