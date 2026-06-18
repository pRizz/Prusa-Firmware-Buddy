# Phase 16: Live Network and Transfer Qualification - Research

**Researched:** 2026-06-18  
**Domain:** Live and controlled-service evidence contracts for Connect, PrusaLink/WUI, TLS, telemetry, proxy behavior, transfers, and secret-safe artifacts  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

All text in this section is copied from `.planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md`; it is the locked planning boundary for this phase. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

### Locked Decisions

## Implementation Decisions

### D-01: Phase Boundary and Ownership

**Decision**: Phase 16 owns live or controlled-service qualification evidence for Connect, PrusaLink/WUI, TLS, telemetry, proxy behavior, transfers, and secret-safe artifact handling.

**Implications**:
- Create a Phase 16 evidence contract and verifier rather than mutating archived Phase 9/11/13/14/15 evidence.
- Cover live/control-service behavior that prior source-backed and simulator phases explicitly left as non-local.
- Treat missing live credentials, endpoints, cert fixtures, or hardware/service access as explicit pending/blocking statuses, not as pass.
- Do not implement release/signing, retained-code final decisions, or hardware safety validation in this phase.

**Rationale**: Roadmap success criteria and requirements LIVE-01..LIVE-03 focus on reviewable live/control-service evidence and secret-safe artifacts.

### D-02: Scenario Coverage Contract

**Decision**: The Phase 16 contract must define row-level qualification scenarios for:
- Connect registration, telemetry, WebSocket commands, token/fingerprint behavior, and proxy limitations.
- PrusaLink/WUI HTTP API, digest auth, API-key auth, SNTP, mDNS, syslog, metrics, and transfer behavior.
- TLS, certificate behavior, credential redaction, negative protocol cases, long transfers, and crash-dump upload evidence.

**Implications**:
- Each row must map to LIVE-01, LIVE-02, or LIVE-03.
- Each row must cite source-backed manifests or prior phase contracts where applicable.
- The verifier must fail if required scenario groups or requirement mappings are missing.

**Rationale**: This directly mirrors the Phase 16 success criteria and keeps planning measurable.

### D-03: Live Evidence Status Model

**Decision**: Live/control-service rows must use explicit statuses such as `pending-live-input`, `manual-live-service-required`, `controlled-service-required`, `blocked-credentials-unavailable`, `passed`, `failed`, or `not-applicable-with-justification`.

**Implications**:
- Deterministic local checks can pass while live rows remain pending, as long as pending status is explicit and honest.
- The verifier must reject a `passed` status without corresponding operator evidence metadata or artifact references.
- The verifier must reject overclaiming language that implies live services were validated when only dry-run/source evidence exists.

**Rationale**: Prior phases use dry-run/pending models for non-local evidence; Phase 16 must not convert missing access into false assurance.

### D-04: Generated Artifact Policy

**Decision**: Generated Phase 16 artifacts should live under `build/ci-evidence/phase16` or another ignored build path.

**Implications**:
- Checked-in files should be limited to the contract, verifier, tests, docs/manifest definitions, Bazel/just wiring, and redaction rules.
- Generated run manifests, normalized result JSON, redacted summaries, and operator-input echoes must remain untracked.
- The verifier must fail if output paths escape the approved generated-artifact directory.

**Rationale**: Existing phase evidence runners use ignored `build/ci-evidence/...` directories and this keeps live evidence out of git by default.

### D-05: Secret-Safe Artifact Contract

**Decision**: Phase 16 must define a denylist and redaction contract for forbidden live artifacts, including but not limited to Connect tokens, registration codes, private fingerprints, Wi-Fi credentials, PrusaLink passwords/API keys, private certificates, signing keys, raw crash dumps, raw production payloads, and unredacted HTTP/TLS logs.

**Implications**:
- The verifier must scan operator evidence input and generated summaries for forbidden markers before accepting them.
- Only redacted summaries, fixture names, hash digests, external artifact references, and non-secret metadata should be committed or echoed.
- Private certs and credentials must be referenced by fixture name or external secret-store handle, not embedded content.

**Rationale**: Success criterion 4 requires that no secrets, tokens, or private certificates are committed to repository or planning artifacts.

### D-06: Redaction and Overclaim Guards

**Decision**: Add automated guards that reject:
- Secret-looking keys/values or private certificate blocks.
- Raw crash-dump payloads.
- Raw HTTP/TLS logs containing authorization, token, cookie, fingerprint, API key, or password values.
- Overclaim phrases such as “live passed” without operator evidence, or “production Connect validated” in dry-run output.

**Implications**:
- Tests must include negative fixtures proving forbidden content is rejected.
- Redacted summaries must preserve enough metadata for maintainers to review behavior without exposing secrets.

**Rationale**: Automated guardrails are the main protection against accidental credential leaks during live qualification.

### D-07: Tooling Shape

**Decision**: Implement a Phase 16 runner/verifier following the Phase 13/14/15 tooling pattern:
- `tools/bazel/phase16_live_network_evidence.py`
- `tools/bazel/phase16_live_network_evidence_test.py`
- `tools/bazel/manifests/phase16_live_network_evidence_contract.json`
- Bazel targets for verifier and tests.
- Root aliases/docs filegroups as needed.
- `tools/bazel/rust_workflow.sh` cases.
- `just phase16-verify`.

**Implications**:
- The runner should support deterministic local verification and an explicit operator/live evidence input mode.
- Prefer Python standard library and JSON over new dependencies.
- Keep the implementation thin and evidence-oriented rather than building a full test harness or live-service client.

**Rationale**: Phases 13-15 already establish the repository pattern for evidence contracts and Bazel/just integration.

### D-08: Deterministic Local Verification

**Decision**: Local verification must not require live credentials or network access.

**Implications**:
- Local `phase16-verify` should validate schema, required row coverage, source references, Bazel/just wiring, dry-run generation, redaction guards, and path safety.
- Real live/control-service evidence should be accepted through explicit input files/flags and marked pending when unavailable.

**Rationale**: The repo must stay testable by contributors and CI without private services or hardware access.

### D-09: Operator Evidence Input

**Decision**: The runner should accept an optional operator evidence JSON input containing live/control-service results, artifact references, redaction attestations, and residual risks.

**Implications**:
- The input schema must require scenario IDs, status, evidence type, operator notes, artifact references, redaction summary, and timestamp/build metadata.
- The runner must normalize accepted operator rows into generated output.
- Missing rows remain pending rather than failing the whole dry-run contract.

