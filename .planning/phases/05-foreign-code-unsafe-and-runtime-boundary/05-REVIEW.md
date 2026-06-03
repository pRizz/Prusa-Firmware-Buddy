---
phase: 05-foreign-code-unsafe-and-runtime-boundary
reviewed: 2026-06-03T20:56:43Z
depth: standard
files_reviewed: 26
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - rust/crates/board-adapter/Cargo.toml
  - rust/crates/board-adapter/src/clock.rs
  - rust/crates/board-adapter/src/dma.rs
  - rust/crates/board-adapter/src/ffi.rs
  - rust/crates/board-adapter/src/interrupt.rs
  - rust/crates/board-adapter/src/lib.rs
  - rust/crates/board-adapter/src/mcu.rs
  - rust/crates/board-adapter/src/memory_region.rs
  - rust/crates/board-adapter/src/mmio.rs
  - rust/crates/runtime-adapter/src/allocator.rs
  - rust/crates/runtime-adapter/src/lib.rs
  - rust/crates/runtime-adapter/src/linker.rs
  - rust/crates/runtime-adapter/src/panic_boundary.rs
  - rust/crates/runtime-adapter/src/queue.rs
  - rust/crates/runtime-adapter/src/startup.rs
  - rust/crates/runtime-adapter/src/static_memory.rs
  - rust/crates/runtime-adapter/src/synchronization.rs
  - rust/crates/runtime-adapter/src/task.rs
  - rust/crates/runtime-adapter/src/timer.rs
  - tools/bazel/BUILD.bazel
  - tools/bazel/manifests/foreign_code_inventory.json
  - tools/bazel/manifests/unsafe_boundary_audit.json
  - tools/bazel/phase5_verify.py
  - tools/bazel/rust_workflow.sh
findings:
  critical: 1
  warning: 5
  info: 0
  total: 6
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-06-03T20:56:43Z
**Depth:** standard
**Files Reviewed:** 26
**Status:** issues_found

## Summary

Reviewed the Phase 5 Rust adapter contracts, retained-code manifests, Bazel/just wiring, and verifier. The review applied repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the pinned Bright Builds architecture, code-shape, verification, testing, and Rust standards. No `.claude/skills` or `.agents/skills` project skills were present.

The current automated gates pass, but several contract bugs remain: the MMIO facade exposes safe arbitrary volatile pointer access, TaskDeps feature gates are flattened into unconditional masks, H503 linker selection loses the active boot/noboot wrapper, static/timer stack contracts can encode invalid runtime facts, and the unsafe verifier can false-positive on harmless comments or strings.

Verification run during review:

- `python3 tools/bazel/phase5_verify.py --quick` passed.
- `cargo test --all-features -p buddy-board-adapter -p buddy-runtime-adapter` passed: 39 unit tests.

## Critical Issues

### CR-01: Safe MMIO API Allows Arbitrary Volatile Reads And Writes

**File:** `rust/crates/board-adapter/src/mmio.rs:46`

**Issue:** `RegisterAddress::new` accepts any nonzero aligned `usize`, then `Register32::read` and `write` expose safe methods that dereference that address through `read_volatile`/`write_volatile` at lines 107 and 120. Nonzero alignment does not prove the address is a valid MCU peripheral register, scoped to the selected board, readable/writable for the requested width, or non-trapping. This makes safe Rust capable of arbitrary memory/MMIO access and can crash or corrupt firmware state.

**Fix:** Make arbitrary-address construction and access unsafe until a board-profile-validated peripheral range type exists, or require construction from a checked MCU MMIO region before safe reads/writes are available.

```rust
pub unsafe fn new_unchecked(
    address: usize,
    width: RegisterWidth,
) -> Result<Self, RegisterAddressError> {
    // existing nonzero/alignment checks
}

pub unsafe fn read(&self) -> u32 {
    core::ptr::read_volatile(self.address.as_const_ptr::<u32>())
}
```

Preferred longer-term fix: add a `McuMmioRegion`/`PeripheralRegisterBlock` produced from `ProductProfile` and reject addresses outside the selected MCU's register map before exposing safe `Register32::read/write`.

## Warnings

### WR-01: Feature-Gated TaskDeps Are Modeled As Unconditional Dependencies

**File:** `rust/crates/runtime-adapter/src/task.rs:250`

**Issue:** `DEFAULT_START_DEPS` and `BOOTSTRAP_DONE_DEPS` always include `PuppiesReady`, but the retained C++ masks include that bit only under `HAS_PUPPIES()` (`include/tasks.hpp:51-65`). `DependencyMaskRequirement::AllowEmpty` does not remove the dependency; it only permits an empty slice if one is supplied. Later consumers using `default_start` or `bootstrap_done` for MINI/MK4/non-puppy builds could wait for `puppies_ready` forever.

**Fix:** Make task dependency masks profile/feature aware, or encode feature-gated dependencies explicitly.

