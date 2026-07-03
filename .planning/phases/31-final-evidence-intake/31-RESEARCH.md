# Phase 31: Final Evidence Intake - Research

**Researched:** 2026-07-03  
**Domain:** Final evidence intake wrapper over existing Python/Bazel cutover-evidence verifiers. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]  
**Confidence:** HIGH. The phase is constrained by locked decisions and already-shipped Phase 23-26 machinery. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: .planning/milestones/v1.2-phases/23-simulator-evidence-execution/23-01-SUMMARY.md; VERIFIED: .planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md]

<user_constraints>
## User Constraints (from CONTEXT.md)

Source for this copied constraint section: [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

### Locked Decisions

### Shared Final-Intake Gate
- **D-01:** Build Phase 31 as a shared fail-closed final-intake gate over the existing Phase 23, Phase 24, Phase 25, and Phase 26 contracts. Do not create a new evidence schema, status vocabulary, or proof class unless a real final packet exposes a narrow decision-blocking defect that the existing contract cannot represent.
- **D-02:** Phase 31 may add thin intake receipts or a final intake manifest with v1.3 provenance fields such as submission id, packet hash, operator/release-manager identity reference, timestamp, validator command, validator output refs, and consumed upstream row refs. Receipts must not duplicate stream scenario fields or become a second evidence schema.
- **D-03:** Preserve stream-specific validators as authoritative. The shared gate should call or revalidate through the existing Phase 23-26 scripts instead of reimplementing simulator, hardware, live-service, or release-specific rules.
- **D-04:** Accepted final evidence must retain enough canonical row data for Phase 32 to classify missing, stale, failed, redaction-failed, malformed, blocked, and exception-requested rows without rereading raw secret-bearing payloads.

### Simulator Evidence Intake
- **D-05:** Simulator intake should reuse the unchanged Phase 23 real-input path and require real-run metadata, exact Phase 14 scenario coverage, Phase 23 retained outputs, and the Phase 26-compatible upstream simulator result row.
- **D-06:** If separate Phase 31 simulator provenance is needed, add only a thin receipt over the validated Phase 23 packet. Do not add final-only simulator scenario fields or statuses.

### Hardware, Media, and Safety Evidence Intake
- **D-07:** Hardware/media/safety intake should preserve Phase 24 as the authority for required Phase 15 scenarios, status normalization, storage and safety metadata, artifact refs, secret guards, overclaim guards, retained outputs, and upstream rows.
- **D-08:** Phase 31 can either invoke Phase 24 for raw final packets or register Phase 24 retained outputs, but it must enforce real hardware evidence provenance and reject stale, quick, or placeholder outputs as final proof.

### Live-Service Evidence Intake
- **D-09:** Live-service intake should be a thin wrapper around the Phase 25 evidence-input path, preserving exact Phase 16 scenario coverage for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative protocol, long transfer, and crash-dump flows.
- **D-10:** No local smoke output, quick/default output, manually written prose attestation, or summary-only upstream row should pass as final live-service proof unless the underlying Phase 25 retained packet and manifest are revalidated.

### Release, Signing, and Provenance Evidence Intake
- **D-11:** Release/signing/provenance intake should reuse Phase 26 release/signing/upstream evidence validation and retain sanitized manifests, external refs, digests, redaction/provenance summaries, artifact-reference summaries, and normalized upstream rows.
- **D-12:** Raw private keys, tokens, certificates, service payloads, raw crash dumps, raw release logs, and other secret-bearing material must stay outside retained artifacts. Signing identity and provenance should be represented as references and digests, not copied secret material.

### Sanitization and Non-Final Outputs
- **D-13:** Accepted refs should stay within each stream's allowed local output root or `external://phaseXX/` reference namespace. Phase 31 should preserve `redaction_status`, `source_ref_status`, `exception_status`, `failure_reason`, lifecycle/provenance signals, and artifact-reference summaries.
- **D-14:** Quick/default placeholders, local-only dry-run rows, template rows, and local smoke fixtures are useful for workflow checks but must be marked non-final and rejected as cutover proof.
- **D-15:** A quarantine or rejected-submissions report is acceptable only if names make clear that quarantined rows are not accepted final evidence. Quarantined data must not feed final readiness as proof.

### the agent's Discretion

- The agent may choose the concrete file shape for Phase 31 receipts and aggregate manifests, provided the schema remains a wrapper over Phase 23-26 outputs.
- The agent may choose whether to implement one shared script with stream-specific adapters or a small shared policy module plus a Phase 31 verifier script.
- The agent may choose exact Bazel labels and `just` target names, but they should follow existing phase naming patterns such as `phase23_verify`, `phase24_verify`, `phase25_verify`, and `phase26_verify`.

### Deferred Ideas (OUT OF SCOPE)

- Blocker register grouping, ownership, severity, next action, and decision impact belong to Phase 32.
- Retained-code, exception, residual-risk, final-readiness, and demotion decisions belong to Phase 33.
- Final readiness packet generation and reference-demotion dry-run behavior belong to Phase 34.
- Cutover verdict publication belongs to Phase 35.
- Broad retained vendor/HAL replacement, new printer behavior, and long-run dashboards remain future milestone work unless Phase 31 reveals a narrow decision-blocking defect.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INTAKE-01 | Maintainer can supply final simulator evidence packets for startup, G-code, GUI, storage, transfer, and selected failure flows using sanitized real-run inputs. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 23 `--evidence-input`, require 9 Phase 14 scenarios, require `real_simulator_evidence_supplied: true`, and retain a Phase 31 receipt over `upstream-simulator-result-row.json`. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| INTAKE-02 | Maintainer can supply final hardware/media/safety evidence packets for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 24 `--evidence-input`, require 26 Phase 15 scenarios, require `real_hardware_evidence_supplied: true`, and accept retained-output registration only when manifest and upstream row prove real evidence. [VERIFIED: tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py] |
| INTAKE-03 | Maintainer can supply final live-service evidence packets for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 25 `--evidence-input`, require 20 Phase 16 scenarios, require `real_live_service_evidence_supplied: true`, and reject prose or upstream-row-only submissions unless the retained Phase 25 packet is revalidated. [VERIFIED: tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |
| INTAKE-04 | Release manager can supply final release/signing/provenance evidence from real release-environment outputs without exposing private keys, tokens, certificates, service payloads, raw crash dumps, or other secret-bearing data. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 26 `--release-input` plus Phase 23/24/25 compact upstream row inputs, require real release evidence where release proof is being finalized, and preserve redaction/provenance and artifact-reference summaries. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; VERIFIED: tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json] |
</phase_requirements>

## Summary

Phase 31 should be implemented as one shared final-intake verifier with stream-specific adapters over Phase 23, Phase 24, Phase 25, and Phase 26, because the locked decision set explicitly forbids a new evidence schema, status vocabulary, or proof class unless real evidence exposes a narrow decision-blocking defect. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

The implementation should write Phase 31-owned provenance only: an aggregate final intake manifest plus per-stream receipts under `build/ci-evidence/phase31`, while the authoritative scenario validation and retained stream outputs remain owned by Phase 23-26 scripts. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

Final acceptance must be fail-closed: quick/default placeholders, local smoke fixtures, template rows, prose attestations, stale lifecycle IDs, source-ref failures, redaction failures, unsafe refs, and secret-bearing material must be rejected as final proof before Phase 31 emits accepted receipts. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

**Primary recommendation:** Build `tools/bazel/phase31_final_evidence_intake.py`, `tools/bazel/phase31_final_evidence_intake_test.py`, and `tools/bazel/manifests/phase31_final_evidence_intake_contract.json` as a standard-library Python wrapper that invokes or registers Phase 23-26 outputs, emits thin receipts, and wires `phase31_verify` / `phase31_verify_tests` through Bazel and `just phase31-verify`. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

## Project Constraints (from AGENTS.md)

- Read `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before plan, review, implementation, or audit work. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md]
- Keep Bright Builds managed files unedited unless the task is upstream rule maintenance; repo-specific deviations belong in `standards-overrides.md`. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md]
- Use `rg` for searches and prefer semantic/LSP tools when available; no project-local skills were present under `.claude/skills` or `.agents/skills`. [VERIFIED: AGENTS.md; VERIFIED: `find .claude/skills .agents/skills -maxdepth 2 -name SKILL.md`]
- Before committing code in this Rust-containing repository, the required sequence is `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`. [VERIFIED: AGENTS.md]
- For this phase, use the existing Bazel-primary and `justfile` workflow rather than adding an alternate runner. [VERIFIED: .planning/PROJECT.md; VERIFIED: AGENTS.md]
- Prefer functional core / imperative shell: keep intake policy as pure transformations over loaded rows and keep subprocess/file writes in a thin CLI shell. [VERIFIED: standards/core/architecture.md; VERIFIED: AGENTS.bright-builds.md]
- Parse boundary JSON into stricter internal records early; do not pass raw dictionaries deep into the decision logic when row shape can be checked once. [VERIFIED: standards/core/architecture.md]
- Prefer early returns, keep control flow shallow, and use `maybe_` for internal optional or absence-like names where practical. [VERIFIED: standards/core/code-shape.md; VERIFIED: AGENTS.bright-builds.md]
- Unit-test pure/business logic, keep tests to one concern, and delineate Arrange, Act, and Assert comments in non-trivial tests. [VERIFIED: standards/core/testing.md; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]
- Run relevant repo-native verification before done; for Phase 31 this means direct Python tests and `just phase31-verify` after wiring, plus the Rust sequence only if Rust files are touched. [VERIFIED: standards/core/verification.md; VERIFIED: justfile; VERIFIED: AGENTS.md]
- Do not use standalone `---` body separators in GSD Markdown artifacts because repo tooling parses YAML frontmatter delimiters specially. [VERIFIED: AGENTS.md]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python standard library | Python 3.14.4 available locally | Implement verifier CLI, JSON parsing/writing, subprocess calls, hashing, path validation, and `unittest` tests. | All Phase 23-28 evidence verifiers are Python standard-library scripts, and local `python3 --version` reports 3.14.4. [VERIFIED: `python3 --version`; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| JSON contracts under `tools/bazel/manifests/` | Repo-current tracked files | Describe Phase 31 wrapper policy and cite existing Phase 23-26 contracts. | Phase 23-28 use tracked JSON contracts as the stable policy source for verifier behavior. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json] |
| Bazel `shell_binary` targets | Bazel 9.1.1 available locally | Expose `phase31_verify` and `phase31_verify_tests`. | Existing phase verifiers are wired through `tools/bazel/BUILD.bazel` `shell_binary` targets and root aliases. [VERIFIED: `bazel --version`; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel] |
| `just` facade | just 1.48.0 available locally | Provide `just phase31-verify`. | Phase 23-28 all expose `just phaseXX-verify` recipes that run tests before the verifier. [VERIFIED: `just --version`; VERIFIED: justfile] |
| Existing Phase 23-26 verifier scripts | Repo-current tracked scripts | Keep stream-specific validation authoritative. | Phase 31 context requires existing stream validators to remain authoritative and not be reimplemented. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `jq` | jq-1.7.1-apple available locally | Inspect contract fields during development and debugging. | Use only as a developer aid; the implementation should parse JSON with Python to avoid adding runtime dependencies. [VERIFIED: `jq --version`; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| `rg` | Available in session by usage | Locate existing target names, secret markers, and contract fields. | Use during planning and implementation to preserve current naming and guard behavior. [VERIFIED: AGENTS.md; VERIFIED: current research `rg` commands] |
| Git | git 2.53.0 available locally | Inspect worktree state and final diff. | Use for verification and review; current worktree already has an unrelated `.planning/config.json` modification that Phase 31 research must not revert. [VERIFIED: `git --version`; VERIFIED: `git status --short`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Shared Phase 31 wrapper over Phase 23-26 | New Phase 31 stream schemas | Rejected by locked decision D-01 because it duplicates authoritative schema and status surfaces. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |
| Subprocess invocation of Phase 23-26 CLIs | Reimplement scenario coverage and release proof checks in Phase 31 | Rejected by D-03; reimplementation risks drift from existing validators and tests. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py] |
| Thin receipts plus aggregate manifest | Copy full stream scenario rows into a second schema | Rejected by D-02 because receipts must not duplicate stream scenario fields. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |
| Machine-readable intake manifest | Prose-only attestation or manually written summary | Rejected by D-10 and D-14 because local smoke, summary-only, prose, and quick outputs must not pass final proof. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |

**Installation:** No new packages are required. [VERIFIED: existing Phase 23-28 scripts use Python standard library imports; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

**Version verification:** Local tool versions were verified with:

```bash
python3 --version
bazel --version
just --version
jq --version
git --version
```

No `npm view` verification applies because Phase 31 should not add npm packages. [VERIFIED: .planning/PROJECT.md; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── manifests/
│   └── phase31_final_evidence_intake_contract.json  # Wrapper policy over Phase 23-26 contracts. [VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json]
├── phase31_final_evidence_intake.py                 # Pure intake policy plus thin CLI/subprocess shell. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py]
└── phase31_final_evidence_intake_test.py            # unittest regression coverage with Arrange/Act/Assert comments. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]

build/ci-evidence/phase31/
├── final-intake-manifest.json                       # Aggregate accepted/rejected stream receipt index. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]
├── stream-receipts/
│   ├── simulator-intake-receipt.json
│   ├── hardware-media-safety-intake-receipt.json
│   ├── live-service-intake-receipt.json
│   └── release-signing-intake-receipt.json
├── rejected-submissions.json                        # Optional quarantine report; not accepted proof. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]
└── contract-snapshots/
    ├── phase23_simulator_evidence_execution_contract.json
    ├── phase24_hardware_media_safety_evidence_execution_contract.json
    ├── phase25_live_service_evidence_execution_contract.json
    └── phase26_release_signing_upstream_evidence_contract.json
```

### Pattern 1: Shared Gate With Stream Adapters

**What:** Implement one `phase31_final_evidence_intake.py` CLI with adapter constants for simulator, hardware/media/safety, live-service, and release/signing streams. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**When to use:** Use for all INTAKE-01 through INTAKE-04 submissions so finality policy is centralized while stream validation remains delegated. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Implementation guidance:** Each stream adapter should name the owning validator command, default retained output root, required real-evidence flag, manifest filename, upstream row filename, accepted local root, accepted external root, and requirement ID. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

### Pattern 2: Invoke Existing Validators for Raw Packets

**What:** Raw final packets should be passed to Phase 23/24/25 with `--evidence-input` and to Phase 26 with `--release-input` and compact upstream row flags. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

**When to use:** Use this path when a maintainer or release manager provides a new sanitized local JSON input file for Phase 31 intake. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Example command chain:** Run the stream command, then parse the retained manifest and upstream row to build the receipt. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

```bash
python3 tools/bazel/phase23_simulator_evidence_execution.py \
  --evidence-input build/ci-evidence/phase31/incoming/simulator-evidence.json \
  --output-dir build/ci-evidence/phase23
```

### Pattern 3: Register Retained Outputs Only After Real-Proof Checks

**What:** A retained-output registration path should read existing Phase 23/24/25/26 manifests and rows, then require the stream-specific `real_*_evidence_supplied` flag to be true before accepting the receipt. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

**When to use:** Use when real evidence was already validated by Phase 23-26 and Phase 31 only needs final v1.3 provenance and consumed-row references. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Required checks:** Reject retained outputs if command mode is quick/default/template, real evidence flag is false, lifecycle ID is missing or stale, status fields are malformed, redaction/source-ref status fails, artifact refs escape allowed roots, or required retained files are absent. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

### Pattern 4: Receipt Schema Is Provenance, Not Evidence

**What:** Receipt rows should record `submission_id`, `stream`, `requirement_ids`, `finality_status`, `validated_by`, `validator_command`, `validator_output_refs`, `consumed_upstream_row_ref`, `receipt_generated_at_utc`, `submitter_identity_ref`, `packet_sha256`, `redaction_status`, `source_ref_status`, `exception_status`, and `failure_reason`. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json]

