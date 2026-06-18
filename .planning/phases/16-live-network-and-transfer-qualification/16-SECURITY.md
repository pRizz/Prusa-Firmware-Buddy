---
phase: 16
slug: 16-live-network-and-transfer-qualification
status: verified
threats_open: 0
asvs_level: 1
created: 2026-06-18
---

# Phase 16 - Security

Per-phase security contract for Phase 16 live network and transfer qualification.

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Checked-in JSON contract -> verifier | Contract rows are parsed as untrusted data and schema-validated before use. | Scenario metadata, status vocabularies, source refs |
| Prior evidence refs -> Phase 16 contract | `file#row-id` refs resolve to existing source-backed rows without mutating prior phases. | Phase 9/11/13/14/15 manifest refs |
| Operator JSON -> generated live evidence | External operator evidence requires metadata, valid statuses, guarded refs, redaction, and residual risk. | Operator-supplied live/control-service evidence |
| Contract/operator text -> retained summaries/logs | Evidence text can leak secrets, raw logs, dumps, payloads, or overclaims if not scanned. | Retained summaries, logs, artifact refs |
| CLI output path -> filesystem | Output dirs and artifact refs must stay under ignored Phase 16 evidence root. | `build/ci-evidence/phase16` paths |
| Dry-run quick mode -> maintainer interpretation | Local deterministic artifacts must not be confused for live service qualification. | Scenario status rows |
| Proxy/TLS summaries -> maintainer decisions | Proxy/TLS evidence must preserve proof-scope and limitation boundaries. | Proxy/TLS scenario summaries |
| Bazel/just facade -> maintainer workflow | Workflow wiring must not skip tests or imply live proof. | Bazel labels, `rust_workflow.sh`, `just` recipe |

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-16-01 | Information Disclosure | Operator evidence and generated artifacts | mitigate | Forbidden evidence marker scanner rejects tokens, credentials, private keys/certs, signing keys, payload markers, and secret-bearing headers before operator evidence is accepted or quick artifacts pass security scan. | closed |
| T-16-02 | Information Disclosure | HTTP/TLS logs | mitigate | Scanner rejects raw HTTP/TLS log and keylog markers plus Authorization/Cookie/API-key/password fields; generated artifacts retain redacted summaries and artifact refs. | closed |
| T-16-03 | Information Disclosure | Crash-dump upload evidence | mitigate | Scanner rejects raw crash/RAM/memory dump markers; crash-dump contract row requires hash/consent/redaction-only metadata and external refs. | closed |
| T-16-04 | Spoofing / Repudiation | Local quick mode | mitigate | Default live-service status is `pending-live-input`; only validated operator rows can change scenario status, and passed live rows require live/control-service evidence type. | closed |
| T-16-05 | Tampering | Output paths and artifact refs | mitigate | Filesystem refs and output dirs must be repo-relative under `build/ci-evidence/phase16`; absolute paths, traversal, symlink escapes, and unapproved external refs are rejected. | closed |
| T-16-06 | Repudiation | Operator live evidence rows | mitigate | Operator rows require device/build/operator/timestamp/scenario/result/evidence/surface/mode/artifact/redaction/risk metadata before leaving pending state. | closed |
| T-16-07 | Tampering | Source refs | mitigate | Structured `source_contract_refs` resolve as repo-relative `file#row-id`; doc refs are separately checked by file existence and anchor text. | closed |
| T-16-08 | Spoofing / Repudiation | Proxy/TLS evidence | mitigate | Proxy/TLS rows cite Phase 9 concerns and overclaim scanner rejects full proxy support, proxy authentication, production Connect validation, and TLS proof without operator evidence. | closed |
| T-16-09 | Denial of Service | Live service availability | accept | Missing credentials/endpoints remain truthful pending/manual/controlled/blocked statuses, not verifier failures. | closed |
| T-16-10 | Elevation of Privilege | Verifier command execution | mitigate | Verifier implementation is stdlib-only and contains no subprocess use; tests use argument-list `subprocess.run(..., shell=False)`. | closed |

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-16-09 | T-16-09 | Approved live endpoints, credentials, controlled services, and external artifacts are intentionally outside local verification. The verifier represents their absence with pending/manual/controlled/blocked statuses and does not fail local validation for missing live service availability. | gsd-security-auditor | 2026-06-18 |

## Threat Verification