**Rationale**: Maintainers need a repeatable way to attach live evidence without committing private logs or credentials.

### D-10: Prior Evidence Traceability

**Decision**: Every Phase 16 scenario should cite relevant prior evidence where possible:
- Phase 9 network/transfer source-backed manifests.
- Phase 11 parity/cutover/reference comparison manifests.
- Phase 13 CI evidence contracts.
- Phase 14 simulator evidence contracts.
- Phase 15 hardware evidence contracts.
- Archived v1.0 release evidence where requirement lineage depends on it.

**Implications**:
- The contract should include source reference fields and the verifier should resolve them.
- The research/plan should avoid re-litigating already-locked local/source evidence unless it is needed to define live gaps.

**Rationale**: Phase 16 is an evidence completion layer, not a rewrite of earlier manifests.

### D-11: Connect-Specific Boundaries

**Decision**: Connect evidence should qualify current behavior for registration, telemetry/events, command channel behavior, token/fingerprint use, TLS/certificate behavior, proxy behavior, and transfers.

**Implications**:
- Evidence rows should distinguish approved live Connect, controlled Connect-compatible service, and source-only/dry-run evidence.
- Proxy limitations must be documented honestly rather than treated as full proxy support.
- Token/fingerprint handling must be redacted.

**Rationale**: LIVE-01 and LIVE-03 explicitly require these surfaces.

### D-12: WUI/PrusaLink-Specific Boundaries

**Decision**: WUI evidence should qualify API behavior, digest authentication, API-key authentication, SNTP, mDNS, syslog/metrics, and transfer behavior.

**Implications**:
- Evidence rows should allow simulator, controlled hardware, or controlled network-lab input where available.
- Authentication evidence must not expose passwords, API keys, digest responses, or session-sensitive headers.
- Metrics/syslog evidence should be summarized by collector fixture name, destination, and redacted sample classification rather than raw payloads if secrets could appear.

**Rationale**: LIVE-02 explicitly requires these surfaces.

### D-13: Transfer-Specific Boundaries

**Decision**: Transfer evidence should include long transfer, negative protocol, resume/range behavior, Connect-initiated transfer, WUI upload transfer, encrypted payload, storage/media edge cases where externally evidenced, and crash-dump upload boundary evidence.

**Implications**:
- The phase should not fake long-transfer or media-race evidence locally.
- The contract can mark storage/media hardware scenarios as pending hardware/operator evidence when prerequisites are absent.
- Crash-dump upload evidence must be redacted and must not commit raw dumps.

**Rationale**: LIVE-02 and LIVE-03 include transfer behavior, long transfers, negative protocol, and crash-dump upload evidence.

### D-14: No New Heavy Dependencies

**Decision**: Prefer Python standard library, Bazel shell wrappers, JSON contracts, and existing just workflow.

**Implications**:
- Do not add requests/aiohttp/docker orchestration/jsonschema unless the plan proves they are necessary.
- Avoid adding a live Connect mock server unless a future phase explicitly requests controlled-service automation.

**Rationale**: This phase is about evidence qualification and secret-safe manifests, not building new infrastructure.

### D-15: Lifecycle and Planning Integration

**Decision**: Use lifecycle ID `16-2026-06-18T01-09-34` for Phase 16 planning artifacts unless the orchestrator supersedes it.

**Implications**:
- Research and plan files should cite this lifecycle where relevant.
- Planner should keep one plan unless research finds a true need for split plans.

**Rationale**: The phase is cohesive and the GSD lifecycle check is currently valid.

### D-16: Explicit Non-Goals

**Decision**: Do not include:
- Release/signing finalization.
- Reference implementation demotion/removal.
- Full hardware safety sign-off.
- New production credentials or committed cert material.
- Broad soak/lab automation beyond operator evidence ingestion.

**Implications**:
- Mention these as out of scope or deferred when they come up during planning.
- Keep the plan focused on evidence contract, verifier, wiring, tests, and documentation.

**Rationale**: These are covered by later phases or future work and would expand Phase 16 beyond its success criteria.

## the agent's Discretion

- Exact scenario IDs and JSON field names are flexible if they remain traceable to LIVE-01..LIVE-03 and prior evidence.
- The runner can model live evidence as pending by default, as long as local verification proves the contract is complete and honest.
- The verifier may generate redacted summaries and source snapshots in any stable JSON shape that is easy for maintainers to inspect.
- The planner can choose whether to add a small docs file or rely on the contract README-style fields, provided maintainer workflow is discoverable through `just phase16-verify`.
- Test names and fixture layout are flexible, but tests must cover secret rejection, overclaim rejection, source-ref validation, path safety, required scenario coverage, and Bazel/just wiring.

## Deferred Ideas

- Release/signing qualification belongs to Phase 17.
- Retained code inventory, final source-reference decisions, and reference demotion belong to Phase 18.
- Full continuous live-service lab automation can be future work after Phase 16 establishes the contract and operator input format.
- Hardware safety evidence beyond network/transfer-related operator proof remains outside Phase 16.
- Production dashboards or long-running soak infrastructure are not required for this phase unless supplied as external artifact references.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LIVE-01 | Maintainer can run live or controlled evidence for Prusa Connect registration, telemetry, WebSocket commands, token/fingerprint behavior, and proxy limitations. | Plan Phase 16 rows around Phase 9 Connect contract rows for registration/token/fingerprint, telemetry/events, WebSocket `/p/ws`, proxy limitations, TLS, and Connect-initiated transfer; ingest operator evidence instead of requiring credentials in local CI. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: src/connect/connect.cpp; VERIFIED: doc/proxy_support.md] |
| LIVE-02 | Maintainer can run live or controlled evidence for PrusaLink/WUI HTTP API, digest/API-key auth, SNTP, mDNS, syslog, metrics, and transfer behavior. | Plan rows around Phase 9 WUI, network-service, and transfer contracts, plus source surfaces for WUI API handlers, digest/API-key auth, SNTP/mDNS/metrics/syslog configuration, and upload/transfer rendering. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json; VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json; VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp; VERIFIED: lib/WUI/nhttp/req_parser.cpp; VERIFIED: doc/metrics.md] |
| LIVE-03 | Maintainer can verify TLS, certificate, credential-redaction, negative protocol, long-transfer, and crash-dump upload evidence without committing secrets, tokens, or private certs. | Plan secret-safe rows and automated guards using the Phase 15 raw-input scanner pattern, Phase 14 explicit input split, Phase 9 TLS/transfer/crash-dump concerns, and current source behavior for TLS verification, custom DER certificate loading, transfer range/downloads, and crash-dump upload boundaries. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md; VERIFIED: src/connect/tls/tls.cpp; VERIFIED: src/transfers/download.cpp; VERIFIED: src/common/crash_dump/crash_dump_distribute.cpp] |
</phase_requirements>

