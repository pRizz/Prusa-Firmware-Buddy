---
phase: 08-local-interface-and-workflow-parity
plan: 01
subsystem: ui-parity-manifests
tags: [phase8, ifce-01, gui, display-layouts, concern-dispositions, manifests]

# Dependency graph
requires:
  - phase: 01-reference-baseline-and-safety-envelope
    provides: Concern ledger and safety envelope for CL-008, CL-011, and crash dump boundaries.
  - phase: 07-persistence-storage-and-resource-compatibility
    provides: Resource, generated-output, localization, and font traceability consumed by GUI layout contracts.
provides:
  - Source-backed IFCE-01 GUI workflow manifest rows for screen stack, dialogs, menus, print controls, setup flows, Connect, PrusaLink, and warning/error surfaces.
  - Display-class layout contracts for 240x320 and 480x320 GUI defaults, print preview/progress, localization/fonts, warning dialogs, redscreens, and Connect registration.
  - GUI concern disposition rows for CL-008, CL-011, CL-003, and CL-019 with sensitive-data boundaries.
affects: [phase8, phase9-network-parity, phase10-auxiliary-runtime, phase11-cutover]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Source-backed JSON manifests with requirement_id and reference_sources canonical fields.
    - Local proof scoped to static/source manifest evidence with hardware, simulator, network, auxiliary, and cutover proof classified as non-local evidence.

key-files:
  created:
    - tools/bazel/manifests/phase8_gui_workflows.json
    - tools/bazel/manifests/phase8_display_layouts.json
    - tools/bazel/manifests/phase8_concern_dispositions.json
    - .planning/phases/08-local-interface-and-workflow-parity/08-01-SUMMARY.md
  modified: []

key-decisions:
  - "Represent Phase 8 IFCE-01 GUI parity first as source-backed JSON manifests before Rust verifier work claims coverage."
  - "Keep physical LCD, touch, timing-sensitive simulator, hardware, network service, auxiliary runtime, and cutover proof out of local manifest claims."
  - "Consume Phase 7 resource and generated-output manifests for GUI font/resource traceability instead of duplicating generator ownership."
  - "Disposition CL-008 and CL-011 without embedding credential, certificate, EEPROM, private-key, or crash dump byte material."

patterns-established:
  - "Workflow rows use semantic_action_id for print preview and print-control identities."
  - "Layout rows make 240x320 and 480x320 values explicit rather than using either class as a proxy."
  - "Concern rows include regression_guard objects for later verifier enforcement."

requirements-completed: [IFCE-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 8-2026-06-13T16-58-45
generated_at: 2026-06-13T18:12:17Z

# Metrics
duration: 8 min
completed: 2026-06-13
---

# Phase 08 Plan 01: GUI Manifest Foundation Summary

**Source-backed GUI workflow, display layout, localization, and concern disposition manifests for IFCE-01 local interface parity**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-13T18:03:30Z
- **Completed:** 2026-06-13T18:12:17Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Created `phase8_gui_workflows.json` with all required workflow row IDs, IFCE-01 mapping, source references, print semantic action IDs, icon resource IDs, and non-local evidence boundaries.
- Created `phase8_display_layouts.json` with explicit MINI 240x320 and large 480x320 layout/font/resource contracts and Phase 7 localization/resource traceability.
- Created `phase8_concern_dispositions.json` for CL-008, CL-011, CL-003, and CL-019 without sensitive bytes or secret material.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write GUI workflow manifest** - `4d8a6e540` (feat)
2. **Task 2: Write display layout and localization manifest** - `1820702d7` (feat)
3. **Task 3: Write GUI concern disposition manifest** - `57a30b0a9` (feat)

**Plan metadata:** pending final docs commit

## Files Created/Modified

- `tools/bazel/manifests/phase8_gui_workflows.json` - Source-backed workflow contracts for GUI stack, dialogs, menus, print controls, setup flows, Connect, PrusaLink, and warnings/errors.
- `tools/bazel/manifests/phase8_display_layouts.json` - Display-class layout, print preview/progress, localization/font/resource, warning, redscreen, and Connect registration contracts.
- `tools/bazel/manifests/phase8_concern_dispositions.json` - Concern disposition contracts for CL-008, CL-011, CL-003, and CL-019.

## Decisions Made

- Used the canonical `requirement_id` and `reference_sources` fields throughout the new Phase 8 manifests.
- Treated manifest/source checks as local evidence only; runtime display, simulator, hardware, network, auxiliary, and cutover proof remains non-local.
- Kept crash dump and credential-adjacent rows name-only and warning-text-only.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None - stub-pattern scan found no placeholder/TODO/FIXME/empty-data stubs in the three created manifest files.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for dependent Phase 8 domain and verifier work to consume the manifest rows. The current plan deliberately leaves hardware display, simulator flow, network service parity, auxiliary runtime parity, and final cutover evidence as later non-local proof.

## Self-Check: PASSED

- Found all created manifest and summary files.
- Found task commits `4d8a6e540`, `1820702d7`, and `57a30b0a9`.
- No STATE.md, ROADMAP.md, or REQUIREMENTS.md updates were made by this executor.

---
*Phase: 08-local-interface-and-workflow-parity*
*Completed: 2026-06-13*