| Threat ID | Disposition | Evidence |
|-----------|-------------|----------|
| T-16-01 | mitigate | `tools/bazel/phase16_live_network_evidence.py:166` defines forbidden secret/payload patterns; `tools/bazel/phase16_live_network_evidence.py:656` and `tools/bazel/phase16_live_network_evidence.py:703` scan operator input before acceptance; `tools/bazel/phase16_live_network_evidence.py:935` and `tools/bazel/phase16_live_network_evidence.py:941` scan quick artifacts after writing. |
| T-16-02 | mitigate | `tools/bazel/phase16_live_network_evidence.py:173` rejects `raw_http_log`, `raw_tls_log`, TLS keylog, token/fingerprint/API-key/password markers; `tools/bazel/phase16_live_network_evidence.py:893` states retained output is redacted summaries, operator metadata, source snapshots, and artifact refs. |
| T-16-03 | mitigate | `tools/bazel/phase16_live_network_evidence.py:173` rejects raw crash/RAM/memory dump markers; `tools/bazel/manifests/phase16_live_network_evidence_contract.json:1171` through `tools/bazel/manifests/phase16_live_network_evidence_contract.json:1207` define the crash-dump row as hash/consent/redaction evidence with source refs only. |
| T-16-04 | mitigate | `tools/bazel/phase16_live_network_evidence.py:745` defaults live rows to `pending-live-input`; `tools/bazel/phase16_live_network_evidence.py:839` merges only matching operator rows; `tools/bazel/phase16_live_network_evidence.py:725` rejects passed live rows without live/control-service evidence type. |
| T-16-05 | mitigate | `tools/bazel/phase16_live_network_evidence.py:292` rejects absolute/traversing repo paths; `tools/bazel/phase16_live_network_evidence.py:306` checks resolved output containment; `tools/bazel/phase16_live_network_evidence.py:670` allows only contained filesystem refs or `external://`/`artifact://` handles; tests cover traversal and symlink escapes at `tools/bazel/phase16_live_network_evidence_test.py:483` and `tools/bazel/phase16_live_network_evidence_test.py:669`. |
| T-16-06 | mitigate | `tools/bazel/phase16_live_network_evidence.py:97` lists all required operator fields; `tools/bazel/phase16_live_network_evidence.py:701` requires them per row; `tools/bazel/phase16_live_network_evidence.py:706` requires ISO-8601 UTC timestamps; `tools/bazel/phase16_live_network_evidence.py:731` retains only validated required fields. |
| T-16-07 | mitigate | `tools/bazel/phase16_live_network_evidence.py:130` lists Phase 9/11/13/14/15 source manifests; `tools/bazel/phase16_live_network_evidence.py:354` resolves repo-relative `file#row-id`; `tools/bazel/phase16_live_network_evidence.py:368` validates doc refs by file and anchor; `tools/bazel/phase16_live_network_evidence.py:473` and `tools/bazel/phase16_live_network_evidence.py:478` apply both checks to every scenario row. |
| T-16-08 | mitigate | `tools/bazel/manifests/phase16_live_network_evidence_contract.json:272` cites Phase 9 proxy limitation concern; `tools/bazel/manifests/phase16_live_network_evidence_contract.json:832` cites TLS verification policy; `tools/bazel/phase16_live_network_evidence.py:203` rejects overclaim strings including full proxy support, proxy authentication, production Connect validation, and TLS proof without operator evidence. |
| T-16-09 | accept | Accepted risk `AR-16-09`; allowed pending/manual/controlled/blocked states are present in `tools/bazel/phase16_live_network_evidence.py:67`, `tools/bazel/phase16_live_network_evidence.py:77`, and `tools/bazel/manifests/phase16_live_network_evidence_contract.json:5`. |
| T-16-10 | mitigate | `tools/bazel/phase16_live_network_evidence.py:4` through `tools/bazel/phase16_live_network_evidence.py:11` import only stdlib modules and do not import subprocess or network clients; the test harness subprocess use is argument-list based with `shell=False` at `tools/bazel/phase16_live_network_evidence_test.py:44` through `tools/bazel/phase16_live_network_evidence_test.py:51`. |

## Unregistered Flags

No `## Threat Flags` section was present in `16-01-SUMMARY.md`; no unregistered flags recorded.

## Verification Commands

| Command | Result |
|---------|--------|
| `python3 -m json.tool tools/bazel/manifests/phase16_live_network_evidence_contract.json >/dev/null` | passed |
| `python3 tools/bazel/phase16_live_network_evidence.py --contract-only` | passed |
| `python3 tools/bazel/phase16_live_network_evidence.py --security-only` | passed |
| `python3 tools/bazel/phase16_live_network_evidence.py --wiring-only` | passed |

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-18 | 10 | 10 | 0 | gsd-security-auditor |

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-18