## Summary

Phase 16 should be planned as an evidence-contract and verifier phase, not as a new live network client or service emulator. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] The closest implementation template is Phase 15: a JSON contract, a Python standard-library verifier, negative security tests, source-reference resolution, path-safety checks, generated redacted artifacts under `build/ci-evidence/...`, Bazel targets, `rust_workflow.sh` cases, and a `just` alias. [VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence_test.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile]

The prior phases already provide the source-backed network and transfer inventory that Phase 16 must qualify. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json; VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json] Phase 11 identifies live network/TLS/API evidence as a reference-comparison and cutover-readiness gate, while Phase 13/14/15 establish the repository evidence-runner pattern that Phase 16 should reuse. [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json; VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py]

The plan should treat live credentials, approved endpoints, private certificates, raw crash dumps, and unredacted HTTP/TLS logs as unavailable to local verification and forbidden in committed artifacts. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] Local verification should therefore prove schema completeness, traceability, redaction, path safety, source references, and workflow wiring, while optional operator evidence can move individual rows from `pending-live-input` to `passed`, `failed`, or blocked statuses only when metadata and external artifact references are present. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py]

**Primary recommendation:** Implement `tools/bazel/phase16_live_network_evidence.py` as a thin standard-library verifier/normalizer with contract-only, security-only, wiring-only, quick, and optional operator-evidence modes, backed by `tools/bazel/manifests/phase16_live_network_evidence_contract.json`, Bazel targets, tests, `rust_workflow.sh`, and `just phase16-verify`. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

## Project Constraints (from AGENTS.md)

- Repo-local instructions require reading `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant managed standards pages before planning or implementation work. [VERIFIED: AGENTS.md]
- No repo-local project skills exist under `.claude/skills/` or `.agents/skills/`, so Phase 16 planning does not need project-skill-specific patterns. [VERIFIED: find .claude/skills .agents/skills]
- The project is a Rust+Bazel firmware rewrite with behavior parity as a core constraint, Bazel as the authoritative build system, and `justfile` required for common workflows. [VERIFIED: AGENTS.md]
- Bright Builds standards require functional-core/imperative-shell structure, minimal nesting, clear data contracts, locally runnable verification, and unit tests that verify behavior. [VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards/core/architecture.md; VERIFIED: standards/core/code-shape.md; VERIFIED: standards/core/verification.md; VERIFIED: standards/core/testing.md]
- `standards-overrides.md` contains no active override, so the managed Bright Builds defaults apply. [VERIFIED: standards-overrides.md]
- For Rust changes, pre-commit rules require `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`; Phase 16 can avoid Rust changes by staying in Python/Bazel/just/docs wiring. [VERIFIED: AGENTS.md]
- New dependencies should be minimized; the locked Phase 16 decisions explicitly prefer Python standard library, Bazel wrappers, JSON contracts, and existing `just` workflow. [VERIFIED: AGENTS.md; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- Generated artifacts should stay out of git; `/build*` ignores `build/ci-evidence/phase16`. [VERIFIED: .gitignore; VERIFIED: git check-ignore build/ci-evidence/phase16/run-manifest.json]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python standard library (`argparse`, `json`, `pathlib`, `re`, `shutil`, `subprocess`, `unittest`) | Python 3.14.4 available locally | Contract validation, operator-evidence ingestion, redaction scanning, generated summaries, and unit tests | Phase 13/14/15 runners use Python standard-library tooling and Phase 16 explicitly avoids new heavy dependencies. [VERIFIED: python3 --version; VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| JSON contract manifests | Repository-local format | Row-level evidence schema, source references, requirement mapping, status vocabulary, and generated snapshots | Existing phase evidence contracts are JSON manifests under `tools/bazel/manifests/` and are validated by repository Python scripts. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json; VERIFIED: tools/bazel/manifests/phase14_simulator_evidence_contract.json; VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json] |
| Bazel shell targets via `tools/bazel/shell_rules.bzl` | Bazel 9.1.1 available locally | `phase16_verify` and `phase16_verify_tests` runnable targets | Phase 13/14/15 expose verifier/test entrypoints through Bazel targets in `tools/bazel/BUILD.bazel`. [VERIFIED: bazel --version; VERIFIED: tools/bazel/BUILD.bazel] |
| `tools/bazel/rust_workflow.sh` | Repository script | Stable workflow dispatcher used by Bazel shell targets and root aliases | Existing phase workflows add cases for verifier and tests in this script. [VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: tools/bazel/BUILD.bazel] |
| `just` | just 1.48.0 available locally | Maintainer-facing command `just phase16-verify` | Phase 13/14/15 already expose phase verification through `just phase13-verify`, `just phase14-verify`, and `just phase15-verify`. [VERIFIED: just --version; VERIFIED: justfile] |
| Ignored generated output directory | `build/ci-evidence/phase16` | Run manifest, normalized results, redacted summaries, contract snapshots, and operator evidence echoes | Phase 13/14/15 use ignored `build/ci-evidence/...` directories and `.gitignore` ignores `/build*`. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: .gitignore] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| `jq` | jq 1.7.1 available locally | Research-time inspection of JSON manifests | Useful for maintainers during planning/review, but should not be a Phase 16 verifier runtime dependency. [VERIFIED: jq --version; VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| External artifact store / lab notes | Not supplied in repo | Holding raw live logs, raw crash dumps, private certs, and credential-bearing material outside git | Use only by reference in operator evidence, with redacted summaries committed or generated locally. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Approved live or controlled Connect-compatible service | Not supplied in repo | Operator evidence for registration, telemetry, WebSocket commands, proxy/TLS behavior, and Connect transfers | Required for `passed` live rows; absent service access should remain `pending-live-input` or `controlled-service-required`. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json] |
| Controlled WUI-capable printer or simulator endpoint | Not supplied in repo | Operator evidence for PrusaLink/WUI API, auth, SNTP/mDNS/syslog/metrics, and transfer behavior | Required for live/control rows; local verifier should not require it. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Explicit Python contract checks | `jsonschema` package | Avoid `jsonschema`; Phase 13/14/15 already use explicit stdlib validation and Phase 16 locked decisions avoid new heavy dependencies. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Operator evidence input | New live Connect/WUI automation harness | Avoid building automation now; Phase 16 is scoped to evidence qualification and explicitly defers broad lab automation. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Redacted artifact references | Committed raw HTTP/TLS logs or crash dumps | Raw logs and crash dumps are forbidden because they may contain credentials or sensitive data. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: src/gui/screen_home.cpp] |
| Bazel/just wiring | Standalone ad hoc script only | Use Bazel and `just` so maintainers get the same workflow shape as Phases 13/14/15. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile] |

**Installation:** No new packages are required for the recommended Phase 16 implementation. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

```bash
# No npm/pip package installation is needed.
python3 tools/bazel/phase16_live_network_evidence.py --quick
```

**Version verification:** The local planning environment has Python 3.14.4, Bazel 9.1.1, just 1.48.0, and jq 1.7.1 available. [VERIFIED: python3 --version; VERIFIED: bazel --version; VERIFIED: just --version; VERIFIED: jq --version]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase16_live_network_evidence.py             # stdlib verifier, quick generator, operator-evidence normalizer
├── phase16_live_network_evidence_test.py        # stdlib unittest coverage for schema, security, paths, wiring
├── BUILD.bazel                                  # phase16_verify and phase16_verify_tests targets
├── rust_workflow.sh                             # phase16_verify and phase16_verify_tests cases
└── manifests/
    └── phase16_live_network_evidence_contract.json

build/ci-evidence/phase16/                       # ignored generated output, never committed
├── run-manifest.json
├── normalized-live-network-results.json
├── redacted-live-network-summary.json
├── source-contract-snapshot.json
└── operator-evidence-input.json
```