**When to use:** Use for Phase 31-owned auditability and Phase 32 blocker-register input without copying scenario fields into a new stream schema. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Receipt status guidance:** Use `accepted-final`, `rejected-final`, and `quarantined-non-final` only as Phase 31 finality classifications, not as replacement evidence stream statuses. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

### Anti-Patterns to Avoid

- **New scenario fields in Phase 31:** This duplicates Phase 23-25 stream schemas and violates D-01/D-02. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]
- **Upstream row only as final proof:** Phase 31 must not accept summary-only proof unless the underlying retained packet and manifest are revalidated. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]
- **Quick output promotion:** Quick placeholders deliberately have `real_*_evidence_supplied: false` or pending statuses, so accepting them would violate the phase goal. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]
- **Phase 31 readiness or demotion verdicts:** Phase 31 stops at intake provenance; readiness, demotion, and cutover decisions belong to later phases. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: .planning/ROADMAP.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Simulator scenario validation | A new Phase 31 simulator scenario checker | `phase23_simulator_evidence_execution.py --evidence-input` | Phase 23 already enforces exact Phase 14 scenario coverage, status normalization, secret guards, retained outputs, and upstream simulator row production. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py] |
| Hardware/media/safety validation | A final-only hardware schema | `phase24_hardware_media_safety_evidence_execution.py --evidence-input` | Phase 24 already validates 26 Phase 15 scenarios, storage/safety metadata, artifact refs, redaction/source-ref status, retained outputs, and upstream rows. [VERIFIED: tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py] |
| Live-service validation | Prose attestations or a compact row-only validator | `phase25_live_service_evidence_execution.py --evidence-input` | Phase 25 already validates 20 Phase 16 scenarios and rejects credential, payload, raw crash dump, and artifact-ref failures. [VERIFIED: tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py] |
| Release/signing/provenance validation | A custom signing/provenance proof parser | `phase26_release_signing_upstream_evidence.py --release-input` | Phase 26 already handles release proof classes, upstream row normalization, redaction/provenance summaries, artifact-reference summaries, and compact Phase 23-25 row consumption. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; VERIFIED: tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json] |
| Secret scanning | A new unrelated denylist | Reuse existing forbidden field/text patterns and add only Phase 31-specific wrapping around them | Existing streams already reject private keys, certs, tokens, credentials, raw dumps, raw logs, payload bytes, and overclaim phrases before retained writes. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Upstream row normalization | A new canonical row shape | Use Phase 26 upstream policy and row-required fields | Phase 26 defines the canonical Phase 18 criteria, row fields, compact row input policy, and live-service to live-network criterion mapping. [VERIFIED: tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json] |

