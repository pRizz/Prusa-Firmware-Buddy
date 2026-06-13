# Phase 8: Local Interface and Workflow Parity - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-13T16:58:45.186Z
**Phase:** 8-local-interface-and-workflow-parity
**Mode:** Yolo
**Areas discussed:** GUI workflow parity surface, Display classes/layout/localization, Rust domain contracts, Known concerns and intentional deltas, Verification and lifecycle

---

## GUI Workflow Parity Surface

| Option | Description | Selected |
|--------|-------------|----------|
| Source-backed reference manifests | Capture screen stacks, dialogs, menus, wizards, print controls, setup/selftest/calibration flows, Connect registration entry surfaces, warnings, and redscreens with exact retained source paths and fixture identities. | yes |
| Prose-only parity description | Describe GUI parity expectations without machine-checkable row coverage. | |
| Implement GUI replacement directly | Start replacing GUI behavior before the parity surface is explicit. | |

**User's choice:** Auto-selected source-backed reference manifests.
**Notes:** This follows the Phase 3 through Phase 7 pattern and keeps IFCE-01 evidence auditable.

---

## Display Classes, Layout, and Localization

| Option | Description | Selected |
|--------|-------------|----------|
| Treat 240x320 and 480x320 as first-class dimensions | Preserve layout/localization behavior per supported display class and classify physical rendering/touch proof as non-local until simulator or hardware evidence exists. | yes |
| Generalize from one display class | Use one display surface as representative for both classes. | |
| Defer localization/layout contracts | Leave text, font, truncation, and resource display behavior to later phases. | |

**User's choice:** Auto-selected first-class display class and localization contracts.
**Notes:** Phase 8 is specifically scoped to local GUI parity across supported display classes, and Phase 7 already established resource/localization compatibility boundaries.

---

## Rust Domain Contracts

| Option | Description | Selected |
|--------|-------------|----------|
| Add pure typed GUI parity contracts | Model display class, workflow identity, dialog/warning/error surfaces, evidence classes, and manifest row identity in `buddy-domain` style with fallible constructors. | yes |
| Store GUI parity as loose JSON only | Keep all meaning in manifests and verifier string checks. | |
| Move behavior into adapters first | Put GUI behavior decisions directly in retained-code or simulator adapters. | |

**User's choice:** Auto-selected pure typed GUI parity contracts.
**Notes:** This preserves the functional-core/imperative-shell approach from earlier phases and keeps local behavior tests cheap.

---

## Known Concerns and Intentional Deltas

| Option | Description | Selected |
|--------|-------------|----------|
| Explicitly disposition GUI concerns | Track `CL-008`, crash dump warning UI, and GUI resource/layout concerns with source paths, evidence class, and intentional-delta status. | yes |
| Preserve concerns implicitly | Assume concern handling follows from general GUI parity coverage. | |
| Fix defects silently | Change behavior without intentional-delta mapping. | |

**User's choice:** Auto-selected explicit concern dispositions.
**Notes:** Prior phases require known defects to be preserved, fixed intentionally with evidence, or deferred explicitly.

---

## Verification and Lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror prior phase verifier pattern | Add Phase 8 verifier, Bazel labels, `just phase8-verify`, Rust checks, lifecycle validation, and overclaim guards. | yes |
| Rely on manual review | Use documentation review without repo-owned automated checks. | |
| Run only heavyweight firmware/simulator checks | Depend on slow or hardware-bound evidence as the main local gate. | |

**User's choice:** Auto-selected prior phase verifier pattern.
**Notes:** Local checks should be deterministic and honest about non-local display, simulator, hardware, network, auxiliary, and cutover evidence.

---

## the agent's Discretion

- Exact manifest names, schema field order, Rust type names, verifier helper names, and plan split are left to downstream planning as long as they satisfy the context decisions.
- Fixture granularity may be chosen during planning, with a bias toward one compatibility concern per fixture.

## Deferred Ideas

- Network service, TLS, transfer, and WUI API behavior parity belongs to Phase 9.
- Auxiliary-controller, MMU, toolchanger, and update runtime parity belongs to Phase 10.
- Full cutover evidence and hardware acceptance belong to Phase 11 unless Phase 8 creates a narrow prerequisite artifact.
