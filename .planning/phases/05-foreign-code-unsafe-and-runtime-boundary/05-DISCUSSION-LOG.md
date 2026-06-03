# Phase 5: Foreign Code, Unsafe, and Runtime Boundary - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-03T12:57:57.165Z
**Phase:** 5-Foreign Code, Unsafe, and Runtime Boundary
**Mode:** Yolo
**Areas discussed:** Retained foreign-code inventory, Unsafe and FFI boundary shape, STM32 startup/HAL/memory layout, FreeRTOS runtime orchestration, Verification strategy

---

## Retained Foreign-Code Inventory

| Option | Description | Selected |
|--------|-------------|----------|
| Full retained-code inventory | Track every retained C, C++, ASM, generated, and vendor surface with reason, source/version, owner, safe facade, replacement posture, risk, and evidence class. | yes |
| High-level prose only | Summarize retained code by subsystem without row-level traceability. | |
| Defer inventory to subsystem phases | Let later phases discover retained islands as needed. | |

**User's choice:** Full retained-code inventory (auto-selected recommended default).
**Notes:** This aligns with RUST-03 and the project constraint that untracked retained C/C++/ASM/vendor islands are out of scope.

---

## Unsafe And FFI Boundary Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Narrow adapter-local unsafe | Keep pure crates unsafe-free and place required unsafe/FFI/MMIO/static-memory work in documented adapter crates or modules. | yes |
| Workspace-wide unsafe allowance | Relax Rust unsafe policy across the workspace. | |
| Documentation-only unsafe notes | Describe unsafe surfaces without adding facade contracts or tests. | |

**User's choice:** Narrow adapter-local unsafe (auto-selected recommended default).
**Notes:** This carries forward Phase 4's `unsafe_code = "forbid"` posture for pure code while allowing Phase 5 to add deliberate boundary exceptions where needed.

---

## STM32 Startup, HAL, And Memory Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve and manifest startup/linker/HAL behavior | Retain startup assembly/linker/HAL where needed, wrap it with Rust boundary contracts, and verify by manifest/static checks plus explicit hardware/simulator evidence classes. | yes |
| Rewrite startup/linker immediately | Replace startup assembly and linker behavior now before all evidence is available. | |
| Leave startup as implicit CMake behavior | Keep startup/linker/HAL hidden in current build files without Rust/Bazel boundary artifacts. | |

**User's choice:** Preserve and manifest startup/linker/HAL behavior (auto-selected recommended default).
**Notes:** This supports CORE-01 without overclaiming hardware parity before simulator or hardware evidence exists.

---

## FreeRTOS Runtime Orchestration

| Option | Description | Selected |
|--------|-------------|----------|
| Typed runtime contracts | Model task identity, dependency readiness, static task memory, queues, timers, and startup ordering as Rust runtime-adapter contracts around retained FreeRTOS behavior. | yes |
| Direct raw FreeRTOS calls from application code | Let future subsystem code call retained FreeRTOS primitives directly. | |
| Defer RTOS modeling until printing parity | Wait until Phase 6 to model task orchestration. | |

**User's choice:** Typed runtime contracts (auto-selected recommended default).
**Notes:** This supports CORE-02 and prevents later subsystem phases from depending on unchecked RTOS primitives.

---

## Verification Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Phase verifier plus targeted Rust/Bazel checks | Add a Phase 5 verifier, expose it through Bazel/just, run Rust checks, and classify hardware/simulator evidence honestly. | yes |
| Manual review only | Rely on inventory inspection without executable checks. | |
| Full firmware/hardware gate locally | Require local full firmware and hardware evidence for every run. | |

**User's choice:** Phase verifier plus targeted Rust/Bazel checks (auto-selected recommended default).
**Notes:** This follows the Phase 2-4 verifier pattern and Bright Builds verification guidance without hiding hardware-bound work inside routine local checks.

---

## the agent's Discretion

- Exact inventory schema, artifact names, adapter module names, and verifier implementation details.
- Whether the retained-code inventory is pure Markdown, machine-readable manifest plus Markdown, or both, as long as downstream agents and maintainers can inspect it.
- How broad local static verification should be, provided non-local evidence remains explicit.

## Deferred Ideas

- Printing-core behavior parity and safety feature gates belong to Phase 6.
- Storage/resource compatibility belongs to Phase 7.
- GUI, network, transfer, and auxiliary behavior parity belong to Phase 8 through Phase 10.
- Replacing retained vendor/HAL/RTOS components with Rust alternatives is a v2/post-parity decision unless a v1 safety defect forces a narrow replacement.