**Key insight:** Phase 31 adds finality and provenance, not proof semantics; the hard parts are already encoded in Phase 23-26 validators and must remain authoritative. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Creating A Second Evidence Schema

**What goes wrong:** Phase 31 copies scenario fields from Phase 23-25 into a new final schema and later diverges from the source validators. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Why it happens:** Receipts need enough data for Phase 32 triage, but D-02 says receipts must not duplicate stream scenario fields. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**How to avoid:** Store links, hashes, upstream row refs, status summary, finality classification, and validator output refs; keep scenario data in retained Phase 23-25 outputs. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py]

**Warning signs:** `phase31_final_evidence_intake_contract.json` starts listing simulator/hardware/live scenario-specific fields beyond receipt provenance. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

### Pitfall 2: Accepting Quick Or Template Outputs As Final

**What goes wrong:** A local quick run produces retained files and a Phase 31 receipt marks them final. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Why it happens:** Phase 23-26 quick modes intentionally write structurally valid retained outputs for workflow checks. [VERIFIED: .planning/milestones/v1.2-phases/23-simulator-evidence-execution/23-01-SUMMARY.md; VERIFIED: .planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md]

**How to avoid:** Require stream-specific real evidence flags to be true and reject command modes such as `quick-placeholder`, absent release input, pending rows, and template-derived outputs. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]

