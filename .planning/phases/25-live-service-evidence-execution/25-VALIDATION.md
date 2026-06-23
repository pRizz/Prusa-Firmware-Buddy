# Phase 25: Live-Service Evidence Execution - Validation

**Validated:** 2026-06-23
**Scope:** EVID-03 live-service evidence execution

## Acceptance Samples

- A complete input packet with one row per Phase 16 scenario is accepted, retained, and summarized.
- Missing, duplicate, or unknown scenario rows are rejected.
- Phase 25 status is limited to `passed`, `failed`, `blocked`, and `exception-requested`.
- `pending-live-input`, `manual-live-service-required`, `controlled-service-required`, `blocked-credentials-unavailable`, `blocked-endpoint-unavailable`, and `not-applicable-with-justification` cannot pass as Phase 25 results.
- `exception-requested` rows require owner, rationale, evidence ref, and revisit condition.
- Service rows preserve Phase 16 service surface and mode.
- Passed live-service rows require live or controlled service observation evidence type.
- The source-contract boundary row requires source-contract validation evidence type.
- Artifact refs outside `build/ci-evidence/phase25/` or `external://phase25/` are rejected.
- Secret-bearing fields and text markers are rejected.
- Retained outputs include a run manifest, normalized results, redacted summary, upstream row, operator template, artifact summary, and source contract snapshots.
- Bazel, workflow, and `just` wiring expose Phase 25 tests and verification.

## Non-Local Proof Boundary

Quick mode is intentionally a blocked placeholder. It proves the local validation and retention path, not real Connect, WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, or crash-dump behavior.