This structure matches the existing phase evidence runner pattern and uses an ignored output directory. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: .gitignore]

### Pattern 1: Row-Level Evidence Contract

**What:** Define one JSON row per live/control-service scenario, with explicit requirement IDs, source refs, service surface, evidence mode, required input kind, default status, allowed statuses, forbidden artifact classes, and pass/fail semantics. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

**When to use:** Use this for every LIVE-01, LIVE-02, and LIVE-03 behavior so the verifier can detect missing coverage before any live evidence is supplied. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

**Example:**

```json
{
  "id": "live-connect-websocket-command-channel",
  "requirement_ids": ["LIVE-01"],
  "service_surface": "connect",
  "evidence_mode": "live-or-controlled-service",
  "default_status": "pending-live-input",
  "allowed_statuses": [
    "pending-live-input",
    "manual-live-service-required",
    "controlled-service-required",
    "blocked-credentials-unavailable",
    "passed",
    "failed",
    "not-applicable-with-justification"
  ],
  "source_contract_refs": [
    "tools/bazel/manifests/phase9_connect_contracts.json#connect-command-polling-websocket"
  ],
  "forbidden_artifacts": ["token", "fingerprint", "raw-http-log", "raw-tls-log"]
}
```

The exact field names can vary, but the contract needs enough structure to validate coverage, status honesty, source refs, and secret-safe artifact handling. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/phase15_hardware_evidence.py]

### Pattern 2: Deterministic Quick Mode

**What:** `--quick` should validate the contract, source references, security rules, wiring, and output path, then generate redacted local artifacts with live rows left pending by default. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py]

**When to use:** Use it for CI and local contributor verification because live credentials and services are not required locally. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

**Expected artifacts:** `run-manifest.json`, `normalized-live-network-results.json`, `redacted-live-network-summary.json`, `source-contract-snapshot.json`, and optional `operator-evidence-input.json` under `build/ci-evidence/phase16`. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py]

### Pattern 3: Operator Evidence Input

**What:** Accept an optional JSON object such as `{ "evidence_rows": [...] }` or a top-level list, scan the raw text for forbidden content before parsing, then normalize only rows that satisfy status, metadata, artifact-ref, and redaction requirements. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]

**When to use:** Use this when a maintainer runs a live or controlled-service qualification outside CI and wants to attach secret-safe evidence references. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

**Required metadata:** scenario ID, status, evidence type, timestamp, operator or lab identifier, firmware/build identifier, service mode, redaction summary, external artifact reference, residual risk, and no raw secrets. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/phase15_hardware_evidence.py]

### Pattern 4: Source-Reference Resolution

**What:** Resolve source refs as repo-relative `path#row-id` entries and recursively search known row containers so Phase 16 rows prove traceability to Phase 9/11/13/14/15 evidence. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]

**When to use:** Use this for every row with prior source-backed evidence or previous phase lineage. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

**Primary source-ref files:** Phase 9 Connect, WUI, network-service, transfer manifests; Phase 11 parity/cutover/reference manifests; Phase 13/14/15 contracts and verification summaries. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json; VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json; VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json; VERIFIED: tools/bazel/manifests/phase14_simulator_evidence_contract.json; VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]

### Pattern 5: Workflow Wiring

**What:** Add Bazel targets, root aliases/docs filegroups, `rust_workflow.sh` cases, and a `just phase16-verify` recipe that runs tests before the verifier. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