**Warning signs:** A receipt uses `build/ci-evidence/phase23` or `phase26` outputs but has no local evidence input path, no submitter identity ref, no packet hash, or a manifest flag such as `real_simulator_evidence_supplied: false`. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

### Pitfall 3: Losing Phase 26 Compatibility

**What goes wrong:** Phase 31 emits rows that Phase 26, Phase 28, or later readiness logic cannot consume. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

**Why it happens:** Phase 25 compact row criterion `final-live-service-evidence` maps to Phase 18 canonical criterion `final-live-network-transfer-evidence` through Phase 26. [VERIFIED: tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]

**How to avoid:** Let Phase 26 normalize compact upstream rows and have Phase 31 receipts reference consumed row paths rather than translating criteria itself. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

**Warning signs:** Phase 31 directly writes `upstream-result-row-table.json` with Phase 18 criteria. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

### Pitfall 4: Treating Redaction Or Source-Ref Failures As Normal Exceptions

**What goes wrong:** Secret-tainted or source-ref-failed evidence is accepted because a maintainer exception is present. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

**Why it happens:** Later decision phases allow some exception states, but Phase 28 treats redaction failure, overclaim failure, lifecycle mismatch, source-ref failure, unsafe refs, and secret-tainted evidence as hard blockers. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py; VERIFIED: .planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md]

