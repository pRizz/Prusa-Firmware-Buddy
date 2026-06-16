---
phase: 03-artifact-and-generator-parity
plan: 01
subsystem: build
tags: [bazel, artifacts, manifests, generated-files, verification]
requires:
  - Phase 1 reference baseline
  - Phase 2 Bazel facade
provides:
  - Phase 3 verifier CLI
  - Deterministic artifact packager helper
  - Normalized artifact manifest helper
  - Artifact metadata comparison helper
  - Generated-output drift helper
affects: [phase-3-artifact-parity, phase-11-cutover-evidence]
tech-stack:
  added: [standard-library Python helper scripts]
  patterns: [stage-aware verifier, evidence-classified reference status, read-only generated drift checks]
key-files:
  created:
    - tools/bazel/phase3_verify.py
    - tools/bazel/artifact_packager.py
    - tools/bazel/artifact_manifest.py
    - tools/bazel/artifact_metadata_compare.py
    - tools/bazel/generated_drift.py
  modified: []
key-decisions:
  - "Reference BBF/DFU formats are invoked through existing scripts when prerequisites exist; local fallback emits bootstrap/CI status evidence instead of non-reference encoders."
  - "Artifact manifests derive filename, size, and SHA-256 from actual files."
  - "Generated check mode writes only to temporary/output directories; update mode is the only source-writing path."
patterns-established:
  - "Phase helpers are standard-library Python with explicit self-tests."
  - "Verifier modes are split by artifact, manifest, drift, update, facade, reference-status, and reference-artifact gates."
requirements-completed: [BAZL-03, BAZL-05]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 3-2026-06-02T21-03-53
generated_at: 2026-06-03T01:49:11.582Z
duration: 35min
completed: 2026-06-03
---

# Phase 3 Plan 01 Summary

**Standard-library artifact, manifest, metadata comparison, drift, and verifier helpers for Phase 3**

## Performance

- **Duration:** 35 min
- **Completed:** 2026-06-03T01:49:11Z
- **Tasks:** 3 completed
- **Files modified:** 5 created

## Accomplishments

- Added `phase3_verify.py` with quick, artifact, manifest, drift, update, facade, reference-status, and reference-artifact verification gates.
- Added `artifact_packager.py` for deterministic package-surface smoke outputs and reference-format status classification.
- Added `artifact_manifest.py` to write normalized artifact metadata from actual files.
- Added `artifact_metadata_compare.py` to compare representative metadata and Phase 1 reference surfaces.
- Added `generated_drift.py` with a registry covering Phase 3 generated-output surfaces and a read-only check/update split.

## Task Commits

Task commits are intentionally deferred. The invoked wrapper requires no final commit or push before clean phase verification, so all Phase 3 changes remain uncommitted until the final wrapper gate passes.

## Files Created/Modified

- `tools/bazel/phase3_verify.py` - Phase 3 verification CLI.
- `tools/bazel/artifact_packager.py` - Package-surface smoke and BBF/DFU reference-status helper.
- `tools/bazel/artifact_manifest.py` - Normalized manifest writer.
- `tools/bazel/artifact_metadata_compare.py` - Metadata/reference comparison helper required by the local validation contract.
- `tools/bazel/generated_drift.py` - Generated-output check/update helper.

## Decisions Made

- Classified missing `utils/pack_fw.py --no-sign` prerequisites as `bootstrap-required`.
- Classified DFU reference-generation gaps as `ci-only` when the reference command cannot run in the current Bazel action context.
- Kept helper self-tests local and free of private keys, simulator flows, hardware checks, and full firmware builds.

## Deviations from Plan

- Added `artifact_metadata_compare.py` because the existing Phase 3 validation contract required it, even though the older plan frontmatter did not list it.

## Issues Encountered

- `utils/pack_fw.py` imports `ecdsa`, which is not installed in the current local Python environment. The packager therefore emits `bootstrap-required` reference status instead of claiming local BBF parity.

## User Setup Required

None for local smoke verification. Bootstrap/reference environments can run the guarded reference-format artifact target.

## Next Phase Readiness

Plan 02 can wire these helpers into Bazel artifact-producing labels, and Plan 03 can route generated-output checks through the same verifier surface.

---

*Phase: 03-artifact-and-generator-parity*
*Completed: 2026-06-03*