**When to use:** Use this so Phase 16 follows the repository’s existing evidence workflow and maintainer entrypoints. [VERIFIED: AGENTS.md; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

### Required Scenario Groups

| Group | Recommended Scenario IDs | Source Backing |
|-------|--------------------------|----------------|
| Connect registration, tokens, fingerprints | `live-connect-registration-token-fingerprint`, `live-connect-token-fingerprint-persistence` | Phase 9 Connect registration/token rows and source headers using `Fingerprint` and `Token`. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: src/connect/connect.cpp] |
| Connect telemetry and events | `live-connect-telemetry-events` | Phase 9 telemetry/events row and source POSTs to `/p/telemetry` and `/p/events`. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: src/connect/connect.cpp] |
| Connect WebSocket commands | `live-connect-websocket-command-channel` | Phase 9 command polling/WebSocket row and source upgrade request to `/p/ws`. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: src/connect/connect.cpp] |
| Connect proxy limitations | `live-connect-proxy-limitations` | Proxy docs and source show CONNECT proxy support without auth and TLS-gated proxy selection. [VERIFIED: doc/proxy_support.md; VERIFIED: src/common/http/proxy.cpp; VERIFIED: src/connect/connection_cache.cpp] |
| WUI API and auth | `live-wui-api-v1-status-job-files-transfer`, `live-wui-digest-auth-nonce-stale`, `live-wui-api-key-auth` | Phase 9 WUI rows and WUI request parser/status page/API sources. [VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp; VERIFIED: lib/WUI/nhttp/req_parser.cpp; VERIFIED: lib/WUI/nhttp/status_page.cpp] |
| Local network services | `live-wui-sntp-clock-update`, `live-wui-mdns-discovery`, `live-metrics-syslog-udp-collector` | Phase 9 network-service rows and metrics/syslog docs/source. [VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json; VERIFIED: doc/metrics.md; VERIFIED: src/common/metric_handlers.cpp; VERIFIED: src/syslog/syslog_transport.cpp] |
| Transfers | `live-wui-upload-transfer-behavior`, `live-connect-transfer-download`, `live-transfer-long-range-resume`, `live-transfer-encrypted-download`, `live-transfer-negative-protocol` | Phase 9 transfer rows and WUI upload/download/range source behavior. [VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json; VERIFIED: lib/WUI/nhttp/gcode_upload.cpp; VERIFIED: lib/WUI/nhttp/transfer_renderer.cpp; VERIFIED: src/transfers/download.cpp] |
| TLS, certificates, crash dump boundary | `live-connect-tls-certificate-policy`, `live-custom-der-certificate-fixture`, `live-crash-dump-upload-redacted-boundary` | Phase 9/11 TLS and crash-dump gaps plus TLS and crash-dump source behavior. [VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md; VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; VERIFIED: src/connect/tls/tls.cpp; VERIFIED: src/common/crash_dump/crash_dump_distribute.cpp; VERIFIED: src/gui/screen_home.cpp] |

### Anti-Patterns to Avoid

- **Committing raw live evidence:** Commit only contracts, verifier code, tests, and docs; keep generated live artifacts under ignored build paths or external artifact references. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: .gitignore]
- **Treating dry-run evidence as live pass:** A deterministic local run can validate the process but must keep live rows pending unless operator evidence is supplied. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py]
- **Mutating archived evidence:** Phase 16 should cite Phase 9/11/13/14/15 artifacts instead of rewriting them. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- **Using shell strings for external commands:** If any external command is added, use list-form `subprocess.run` with `shell=False`, matching the existing runner pattern. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: AGENTS.md]
- **Adding a dependency-heavy live harness:** The locked decision is a thin evidence-oriented runner using Python stdlib and JSON. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Live Connect cloud replacement | A fake production Connect server in Phase 16 | Operator evidence input with `live` or `controlled-service` mode | Phase 16 is scoped to evidence qualification, and broad lab automation is deferred. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Secret scanning from scratch without tests | Ad hoc string checks only in generated summaries | Phase 15 raw-input-before-parse scanner pattern plus negative fixtures | Phase 15 already validates forbidden text in raw operator input before JSON parsing. [VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence_test.py] |
| Schema validation through prose review | Manual checklist without executable checks | Explicit Python contract checks and `unittest` coverage | Phase 13/14/15 runners fail on missing required rows, invalid paths, and broken wiring. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| TLS certificate parser or crypto harness | Custom TLS/cert parser in evidence tooling | Source references plus operator evidence metadata, fixture names, and redacted outcomes | The firmware already uses mbedTLS; Phase 16 should qualify evidence, not implement cryptography. [VERIFIED: src/connect/tls/tls.cpp; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| WUI/HTTP behavior simulator | New web server clone | Existing WUI source refs plus operator/simulator evidence rows | The repository already has WUI source surfaces and Phase 9 WUI contracts; Phase 16 should complete live/control evidence. [VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp] |
| Transfer stress system | Local synthetic long-transfer pass with no operator proof | Pending rows plus operator evidence for long transfer, range/resume, encrypted payload, and media races | Phase 9 identifies long-transfer/media-race cases as non-local evidence gaps. [VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json; VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md] |

**Key insight:** The hard part of Phase 16 is not protocol implementation; it is producing honest, traceable, secret-safe evidence for behaviors that cannot be proven by local source tests alone. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md]

## Common Pitfalls

### Pitfall 1: Quick Mode Overclaims Live Qualification

**What goes wrong:** `just phase16-verify` passes and generated summaries imply production or live-service validation happened. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
**Why it happens:** Existing phase verifiers are locally deterministic, but Phase 16 has live/control-service requirements. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py]  
**How to avoid:** Keep default live statuses as `pending-live-input`, `manual-live-service-required`, or `controlled-service-required` and reject `passed` without operator evidence metadata. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
**Warning signs:** Generated summaries contain phrases such as `production Connect validated` or `live passed` without artifact references. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

### Pitfall 2: Partial Redaction

**What goes wrong:** Raw operator JSON, raw logs, or raw crash dumps contain tokens, fingerprints, API keys, passwords, private certs, or sensitive crash content. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: src/gui/screen_home.cpp]  
**Why it happens:** Scanning only parsed fields can miss forbidden content outside expected keys. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]  
**How to avoid:** Scan the raw input text before JSON parsing, then scan generated summaries as a second guard. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]  
**Warning signs:** Operator evidence includes `Authorization`, `Token`, `Fingerprint`, `ApiKey`, private certificate blocks, cookie headers, or raw dump bytes. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

### Pitfall 3: Artifact Path Escape

**What goes wrong:** Generated artifacts or referenced local paths escape the approved output directory and can expose local files. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]  
**Why it happens:** Evidence tooling receives operator-provided paths. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
**How to avoid:** Reuse the Phase 15 repo-relative and output-directory checks for all generated paths and source references. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]  
**Warning signs:** Input contains `..`, absolute paths outside repo/build output, or symlink-like artifact refs presented as local evidence. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]

### Pitfall 4: Proxy Support Is Overstated