**How to avoid:** Phase 31 should reject redaction/source-ref/unsafe-ref failures at intake and preserve failure reason fields for Phase 32 triage. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Warning signs:** Phase 31 has `accepted-final` receipts where `redaction_status != passed` or `source_ref_status != passed`. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

### Pitfall 5: Retaining Secret-Bearing Artifacts

**What goes wrong:** Raw private keys, tokens, certificates, service payloads, raw crash dumps, or raw release logs are copied into retained outputs. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Why it happens:** Final evidence packets describe live services and release environments, where raw data often includes credentials or sensitive payloads. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

**How to avoid:** Keep only sanitized refs, digests, redaction summaries, provenance summaries, and artifact-reference summaries. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

**Warning signs:** Receipt or manifest field names include `token`, `private_key`, `certificate_pem`, `raw_crash_dump`, `raw_logs`, `payload_bytes`, or similar markers already forbidden by Phase 23-26 scripts. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

## Code Examples

### Stream Adapter Table

```python
STREAMS = {
    "simulator": {
        "requirement_ids": ["INTAKE-01"],
        "validator": "tools/bazel/phase23_simulator_evidence_execution.py",
        "raw_input_flag": "--evidence-input",
        "output_dir": "build/ci-evidence/phase23",
        "manifest": "simulator-result-manifest.json",
        "upstream_row": "upstream-simulator-result-row.json",
        "real_flag": "real_simulator_evidence_supplied",
        "accepted_roots": ["build/ci-evidence/phase23/", "external://phase23/"],
    },
    # Repeat for Phase 24, Phase 25, and Phase 26.
}
```

This adapter shape is a Phase 31 recommendation derived from existing stream commands and retained output filenames, not an existing checked-in API. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py]

### Validator Invocation Shell

```python
def run_validator(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, *command],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return completed.returncode, completed.stdout
```

Use an argument list instead of shell strings because existing phase scripts are Python CLIs and Bright Builds discourages hidden foreign-language logic inside strings. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: standards/core/code-shape.md]

### Receipt Row Shape

```json
{
  "submission_id": "final-intake-2026-07-03T00:00:00Z-simulator",
  "stream": "simulator",
  "requirement_ids": ["INTAKE-01"],
  "finality_status": "accepted-final",
  "validator_command": "python3 tools/bazel/phase23_simulator_evidence_execution.py --evidence-input ...",
  "validator_output_refs": [
    "build/ci-evidence/phase23/simulator-result-manifest.json",
    "build/ci-evidence/phase23/normalized-simulator-results.json"
  ],
  "consumed_upstream_row_ref": "build/ci-evidence/phase23/upstream-simulator-result-row.json",
  "redaction_status": "passed",
  "source_ref_status": "passed",
  "exception_status": "none",
  "failure_reason": "none"
}
```

