# Phase 14: Simulator Evidence Gates - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-17T16:12:37.174Z
**Phase:** 14-Simulator Evidence Gates
**Mode:** Yolo
**Areas discussed:** Simulator proof scope, Traceability and artifact contract, Runner and developer workflow, Overclaim and safety boundaries

---

## Simulator Proof Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Single umbrella simulator gate | Simple maintainer headline but weak traceability and high overclaim risk. | |
| Flow-by-flow proof-scope matrix | Trace each simulator scenario to requirements, v1.0 evidence, artifacts, and residual non-simulator gates. | yes |
| Current pytest simulator wrapper only | Lowest implementation cost but weak maintainer review value and poor `SIM-03` coverage. | |
| Simulator-plus-mocked-hardware expansion | Broad apparent coverage but high risk of confusing mocks with hardware proof. | |

**User's choice:** Auto-selected recommended option: flow-by-flow proof-scope matrix.
**Notes:** Advisor research recommended a scenario matrix because Phase 11 already separates simulator, CI, hardware, and live-service evidence, and Phase 13 added durable evidence contract conventions.

---

## Traceability and Artifact Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 14-owned simulator evidence contract plus generated run manifest | Clear `SIM-*` ownership, mirrors Phase 13 contract/run-output split, and links to Phase 11 evidence rows. | yes |
| Extend Phase 13 CI evidence contract with simulator gates | Reuses retention vocabulary but blurs CI orchestration with simulator execution. | |
| Update Phase 11 evidence manifests directly with simulator result fields | Direct v1.0 attachment but mutates archived evidence and risks historical drift. | |

**User's choice:** Auto-selected recommended option: Phase 14-owned simulator evidence contract plus generated run manifest.
**Notes:** Advisor research recommended keeping Phase 14 ownership separate while citing Phase 11 requirement evidence, reference comparisons, cutover criteria, and retained-code rows.

---

## Runner and Developer Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated Phase 14 Python evidence runner over existing pytest simulator tests | Reuses `tests/integration` and `utils/simulator`, writes Phase 13-shaped artifacts, and exposes Bazel/just commands. | yes |
| Thin `simulator-parity` wrapper around pytest | Easy local smoke path but lacks durable run manifests and requirement traceability. | |
| Bazel-native simulator test targets | Strong Bazel status but higher hermeticity and runtime-state risk. | |
| Extend Phase 13 CI evidence runner directly | Single CI entrypoint but couples completed Phase 13 to slow/flaky simulator runtime. | |

**User's choice:** Auto-selected recommended option: dedicated Phase 14 Python evidence runner over existing pytest simulator tests.
**Notes:** Advisor research recommended `phase14_verify` / `phase14_verify_tests`, `just phase14-verify`, and generated outputs under `build/ci-evidence/phase14`.

---

## Overclaim and Safety Boundaries

| Option | Description | Selected |
|--------|-------------|----------|
| Context-only exclusion language | Fast but not enforceable against later manifest or summary drift. | |
| Simulator manifest with explicit hardware-only rows and verifier guards | Makes `SIM-03` machine-checkable and rejects simulator pass claims for hardware-only proof. | yes |
| Phase 13 CI artifact overlay for simulator evidence | Useful retention pattern but not sufficient classification by itself. | |
| Manual hardware-review checklist deferred to Phase 15/18 | Good roadmap boundary, but too weak for Phase 14 overclaim prevention. | |

**User's choice:** Auto-selected recommended option: simulator manifest with explicit hardware-only rows and verifier guards.
**Notes:** Advisor research recommended rejecting claims that simulator evidence proves physical watchdog timing, thermal/motion safety, physical media, MMU/RS485/toolchanger behavior, retained-code acceptance, reference demotion, or cutover completion.

---

## the agent's Discretion

- Exact simulator scenario IDs, artifact names, schema field order, status vocabulary, and verifier helper boundaries may be chosen during planning and implementation.
- The planner may choose one integrated plan or a small number of sub-tasks inside one plan.
- Prefer standard-library Python, JSON manifests, Bazel/just wrappers, and concise generated summaries over broad simulator framework rewrites.

## Deferred Ideas

- Hardware/safety/media/UI input/MMU/RS485/toolchanger evidence belongs to Phase 15.
- Live Connect/WUI/TLS/telemetry/proxy/transfer evidence belongs to Phase 16.
- Release-candidate artifact/signing/provenance evidence belongs to Phase 17.
- Retained-code acceptance and final reference-demotion approval belongs to Phase 18.
- Fully hermetic Bazel-native simulator tests can be revisited after Phase 14 establishes the evidence contract.