```rust
pub fn dependency_mask_for_profile(
    &self,
    profile: &ProductProfile,
) -> Result<DependencyMask, DependencyMaskError> {
    let has_puppies = profile.features().contains(Feature::Puppies);
    let dependencies = match self.name {
        "default_start" if !has_puppies => &[],
        "bootstrap_done" if !has_puppies => &[TaskDependency::ResourcesReady, TaskDependency::EspFlashed],
        _ => self.dependencies,
    };

    DependencyMask::from_dependencies(dependencies, self.dependency_requirement)
}
```

Add tests for a non-puppy profile and a puppy-enabled profile.

### WR-02: H503 Linker Contract Reports The Included Script As The Active Script

**File:** `rust/crates/runtime-adapter/src/linker.rs:92`

**Issue:** The H503 paths set `active_script_path` to `src/puppy/xbuddy_extension/stm32h503.ld`, but retained CMake selects `stm32h503_boot.ld` or `stm32h503_noboot.ld` as the linker script, and those wrappers include `stm32h503.ld`. This drops the boot/noboot distinction from the active contract while preserving it only as an available path.

**Fix:** Select the wrapper as the active script and keep `stm32h503.ld` as `maybe_included_script_path`.

```rust
fn h503_active_script_path(mode: BootloaderMode) -> &'static str {
    match mode {
        BootloaderMode::NoBoot => "src/puppy/xbuddy_extension/stm32h503_noboot.ld",
        BootloaderMode::Boot | BootloaderMode::Auxiliary => {
            "src/puppy/xbuddy_extension/stm32h503_boot.ld"
        }
    }
}
```

If auxiliary firmware needs both boot and noboot variants, introduce an explicit auxiliary linker mode instead of pointing `active_script_path` at the common include file.

### WR-03: Idle Task Memory Contract Understates The Retained Stack Size

**File:** `rust/crates/runtime-adapter/src/static_memory.rs:115`

**Issue:** `idle_task_callback()` hard-codes `stack_words: 1`, but the retained callback returns `configMINIMAL_STACK_SIZE` from `src/freertos/system_tasks.cpp` (128 words for F4/G0 configs and 32 words for xBuddy Extension). This makes the contract encode a stack size that is far smaller than the reference runtime.

**Fix:** Do not invent a representative stack depth. Carry the retained symbol, or select a validated profile/config value and reject zero.

```rust
pub fn idle_task_callback(stack_words: usize) -> Result<Self, StaticTaskMemoryError> {
    Self::new(
        "idle_task",
        stack_words,
        ".ccmram",
        "default RAM",
        "src/freertos/system_tasks.cpp owns persistent idle task storage",
    )
}
```

Add tests for F4/G0 and H503 expected `configMINIMAL_STACK_SIZE` values or keep the value symbolic.

### WR-04: Enabled Timer Task Memory Can Represent A Zero-Depth Stack

**File:** `rust/crates/runtime-adapter/src/timer.rs:36`

**Issue:** `TimerTaskMemory::enabled` accepts `stack_words` directly and never rejects zero. Static task and queue constructors already reject zero-sized runtime storage; timer-service memory should do the same because an enabled FreeRTOS timer task with zero stack words is not a valid contract.

**Fix:** Make the constructor fallible and reuse the same zero-stack invariant as `StaticTaskMemory`.

```rust
pub fn enabled(
    stack_depth_symbol: &'static str,
    stack_words: usize,
) -> Result<Self, TimerTaskMemoryError> {
    if stack_words == 0 {
        return Err(TimerTaskMemoryError::ZeroStackWords);
    }

    Ok(Self::Enabled { /* existing fields */ })
}
```

Add a unit test that `TimerTaskMemory::enabled("configTIMER_TASK_STACK_DEPTH", 0)` is rejected.

### WR-05: Unsafe Scanner Can Fail On Harmless Comments Or Strings

**File:** `tools/bazel/phase5_verify.py:360`

**Issue:** `unsafe_findings_for_file` searches raw source lines for substrings such as `unsafe {`, `unsafe fn`, `unsafe extern`, and `#[unsafe(` without stripping comments or string literals. That can make `--quick` fail when an unaudited safe file merely documents an unsafe invariant or contains a test string. The Rust test in `ffi.rs` already has to split these tokens with `concat!`, which is evidence that the verifier is sensitive to non-code text.

**Fix:** Tokenize or cheaply strip Rust comments and string literals before scanning. At minimum, ignore doc/comment-only lines and add regression tests for comments and string constants containing unsafe phrases.

```python
stripped = line.lstrip()
if stripped.startswith(("//", "//!","///")):
    continue
```

For a robust fix, use a small token-aware scanner or parse `cargo clippy`/Rust compiler diagnostics instead of raw substring matches.

---

_Reviewed: 2026-06-03T20:56:43Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