This receipt shape preserves D-02 provenance fields and Phase 26-compatible status details without copying stream scenarios. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json]

## State of the Art

| Old Approach | Current Approach | When Changed / Verified | Impact |
|--------------|------------------|--------------------------|--------|
| v4-style ASVS category numbering where V2 is Authentication, V3 is Session Management, V4 is Access Control, V5 is Validation, and V6 is Cryptography | ASVS 5.0.0 is the latest stable version; ASVS 5.0.x lists V1 Encoding/Sanitization, V2 Validation/Business Logic, V4 API/Web Service, V5 File Handling, V6 Authentication, V7 Session Management, V8 Authorization, V11 Cryptography, V12 Secure Communication, V13 Configuration, V14 Data Protection, V15 Secure Coding/Architecture, and V16 Logging/Error Handling. | Verified 2026-07-03 from OWASP ASVS project and OWASP Cheat Sheet ASVS index. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html] | Security mapping for Phase 31 should use ASVS 5.0 category names and avoid stale v4 numbering in new docs. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html] |
| Local quick evidence as smoke proof | Quick/default output is a blocked placeholder and not final evidence. | Established in Phase 23-26 summaries and tests. [VERIFIED: .planning/milestones/v1.2-phases/23-simulator-evidence-execution/23-01-SUMMARY.md; VERIFIED: .planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md] | Phase 31 must reject quick/default/template rows as final cutover proof. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |
| Direct final readiness consumption of hardcoded pending defaults | Phase 29 added Phase 23/24/25 compact upstream row ingestion into Phase 26 and Phase 28 preserves producer evidence refs. | Shipped in Phase 29. [VERIFIED: .planning/milestones/v1.2-phases/29-upstream-evidence-flow-closure/29-01-SUMMARY.md] | Phase 31 should feed validated stream rows through Phase 26 rather than inventing a new readiness input. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |

**Deprecated/outdated:** Do not use ASVS v4 numbering in Phase 31's security table; use ASVS 5.0 category names verified above. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | No unverified assumptions are required for planning; implementation recommendations are derived from checked-in contracts, scripts, standards, or cited OWASP pages. [VERIFIED: current research commands] | All | — |

## Open Questions