**What goes wrong:** Evidence says proxy behavior is fully supported or encrypted end-to-end through the printer-to-proxy hop. [VERIFIED: doc/proxy_support.md]  
**Why it happens:** Proxy docs and source implement minimal proxy support with limitations. [VERIFIED: doc/proxy_support.md; VERIFIED: src/common/http/proxy.cpp; VERIFIED: src/connect/connection_cache.cpp]  
**How to avoid:** Scenario rows should explicitly qualify the documented proxy limitations, including no proxy authentication and TLS-gated proxy selection. [VERIFIED: doc/proxy_support.md; VERIFIED: src/connect/connection_cache.cpp]  
**Warning signs:** Row titles or summaries say `full proxy support`, `authenticated proxy`, or `private printer-to-proxy TLS` without evidence. [VERIFIED: doc/proxy_support.md]

### Pitfall 5: Custom DER Certificate Behavior Is Treated As Proven

**What goes wrong:** Phase 16 marks custom certificate behavior passed based only on source existence. [VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md]  
**Why it happens:** Phase 9 flagged TLS/custom cert evidence as non-local, and the current TLS source contains a custom DER file path/parse flow that needs live or fixture evidence. [VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md; VERIFIED: src/connect/tls/tls.cpp]  
**How to avoid:** Require operator evidence for valid, missing, and invalid custom DER fixture behavior, with cert material referenced by fixture name only. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json]  
**Warning signs:** The row passes without a fixture name, cert outcome, TLS server identity class, and redaction attestation. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

### Pitfall 6: Crash-Dump Upload Evidence Leaks Sensitive Data

**What goes wrong:** A raw crash dump or upload payload gets copied into generated artifacts or planning docs. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: src/gui/screen_home.cpp]  
**Why it happens:** The UI warns crash dumps may include unencrypted sensitive information, and the source upload path can be configured to send dumps externally. [VERIFIED: src/gui/screen_home.cpp; VERIFIED: src/common/crash_dump/crash_dump_distribute.cpp]  
**How to avoid:** Accept only redacted summaries, fixture names, hashes, and external artifact references. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
**Warning signs:** Evidence includes binary dump data, memory extracts, unredacted URLs, or payload bodies. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

## Code Examples

Verified patterns from existing repository evidence runners:

### Raw Operator Input Scanner

```python
def load_operator_evidence_path(path: Path) -> object:
    raw_text = path.read_text(encoding="utf-8")
    reject_forbidden_text(raw_text, f"operator evidence {path}")
    return json.loads(raw_text)
```

Use this pattern so forbidden content is rejected before JSON parsing or normalization. [VERIFIED: tools/bazel/phase15_hardware_evidence.py]

### Honest Default Status

```python
def default_status_for(row: dict[str, object]) -> str:
    if row.get("evidence_mode") == "live-or-controlled-service":
        return "pending-live-input"
    return "source-contract-passed"
```

This mirrors the existing split between source/contract proof and non-local evidence while preventing dry-run overclaiming. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

### External Command Guard

```python
completed = subprocess.run(
    ["python3", "tools/bazel/phase16_live_network_evidence.py", "--contract-only"],
    check=False,
    capture_output=True,
    text=True,
)
```

Use list-form `subprocess.run` and keep `shell=False` if Phase 16 tests need to invoke the runner. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: AGENTS.md]

### Source Reference Shape

```json
{
  "source_contract_refs": [
    "tools/bazel/manifests/phase9_transfer_contracts.json#transfer-range-request",
    "tools/bazel/manifests/phase11_reference_comparisons.json#ref-network-tls-api-behavior"
  ]
}
```

