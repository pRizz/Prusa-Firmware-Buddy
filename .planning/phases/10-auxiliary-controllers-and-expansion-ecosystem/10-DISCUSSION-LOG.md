# Phase 10: Auxiliary Controllers and Expansion Ecosystem - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-14T15:09:46.271Z
**Phase:** 10-Auxiliary Controllers and Expansion Ecosystem
**Mode:** Yolo
**Areas discussed:** Auxiliary parity surface, Build and packaging, Rust domain contracts, Known concerns, Verification and evidence

---

## Auxiliary parity surface

| Option | Description | Selected |
|--------|-------------|----------|
| Source-backed manifests | Preserve current C++/CMake reference behavior through explicit manifests for puppies, Dwarf, ModularBed, xBuddy Extension, MMU2, Modbus/RS485, toolchanger, dock/tool offset, startup flashing, and updates. | yes |
| Direct implementation first | Start by rewriting runtime behavior before establishing reference contracts. | no |
| Documentation only | Capture auxiliary behavior in prose without machine-checkable manifests. | no |

**User's choice:** Auto-selected source-backed manifests as the recommended default.
**Notes:** This matches prior Phase 5 through Phase 9 patterns and avoids overclaiming hardware behavior.

---

## Build and packaging

| Option | Description | Selected |
|--------|-------------|----------|
| Bazel-owned auxiliary surfaces | Add Bazel labels/manifests and `just phase10-verify` while treating CMake as reference evidence. | yes |
| Keep CMake authoritative | Leave auxiliary firmware/package behavior primarily under CMake. | no |
| Package-only scope | Verify generated package names without startup flashing, prebuilt paths, or skip-flash modes. | no |

**User's choice:** Auto-selected Bazel-owned auxiliary surfaces as the recommended default.
**Notes:** Phase 10 must include Dwarf, ModularBed, xBuddy Extension, MMU firmware, puppy descriptor, prebuilt binary, and skip-flash/update surfaces.

---

## Rust domain contracts

| Option | Description | Selected |
|--------|-------------|----------|
| Typed auxiliary states | Add pure Rust types for controller kind, runtime state, update mode, Modbus identity/request, MMU transport, dock/tool offset, fault class, and evidence class. | yes |
| Extend only existing feature gates | Only remove `OutOfScopePhase10` from Phase 6 feature gates. | no |
| Adapter-first modeling | Put behavior directly in runtime adapters before pure domain states exist. | no |

**User's choice:** Auto-selected typed auxiliary states as the recommended default.
**Notes:** Existing `ProductProfile`, `FeatureSet`, `ResourceSurface`, and runtime-adapter boundaries should be reused.

---

## Known concerns

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit concern dispositions | Disposition MMU availability/reporting, H503 xBuddy Extension special handling, Modbus timeout/accepted semantics, and resource/update risks in manifests and tests. | yes |
| Preserve silently | Keep behavior without naming known defects or fragile areas. | no |
| Fix opportunistically | Change reference behavior when it seems cleaner without intentional-delta evidence. | no |

**User's choice:** Auto-selected explicit concern dispositions as the recommended default.
**Notes:** Any behavior fix must be named as an intentional delta mapped to IFCE-06.

---

## Verification and evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Local deterministic verifier plus non-local evidence classes | Add Phase 10 verifier tests, `just phase10-verify`, Bazel labels, Rust checks, lifecycle validation, and honest simulator/hardware/manual evidence boundaries. | yes |
| Hardware required for green local verification | Require physical auxiliary hardware for the phase's normal local pass. | no |
| Minimal file existence checks | Verify only that new files exist. | no |

**User's choice:** Auto-selected local deterministic verifier plus non-local evidence classes as the recommended default.
**Notes:** Full physical auxiliary-controller, RS485, toolchanger/dock, MMU, long-run update, and cutover proof remain Phase 11 unless explicitly evidenced.

---

## the agent's Discretion

- Exact manifest names, schema field order, Rust type names, verifier helper layout, and fixture granularity may be chosen by the planner/executor.
- Prefer small, source-backed, standard-library-friendly artifacts over broad runtime rewrites.

## Deferred Ideas

- Full physical auxiliary-controller, RS485, toolchanger/dock, MMU, and long-run update proof remains Phase 11 cutover evidence unless Phase 10 adds explicit simulator or hardware-smoke artifacts.
- Replacing retained LightModbus, retained MMU vendor code, HAL/RTOS/runtime shells, or upstream auxiliary firmware with native Rust implementations beyond parity contracts remains v2 unless directly required for IFCE-06.
- New auxiliary-controller features unrelated to existing behavior parity remain out of scope for v1.