1. **What exact identity-reference format should Phase 31 require?**
   - What we know: Existing evidence packets use `operator`, release evidence uses release identity fields such as `key_identity_ref`, and Phase 31 context allows operator/release-manager identity references. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json; VERIFIED: tools/bazel/manifests/phase17_release_candidate_evidence_contract.json; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]
   - What's unclear: No single existing `operator_identity_ref` field name was found as a global convention. [VERIFIED: `rg -n "operator_identity|identity_ref|submitted_by|release_manager|operator|approver|maintainer" tools/bazel .planning/milestones/v1.2-phases/...`]
   - Recommendation: Use an opaque, non-secret `submitter_identity_ref` string in the Phase 31 receipt and do not authenticate identities in Phase 31. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 31 verifier and tests | yes | 3.14.4 | Blocking if unavailable because Phase 23-28 verifiers use Python. [VERIFIED: `python3 --version`; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Bazel | `phase31_verify` / `phase31_verify_tests` targets | yes | 9.1.1 | Direct Python commands can run during development, but final workflow should wire Bazel. [VERIFIED: `bazel --version`; VERIFIED: tools/bazel/BUILD.bazel] |
| `just` | Developer facade `just phase31-verify` | yes | 1.48.0 | Bazel labels can run directly, but project constraint requires `justfile` workflow. [VERIFIED: `just --version`; VERIFIED: .planning/PROJECT.md; VERIFIED: justfile] |
| `jq` | Developer inspection only | yes | jq-1.7.1-apple | Python JSON parsing. [VERIFIED: `jq --version`; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Git | Diff review and final verification context | yes | 2.53.0 | None for repository workflow. [VERIFIED: `git --version`] |

**Missing dependencies with no fallback:** None found for research/planning. [VERIFIED: environment audit commands]

**Missing dependencies with fallback:** None found for implementation-critical paths. [VERIFIED: environment audit commands]

## Validation Architecture

Nyquist validation applies because `.planning/config.json` explicitly sets `workflow.nyquist_validation` to `true`. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` using standard-library test scripts, matching Phase 23-28 verifier tests. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py; VERIFIED: tools/bazel/phase28_final_readiness_packet_test.py] |
| Config file | None for phase verifier tests; tests run as direct Python scripts and through Bazel shell targets. [VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py; VERIFIED: tools/bazel/BUILD.bazel] |
| Quick run command | `python3 tools/bazel/phase31_final_evidence_intake_test.py -q` after Wave 0 creates the test file. [VERIFIED: Phase 23-28 direct test pattern] |
| Full suite command | `just phase31-verify` after Bazel/root/just wiring. [VERIFIED: justfile; VERIFIED: tools/bazel/rust_workflow.sh] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| INTAKE-01 | Final simulator raw packet invokes Phase 23, rejects missing scenario coverage, rejects quick placeholder, emits accepted receipt over real Phase 23 upstream row. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py] | unit/integration wrapper | `python3 tools/bazel/phase31_final_evidence_intake_test.py -q` | No, Wave 0 required. [VERIFIED: `git ls-files tools/bazel/phase31_final_evidence_intake_test.py`] |
| INTAKE-02 | Final hardware/media/safety raw or retained packet preserves Phase 24 authority, requires real hardware provenance, and rejects quick/stale/placeholder outputs. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py] | unit/integration wrapper | `python3 tools/bazel/phase31_final_evidence_intake_test.py -q` | No, Wave 0 required. [VERIFIED: `git ls-files tools/bazel/phase31_final_evidence_intake_test.py`] |
| INTAKE-03 | Final live-service packet invokes Phase 25, rejects prose/upstream-row-only submissions, rejects secret-bearing fields, and emits receipt over real retained packet. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/phase25_live_service_evidence_execution_test.py] | unit/integration wrapper | `python3 tools/bazel/phase31_final_evidence_intake_test.py -q` | No, Wave 0 required. [VERIFIED: `git ls-files tools/bazel/phase31_final_evidence_intake_test.py`] |
| INTAKE-04 | Final release/signing/provenance input invokes Phase 26, consumes Phase 23/24/25 rows, rejects raw secrets, and preserves redaction/provenance plus artifact-reference summaries. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py] | unit/integration wrapper | `python3 tools/bazel/phase31_final_evidence_intake_test.py -q` | No, Wave 0 required. [VERIFIED: `git ls-files tools/bazel/phase31_final_evidence_intake_test.py`] |

### Sampling Rate

- **Per task commit:** Run the focused Python test file plus the specific mode being touched, such as `python3 tools/bazel/phase31_final_evidence_intake_test.py -q`. [VERIFIED: standards/core/testing.md; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py]
- **Per wave merge:** Run `just phase31-verify` after wiring exists. [VERIFIED: standards/core/verification.md; VERIFIED: justfile]
- **Phase gate:** Run `just phase31-verify`, `git diff --check`, and the Rust pre-commit sequence only if Rust files are touched. [VERIFIED: AGENTS.md; VERIFIED: standards/core/verification.md]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase31_final_evidence_intake_contract.json` - wrapper contract over Phase 23-26. [VERIFIED: no existing Phase 31 implementation from `git ls-files`]
- [ ] `tools/bazel/phase31_final_evidence_intake.py` - final intake verifier and retained receipt writer. [VERIFIED: no existing Phase 31 implementation from `git ls-files`]
- [ ] `tools/bazel/phase31_final_evidence_intake_test.py` - regression tests for accepted raw packets, retained-output registration, placeholder rejection, secret rejection, stale lifecycle rejection, artifact-root rejection, and wiring. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: no existing Phase 31 implementation from `git ls-files`]
- [ ] `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring for `phase31_verify` and `phase31_verify_tests`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]
- [ ] `.planning/phases/31-final-evidence-intake/31-VALIDATION.md` - Nyquist metadata after implementation evidence exists. [VERIFIED: .planning/config.json; VERIFIED: .planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-VALIDATION.md]

## Security Domain

OWASP ASVS 5.0.0 is the latest stable ASVS version, and OWASP states ASVS provides a basis for testing web application technical security controls and secure-development requirements. [CITED: https://owasp.org/www-project-application-security-verification-standard/] The ASVS cheat-sheet index says it is based on ASVS 5.0.x and lists current category names. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Applicable ASVS Categories

| ASVS 5.0 Category | Applies | Standard Control |
|-------------------|---------|------------------|
| V1 Encoding and Sanitization | yes | Reject forbidden field names/text and retain sanitized refs/summaries only. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py] |
| V2 Validation and Business Logic | yes | Parse final intake inputs into checked receipt/stream records and enforce fail-closed finality rules. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: standards/core/architecture.md; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |
| V4 API and Web Service | no direct network API | Phase 31 is a local CLI wrapper, not a network service. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| V5 File Handling | yes | Restrict input/output paths to repo-relative paths and allowed evidence roots; reject traversal and symlink escapes where writing. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| V6 Authentication | no direct authentication | Record `submitter_identity_ref` as evidence provenance only; do not implement user authentication in Phase 31. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |
| V7 Session Management | no | Phase 31 has no sessions. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: local CLI-only verifier pattern in tools/bazel/phase23_simulator_evidence_execution.py] |
| V8 Authorization | limited | Reject final proof where required release-manager/operator identity refs are absent, but leave maintainer authorization decisions to Phases 33-35. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: .planning/ROADMAP.md] |
| V11 Cryptography | yes for hashing/digests, no key handling | Store packet hashes and digest refs; never retain private keys, tokens, cert private material, or raw signing payloads. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| V12 Secure Communication | indirect | Preserve TLS/live-service evidence refs from Phase 25; do not copy raw TLS logs, keylogs, tokens, or service payloads. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py] |
| V13 Configuration | yes | Keep secret-bearing configuration values out of retained artifacts and reject fields with token/certificate/credential/private-key markers. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| V14 Data Protection | yes | Retain external refs, digests, provenance, and redaction summaries instead of raw production data or crash dumps. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py] |
| V15 Secure Coding and Architecture | yes | Use functional-core/imperative-shell, boundary parsing, and unit-tested pure policy decisions. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: standards/core/architecture.md; VERIFIED: standards/core/testing.md] |
| V16 Security Logging and Error Handling | yes | Write rejected-submission/quarantine reports that cannot be mistaken for accepted proof and include failure reasons without secret payloads. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |

### Known Threat Patterns for Phase 31

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secret-bearing final packet is retained | Information Disclosure | Reuse Phase 23-26 forbidden field/text scans before writing Phase 31 receipts; retain refs/digests only. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Path traversal or symlink escape in output refs | Tampering / Information Disclosure | Require repo-relative paths under `build/ci-evidence/phaseXX/` or matching `external://phaseXX/` namespaces. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Quick placeholder promoted to final proof | Spoofing / Elevation of Privilege | Require real-evidence flags and reject pending/quick/template command modes. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py] |
| Prose attestation bypasses machine checks | Tampering / Repudiation | Require stream validator command refs, output refs, consumed upstream row refs, and packet hashes. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |
| Phase 31 implies readiness or demotion approval | Elevation of Privilege | Keep finality receipts separate from Phase 33-35 maintainer decisions, readiness, demotion, and cutover verdict artifacts. [VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md] |

## Sources

### Primary (HIGH Confidence)

- `.planning/phases/31-final-evidence-intake/31-CONTEXT.md` - locked decisions, scope, canonical refs, and output constraints. [VERIFIED: file read]
- `.planning/REQUIREMENTS.md` - INTAKE-01 through INTAKE-04 and out-of-scope secret-bearing artifacts. [VERIFIED: file read]
- `.planning/ROADMAP.md` - Phase 31 goal, success criteria, dependency, and downstream Phase 32-35 boundaries. [VERIFIED: file read]
- `.planning/PROJECT.md` and `.planning/STATE.md` - milestone posture, v1.3 scope, and active blockers. [VERIFIED: file read]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/testing.md`, and `standards/core/verification.md` - local and managed workflow constraints. [VERIFIED: file read]
- `tools/bazel/phase23_simulator_evidence_execution.py` and test/contract files - simulator validation, output roots, status vocabulary, and retained row filenames. [VERIFIED: file read and grep]
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` and test/contract files - hardware/media/safety validation, 26 required scenarios, output roots, and upstream rows. [VERIFIED: file read and grep]
- `tools/bazel/phase25_live_service_evidence_execution.py` and test/contract files - live-service validation, 20 required scenarios, output roots, secret guards, and upstream rows. [VERIFIED: file read and grep]
- `tools/bazel/phase26_release_signing_upstream_evidence.py` and test/contract files - release/signing validation, compact upstream row ingestion, canonical Phase 18 row policy, and retained outputs. [VERIFIED: file read and grep]
- `tools/bazel/phase28_final_readiness_packet.py` and Phase 28 context/summary - downstream fail-closed readiness behavior, hard blockers, and reference-demotion separation. [VERIFIED: file read and grep]
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - existing verifier wiring patterns. [VERIFIED: file read and grep]

### Secondary (MEDIUM Confidence)

- OWASP ASVS project page - ASVS purpose and latest stable 5.0.0 note. [CITED: https://owasp.org/www-project-application-security-verification-standard/]
- OWASP Cheat Sheet ASVS index - ASVS 5.0.x category names. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Tertiary (LOW Confidence)

- None used. [VERIFIED: source log above]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - all recommended tools and patterns are already present in Phase 23-28 and local tool versions were probed. [VERIFIED: environment audit commands; VERIFIED: tools/bazel/BUILD.bazel]
- Architecture: HIGH - locked decisions tightly constrain Phase 31 to a wrapper/receipt gate over Phase 23-26. [VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]
- Pitfalls: HIGH - placeholder, secret, artifact-ref, source-ref, redaction, and no-demotion failure modes are covered by existing tests and downstream readiness logic. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence_test.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]
- Security mapping: MEDIUM - ASVS categories are cited from current OWASP pages, while Phase 31-specific controls are mapped to local CLI behavior rather than a formal security requirement set. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/31-final-evidence-intake/31-CONTEXT.md]

**Research date:** 2026-07-03  
**Valid until:** 2026-08-02 for local codebase patterns; re-check OWASP ASVS and tool versions if planning happens after that. [CITED: https://owasp.org/www-project-application-security-verification-standard/; VERIFIED: environment audit commands]