Use repo-relative `path#row-id` refs so the verifier can resolve traceability across prior phase artifacts. [VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 9 source inventory only | Phase 16 should layer live/control-service qualification rows on top of Phase 9 Connect/WUI/network/transfer manifests | Phase 16 planning lifecycle `16-2026-06-18T01-09-34` | Planner should cite Phase 9 rows and fill non-local evidence gaps, not rewrite source inventory. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json; VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Phase 11 cutover/reference gates as pending | Phase 16 should make live network/TLS/API evidence reviewable with secret-safe refs | Phase 16 follows Phase 11 parity/cutover/reference manifests | Phase 16 can reduce open cutover risk without making release/signing or reference-demotion decisions. [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Phase 13 CI evidence retention | Phase 16 should reuse generated run manifests, source snapshots, redacted summaries, and workflow wiring | Phase 13 introduced CI evidence runner pattern | Use the same artifact hygiene and Bazel/just integration pattern. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile] |
| Phase 14 simulator dry-run plus explicit real input | Phase 16 should use deterministic local checks plus explicit operator/live evidence input | Phase 14 introduced simulator input split | Missing live inputs should be pending, not pass or fail the local contract. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Phase 15 hardware operator evidence | Phase 16 should reuse the raw-input scanner, operator row normalization, path safety, and overclaim guards | Phase 15 introduced hardware evidence input validation | This is the strongest existing local pattern for secret-safe non-local evidence ingestion. [VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence_test.py] |

**Deprecated/outdated:** Treating local source evidence as sufficient for live Connect/WUI/TLS/transfer qualification is out of scope for Phase 16; Phase 9 and Phase 11 both preserve non-local evidence gaps that need live or controlled-service operator proof. [VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md; VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json]

## Assumptions Log

All claims in this research were verified or cited in this session; no `[ASSUMED]` claims are intentionally included. [VERIFIED: this research file source tags]

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | No assumed claims recorded. | — | — |

## Open Questions

1. **Which approved Connect endpoint or controlled Connect-compatible service will maintainers use?**  
   What we know: Phase 16 requires Connect registration, telemetry, WebSocket, token/fingerprint, proxy, TLS, and transfer evidence. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
   What's unclear: No endpoint, credential source, or registration fixture is present in the repo or phase context. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
   Recommendation: Keep rows pending by default and require operator evidence with redacted external artifact refs for `passed`. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

2. **Will custom DER certificate behavior be fixed before live qualification or recorded as current behavior?**  
   What we know: Phase 9 flagged TLS/custom cert evidence as non-local, and the TLS source has a custom DER certificate load/parse path. [VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md; VERIFIED: src/connect/tls/tls.cpp]  
   What's unclear: Phase 16 scope asks for evidence, not necessarily a firmware fix. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
   Recommendation: Plan a row that captures current behavior and residual risk; only plan code changes if the implementation phase explicitly accepts firmware fixes. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

3. **Where should external live artifacts be stored?**  
   What we know: Raw credentials, certs, HTTP/TLS logs, crash dumps, and production payloads must not be committed. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
   What's unclear: The repo does not define a private artifact store or retention location for Phase 16 live logs. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
   Recommendation: Make the contract require external artifact references plus redacted summaries, leaving storage policy to maintainers. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

4. **Which metrics/syslog collector setup is approved for live evidence?**  
   What we know: Metrics docs describe G-code configuration and a local collector stack, and source sends metrics through syslog transport. [VERIFIED: doc/metrics.md; VERIFIED: src/common/metric_handlers.cpp; VERIFIED: src/syslog/syslog_transport.cpp]  
   What's unclear: No active collector or operator fixture is supplied in Phase 16 context. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]  
   Recommendation: Let operator evidence name the collector fixture and redact payload samples; keep local verifier network-free. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 16 verifier/tests | Yes | 3.14.4 | None needed. [VERIFIED: python3 --version] |
| Bazel | `phase16_verify` and `phase16_verify_tests` targets | Yes | 9.1.1 | None needed. [VERIFIED: bazel --version] |
| just | Maintainer command `just phase16-verify` | Yes | 1.48.0 | Direct Bazel targets if needed. [VERIFIED: just --version; VERIFIED: justfile] |
| jq | Research-time manifest inspection | Yes | 1.7.1 | Python JSON tools; jq should not be required by the runner. [VERIFIED: jq --version; VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| Live Connect credentials/registration code/endpoint | LIVE-01 and LIVE-03 operator proof | No | — | `pending-live-input`, `manual-live-service-required`, or `blocked-credentials-unavailable`. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Controlled Connect-compatible service | LIVE-01 and LIVE-03 controlled-service proof | No | — | `controlled-service-required` until supplied. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| WUI-capable printer/simulator endpoint with auth | LIVE-02 operator proof | No | — | `pending-live-input` with operator evidence mode. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| TLS cert fixtures/private cert material | LIVE-03 TLS/certificate proof | No committed material | — | Reference fixture names or external secret-store handles only. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Metrics/syslog collector | LIVE-02 metrics/syslog proof | Not supplied | — | Operator evidence with redacted collector fixture summary. [VERIFIED: doc/metrics.md; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Raw crash dumps | LIVE-03 crash-dump upload boundary | Must not be committed | — | Redacted summaries, hashes, and external artifact refs only. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: src/gui/screen_home.cpp] |

**Missing dependencies with no fallback:** None for deterministic local verification; live proof remains pending until maintainers supply external inputs. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

**Missing dependencies with fallback:**
- Live Connect credentials/endpoints and controlled services fall back to explicit pending/blocking statuses in local verification. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- WUI hardware/simulator endpoints fall back to operator evidence input and pending local rows. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- Private certs, raw logs, and crash dumps fall back to fixture names, hashes, redacted summaries, and external artifact references. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

## Validation Architecture

`workflow.nyquist_validation` is explicitly enabled, so Phase 16 planning needs validation architecture. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` on Python 3.14.4. [VERIFIED: python3 --version; VERIFIED: tools/bazel/phase15_hardware_evidence_test.py] |
| Config file | `tools/bazel/manifests/phase16_live_network_evidence_contract.json` to be created. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Quick run command | `python3 tools/bazel/phase16_live_network_evidence.py --quick`. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| Full suite command | `just phase16-verify` after adding the recipe and Bazel targets. [VERIFIED: justfile; VERIFIED: tools/bazel/BUILD.bazel] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| LIVE-01 | Connect registration, telemetry, WebSocket commands, token/fingerprint behavior, proxy limitations have contract rows, source refs, honest pending defaults, and operator-evidence validation. | unit + contract + quick smoke | `python3 tools/bazel/phase16_live_network_evidence_test.py -k connect` and `python3 tools/bazel/phase16_live_network_evidence.py --quick` | No; Wave 0 creates runner, tests, and contract. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json] |
| LIVE-02 | WUI API, digest/API-key auth, SNTP, mDNS, syslog, metrics, and transfer behavior have rows, source refs, pending defaults, and secret-safe evidence input. | unit + contract + quick smoke | `python3 tools/bazel/phase16_live_network_evidence_test.py -k wui` and `python3 tools/bazel/phase16_live_network_evidence.py --quick` | No; Wave 0 creates runner, tests, and contract. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json; VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json] |
| LIVE-03 | TLS/cert, redaction, negative protocol, long-transfer, and crash-dump upload rows reject forbidden secrets and overclaims while accepting redacted external refs. | unit + security negative tests + quick smoke | `python3 tools/bazel/phase16_live_network_evidence_test.py -k security` and `python3 tools/bazel/phase16_live_network_evidence.py --security-only --quick` | No; Wave 0 creates runner, tests, and contract. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: src/connect/tls/tls.cpp; VERIFIED: src/common/crash_dump/crash_dump_distribute.cpp] |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase16_live_network_evidence_test.py` and `python3 tools/bazel/phase16_live_network_evidence.py --quick`. [VERIFIED: tools/bazel/phase15_hardware_evidence_test.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py]
- **Per wave merge:** Run `just phase16-verify` after Bazel/just wiring is added. [VERIFIED: justfile; VERIFIED: tools/bazel/BUILD.bazel]
- **Phase gate:** `just phase16-verify`, `bazel run //tools/bazel:phase16_verify_tests`, and `bazel run //tools/bazel:phase16_verify` should pass before `/gsd-verify-work`. [VERIFIED: justfile; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: AGENTS.md]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase16_live_network_evidence_contract.json` — row coverage for LIVE-01, LIVE-02, and LIVE-03. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- [ ] `tools/bazel/phase16_live_network_evidence.py` — contract/security/wiring/quick/operator-evidence implementation. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- [ ] `tools/bazel/phase16_live_network_evidence_test.py` — coverage for required rows, redaction, overclaim rejection, source refs, path safety, and workflow wiring. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

## Security Domain

OWASP ASVS is currently versioned; the official ASVS repository identifies version `5.0.0` dated May 2025 as the latest stable version and warns that the master branch can be bleeding edge. [CITED: https://github.com/OWASP/ASVS] Formal control IDs should therefore be written with the ASVS version if the planner adds them. [CITED: https://github.com/OWASP/ASVS]

### Applicable Security Categories

| Security Domain | Applies | Standard Control |
|-----------------|---------|------------------|
| Authentication | Yes | Redact Connect tokens/fingerprints and PrusaLink passwords/API keys; verify positive and negative auth outcomes only through secret-safe metadata. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: src/connect/connect.cpp; VERIFIED: lib/WUI/nhttp/req_parser.cpp] |
| Session/state and nonce handling | Yes | Include WUI digest nonce/stale scenarios and WebSocket command-channel state evidence. [VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: lib/WUI/nhttp/req_parser.cpp; VERIFIED: src/connect/connect.cpp] |
| Access control / API authorization | Yes | Include WUI API-key and digest-auth rows plus negative unauthorized HTTP/API cases. [VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: lib/WUI/nhttp/status_page.cpp] |
| Input validation / protocol robustness | Yes | Include negative protocol cases for WUI HTTP/API, WebSocket upgrade, transfer upload, range/resume, and malformed inputs. [VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json; VERIFIED: src/connect/connect.cpp; VERIFIED: lib/WUI/nhttp/gcode_upload.cpp] |
| Cryptography and secure communications | Yes | Include TLS version/verification/cipher behavior, custom DER cert fixture outcomes, and proxy limitation evidence. [VERIFIED: src/connect/tls/tls.cpp; VERIFIED: doc/proxy_support.md] |
| Data protection and logging | Yes | Reject raw credentials, private certs, raw HTTP/TLS logs, raw crash dumps, and unredacted production payloads. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: src/gui/screen_home.cpp] |

### Known Threat Patterns for Phase 16 Evidence

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Token, fingerprint, password, API-key, or cert disclosure in evidence files | Information Disclosure | Raw-input scanning, generated-summary scanning, denylisted markers, and external refs only. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| False live qualification from dry-run-only output | Spoofing / Repudiation | Required status vocabulary, pending defaults, and overclaim phrase rejection. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |
| Path traversal through operator artifact paths | Tampering / Information Disclosure | Repo-relative source refs and output path containment checks. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| Proxy behavior misrepresented as authenticated or fully encrypted | Information Disclosure / Spoofing | Explicit proxy-limitation scenario rows citing docs/source behavior. [VERIFIED: doc/proxy_support.md; VERIFIED: src/common/http/proxy.cpp; VERIFIED: src/connect/connection_cache.cpp] |
| Crash-dump upload exposes memory contents | Information Disclosure | No raw dumps in git or generated summaries; accept hashes, redacted summaries, and external refs only. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: src/gui/screen_home.cpp] |
| Live artifact provenance cannot be reviewed | Repudiation | Operator evidence requires timestamp/build/service-mode/operator metadata and external artifact references. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md` — locked Phase 16 decisions, scope, statuses, artifact policy, redaction rules, tooling shape, and lifecycle. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- `.planning/REQUIREMENTS.md` — LIVE-01, LIVE-02, and LIVE-03 requirement text. [VERIFIED: .planning/REQUIREMENTS.md]
- `.planning/ROADMAP.md` — Phase 16 goal, dependencies, and success criteria. [VERIFIED: .planning/ROADMAP.md]
- `.planning/STATE.md` — project decision/history context. [VERIFIED: .planning/STATE.md]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/index.md`, and relevant `standards/core/*.md` pages — repo and Bright Builds constraints. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards-overrides.md; VERIFIED: standards/index.md; VERIFIED: standards/core/architecture.md; VERIFIED: standards/core/code-shape.md; VERIFIED: standards/core/verification.md; VERIFIED: standards/core/testing.md]
- `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase14_simulator_evidence.py`, `tools/bazel/phase15_hardware_evidence.py`, and their contracts/tests — implementation patterns for evidence runners. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence_test.py]
- `tools/bazel/manifests/phase9_*` and `tools/bazel/manifests/phase11_*` — source-backed network/transfer inventory and parity/cutover/reference gates. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json; VERIFIED: tools/bazel/manifests/phase9_network_service_contracts.json; VERIFIED: tools/bazel/manifests/phase9_transfer_contracts.json; VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json; VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json]
- `doc/proxy_support.md`, `doc/metrics.md`, and related Connect/WUI/TLS/transfer/crash-dump source files — behavior surfaces and limitations. [VERIFIED: doc/proxy_support.md; VERIFIED: doc/metrics.md; VERIFIED: src/connect/connect.cpp; VERIFIED: src/connect/tls/tls.cpp; VERIFIED: src/common/http/proxy.cpp; VERIFIED: src/connect/connection_cache.cpp; VERIFIED: src/transfers/download.cpp; VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp; VERIFIED: lib/WUI/nhttp/req_parser.cpp; VERIFIED: lib/WUI/nhttp/gcode_upload.cpp; VERIFIED: src/common/crash_dump/crash_dump_distribute.cpp; VERIFIED: src/gui/screen_home.cpp]

### Secondary (MEDIUM confidence)

- Official OWASP ASVS repository and project page — current stable ASVS versioning guidance for security-domain references. [CITED: https://github.com/OWASP/ASVS; CITED: https://owasp.org/www-project-application-security-verification-standard/]

### Tertiary (LOW confidence)

- None. [VERIFIED: this research file source log]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — repository evidence runner pattern, local tool versions, and locked Phase 16 decisions were verified directly. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: python3 --version; VERIFIED: bazel --version; VERIFIED: just --version; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
- Architecture: HIGH — Phase 13/14/15 provide direct templates for manifests, runners, tests, generated artifacts, and Bazel/just wiring. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase15_hardware_evidence.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile]
- Pitfalls: HIGH — secret, overclaim, path, proxy, TLS/custom cert, transfer, and crash-dump risks are documented in locked decisions, prior verification, docs, and source. [VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md; VERIFIED: .planning/phases/09-network-and-transfer-inventory/09-VERIFICATION.md; VERIFIED: doc/proxy_support.md; VERIFIED: src/connect/tls/tls.cpp; VERIFIED: src/gui/screen_home.cpp]
- Live environment availability: MEDIUM — local tool availability is verified, but live services/credentials/endpoints are intentionally absent from repo context and must remain operator-supplied. [VERIFIED: python3 --version; VERIFIED: bazel --version; VERIFIED: just --version; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]

**Research date:** 2026-06-18  
**Valid until:** 2026-07-18 for repository-local patterns; 2026-06-25 for live service and ASVS currency-sensitive details. [CITED: https://github.com/OWASP/ASVS; VERIFIED: .planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md]
