# Phase 6: Printing Core, Safety, and Feature Gates - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-04T09:48:48.542Z
**Phase:** 6 - Printing Core, Safety, and Feature Gates
**Mode:** Yolo
**Areas discussed:** Printing Behavior Parity, Safety And Recovery Gates, Feature Gate Matrix, Known Concern Dispositions, Verification Strategy

---

## Printing Behavior Parity

| Option | Description | Selected |
| --- | --- | --- |
| Reference-first fixture contracts | Capture retained Marlin/Buddy behavior as fixtures and typed contracts before Rust behavior is accepted. | yes |
| Direct Rust planner rewrite | Start replacing planner behavior immediately and rely on later parity checks. |  |
| Documentation only | Describe behavior expectations without executable fixtures or Rust policy types. |  |

**User's choice:** Reference-first fixture contracts.
**Notes:** Yolo recommendation selected the conservative behavior-parity path. This keeps C/C++/Marlin as the oracle while Rust gains typed policy and fixture identity surfaces.

---

## Safety And Recovery Gates

| Option | Description | Selected |
| --- | --- | --- |
| Typed safety policies with evidence classes | Model pure safety/recovery decisions locally and classify hardware/runtime behavior as simulator, hardware-smoke, or manual evidence. | yes |
| Claim local safety parity from static checks | Treat Rust host tests and static manifests as enough for safety-critical behavior. |  |
| Defer all safety work | Wait until Phase 11 to model safety and recovery behavior. |  |

**User's choice:** Typed safety policies with evidence classes.
**Notes:** Yolo recommendation selected the path consistent with the Phase 1 safety envelope and Phase 5 runtime-boundary audit.

---

## Feature Gate Matrix

| Option | Description | Selected |
| --- | --- | --- |
| Derive typed gates from reference sources | Build feature availability from validated product profiles, ProjectOptions, baseline evidence, and retained-code inventory. | yes |
| Freehand feature table | Manually duplicate feature combinations in Rust without source traceability. |  |
| Leave gates as raw booleans | Pass unchecked primitive feature flags through the system. |  |

**User's choice:** Derive typed gates from reference sources.
**Notes:** Yolo recommendation selected the typed invariant path from Bright Builds and prior Phase 4 decisions.

---

## Known Concern Dispositions

| Option | Description | Selected |
| --- | --- | --- |
| Concern-led fixtures and intentional deltas | Tie known printing/safety defects to fixtures or named intentional-delta evidence. | yes |
| Preserve everything silently | Keep reference defects without explicit notes or tests. |  |
| Fix opportunistically | Fix defects as encountered without requirement and fixture evidence. |  |

**User's choice:** Concern-led fixtures and intentional deltas.
**Notes:** Yolo recommendation selected the Phase 1 concern-led approach. Probe-analysis coupling, MMU hard-coded availability, home-screen print-start side effects, and fatal/crash paths must not drift invisibly.

---

## Verification Strategy

| Option | Description | Selected |
| --- | --- | --- |
| Phase-local verifier plus Rust tests | Add a Bazel/just Phase 6 verifier, focused Rust unit tests, schema checks, source coverage checks, and non-local evidence classification. | yes |
| Rely on final cutover only | Skip phase-local verification and defer checks to Phase 11. |  |
| Run only heavy firmware/simulator checks | Depend on expensive or hardware-bound suites without lightweight local gates. |  |

**User's choice:** Phase-local verifier plus Rust tests.
**Notes:** Yolo recommendation selected the same verification pattern used by Phases 4 and 5.

---

## the agent's Discretion

- Exact Rust module names and manifest schema.
- Exact fixture file layout and verifier implementation details.
- Which fixture surfaces are represented as checked local data versus non-local evidence requirements.

## Deferred Ideas

- Persistence, resources, GUI, network, transfer, and auxiliary-controller runtime behavior parity remain in later phases.
