# Phase 09: Network, Web Services, and Transfers - Research

**Researched:** 2026-06-14  
**Domain:** Embedded networking, Prusa Connect, PrusaLink/WUI, TLS/proxy, transfers, telemetry, local services  
**Confidence:** HIGH  
**Lifecycle:** `9-2026-06-14T02-15-21`

<user_constraints>
## User Constraints (from CONTEXT.md)

All bullets in this section are copied from `.planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md`. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

### Locked Decisions

## Implementation Decisions

### Prusa Connect cloud behavior

- **D-01:** Treat the existing `src/connect/`, `src/common/http/`, and `src/connect/tls/` implementation as the Phase 9 reference oracle for Connect registration, telemetry, events, command polling, WebSocket commands, token/fingerprint headers, host decompression, connection reuse, and sleep/backoff behavior.
- **D-02:** Preserve current Connect configuration semantics from the persistent config store, including host, port, TLS flag, token, custom certificate flag, proxy host, proxy port, and enablement. Do not embed token values, Wi-Fi credentials, PrusaLink passwords, certificate bytes, or signing material in manifests, fixtures, logs, or commits.
- **D-03:** Model Connect protocol states in Rust domain contracts instead of passing unchecked strings through the system. Extend the existing `RegistrationCode` and `ConnectEndpoint` style with typed identities for tokens, fingerprints, command IDs, telemetry/event surfaces, WebSocket command states, host/proxy settings, and connection evidence classes.
- **D-04:** Preserve current limitations unless intentionally changed later: whole-response/shared-buffer constraints, single active transfer integration, proxy behavior tied to TLS settings, and disabled/stale manual Connect module tests. Any fixed defect must be named as an intentional delta mapped to IFCE-02 with regression evidence.

### PrusaLink and WUI local services

- **D-05:** Treat `lib/WUI/`, `lib/WUI/nhttp/`, `lib/WUI/link_content/`, and WUI assets packaged by Phase 7 as the reference oracle for the local HTTP server, static web UI, PrusaLink API v1, OctoPrint-compatible endpoints, file/job/status/storage/transfer handlers, and resource-constrained streaming behavior.
- **D-06:** Preserve the embedded server's resource model: streaming parser, limited active connections, shared send buffers, idle/active connection distinction, generated automata, and graceful refusal of unsupported protocol behavior. Do not replace this with a large general-purpose web-server model in Phase 9.
- **D-07:** Preserve local auth semantics for digest authentication and API-key authentication. Phase 9 may name credential-bearing fields and paths, but secret values stay redacted and credential export/display behavior remains tied to Phase 7 storage and Phase 8 GUI contracts.
- **D-08:** Manifest rows for PrusaLink/WUI parity should name endpoint family, retained source paths, auth requirement, storage/transfer integration point, response/error behavior, evidence class, local/non-local proof status, and intentional-delta status.

### Transfer and download semantics

- **D-09:** Treat `src/transfers/`, `src/common/http/`, Connect command initiation, and PrusaLink/WUI transfer endpoints as one parity surface. Preserve single-slot transfer monitor semantics, download range behavior, partial-file direct-sector handling, delete/recreate race assumptions, recovery behavior, encrypted AES-CTR payload handling, storage preconditions, and error mapping.
- **D-10:** Encode transfer invariants in pure Rust domain types before adapter code can use unchecked primitives. Good candidates include transfer source, slot state, range request, partial-file allocation evidence, media identity, encrypted payload metadata, recovery state, and transfer error class.
- **D-11:** Keep transfer media and scheduler proof honest. Local verification may prove manifest coverage, Rust state transitions, parser/error classification, source-path traceability, and host tests. USB/media races, direct-sector writes, network stalls, long-running downloads, and unplug/replug behavior remain simulator, hardware-smoke, or manual evidence until Phase 11.
- **D-12:** Do not redesign concurrency in Phase 9. The single active transfer slot is a compatibility contract unless a later approved phase introduces a new transfer model with explicit v2 scope.

### TLS, proxy, certificates, and security-sensitive paths

- **D-13:** Treat mbedTLS integration in `src/connect/tls/`, socket glue in `src/connect/tls/net_sockets.*`, HTTP CONNECT proxy handling in `src/common/http/proxy.*`, and `doc/proxy_support.md` as the reference surfaces for TLS and proxy parity.
- **D-14:** Preserve required certificate verification and the current TLS 1.2 ECDHE/ECDSA AES-GCM policy while explicitly dispositioning known risks: broken custom DER certificate read path, weak legacy digest modules compiled into mbedTLS, handshake CPU/memory sensitivity, proxy authentication absence, and unencrypted printer-to-proxy leg for minimal proxy support.
- **D-15:** If the custom certificate read bug is fixed in Phase 9, record it as an intentional delta with valid/missing/invalid DER tests and provisioning documentation for `/internal/connect/connect.der`. If it is not fixed, preserve the reference behavior in manifests and mark the defect for cutover review.
- **D-16:** Keep crash dump upload and credential-bearing diagnostics out of Phase 9 green claims unless the plan adds explicit TLS, consent, and redaction evidence. Network secrets remain named-only evidence.

### Telemetry, discovery, metrics, and syslog

- **D-17:** Preserve SNTP, optional mDNS, DNS, metrics, and syslog behavior as local service surfaces tied to `lib/WUI/sntp/`, `lib/WUI/mdns/`, `include/buddy/lwipopts.h`, `src/common/metric*`, `src/logging/log_dest_syslog.cpp`, and `src/syslog/syslog_transport.cpp`.
- **D-18:** Metrics and syslog contracts should preserve runtime config keys, UDP transport behavior, disabled/empty production defaults where applicable, metric throttling semantics, line-protocol-compatible payload shape, and development collector documentation without introducing external-service dependencies into local verification.
- **D-19:** Network startup and service availability should remain product/feature gated through the existing WUI, Connect, and networking options. Rust domain contracts should reject unsupported feature combinations rather than silently enabling services.

### Verification and lifecycle

- **D-20:** Add a Phase 9 verifier exposed through Bazel and `just`, following the Phase 4 through Phase 8 pattern. It should check required manifests, Rust API shape, source-path coverage, concern dispositions, redaction rules, Bazel/just labels, validation artifact presence, lifecycle metadata, and overclaim wording.
- **D-21:** Relevant local verification should include Rust formatting/lint/build/tests, Phase 9 verifier regression tests, a quick `just phase9-verify` path, Bazel queryability for new labels, and lifecycle validation. Heavy firmware builds, simulator network flows, physical network/media tests, long-running transfer tests, and cloud/service integration proof may be recorded as explicit non-local evidence.
- **D-22:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 9-2026-06-14T02-15-21`.

### the agent's Discretion

- Exact manifest names, row IDs, schema field order, Rust type names, and verifier helper structure are flexible if they remain source-backed, reviewable, and covered by tests.
- The planner may split Phase 9 into focused plans by Connect/TLS, PrusaLink/WUI, transfers/downloads, observability/discovery services, Rust domain contracts, known concern dispositions, and aggregate verification.
- Fixture granularity is flexible, but each fixture should prove one network compatibility concern and avoid embedding credentials, certificate bytes, tokens, passwords, private keys, or raw crash dump contents.

### Deferred Ideas (OUT OF SCOPE)

## Deferred Ideas

- Broader proxy authentication, MITM support, or TLS policy expansion beyond the current reference behavior belongs to v2 unless approved as an intentional delta.
- Transfer concurrency redesign beyond the single active slot belongs to v2.
- Full byte-for-byte release, live cloud, hardware network, media race, and cutover proof belongs to Phase 11.
- Auxiliary-controller, MMU, toolchanger, and puppy network/update behavior beyond the transfer integration boundary belongs to Phase 10.
</user_constraints>

## Summary

Plan Phase 9 as a parity-contract phase with implementation guardrails, not as a broad networking rewrite. The reference behavior is split across `src/connect/`, `src/connect/tls/`, `src/common/http/`, `src/transfers/`, `lib/WUI/`, `lib/WUI/nhttp/`, `lib/WUI/link_content/`, `lib/WUI/sntp/`, `lib/WUI/mdns/`, `src/common/metric*`, `src/logging/log_dest_syslog.cpp`, `src/syslog/syslog_transport.cpp`, and config-store keys in `src/persistent_stores/store_instances/config_store/`. [VERIFIED: src/connect/connect.cpp] [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: src/transfers/transfer.cpp] [VERIFIED: lib/WUI/http_lifetime.cpp] [VERIFIED: src/common/metric_handlers.cpp] [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp]

The strongest local plan is to add source-backed manifests, extend `buddy-domain` with typed network/transfer contracts, add Python verifier checks exposed through Bazel and `just`, and use existing Catch2 host-test surfaces as reference evidence where they already exist. [VERIFIED: rust/crates/domain/src/lib.rs] [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: justfile] [VERIFIED: tests/unit/connect/CMakeLists.txt] [VERIFIED: tests/unit/transfers/CMakeLists.txt] [VERIFIED: tests/unit/lib/WUI/nhttp/CMakeLists.txt]

Live Prusa Connect, physical Ethernet/Wi-Fi behavior, USB/media race behavior, long-running transfer proof, simulator network flows, and final cutover proof must be recorded as non-local evidence unless the implementation wave actually runs those environments. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: .planning/REQUIREMENTS.md]

**Primary recommendation:** Build Phase 9 around four manifests (`phase9_connect_contracts.json`, `phase9_wui_contracts.json`, `phase9_transfer_contracts.json`, `phase9_network_service_contracts.json`), one concern-disposition manifest, Rust domain types for unchecked protocol/service state, and `just phase9-verify`; fix the custom DER certificate read bug only as a named IFCE-02 intentional delta with valid/missing/invalid DER fixtures. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: src/connect/tls/tls.cpp]

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IFCE-02 | Rust firmware preserves Prusa Connect behavior for registration, tokens/fingerprints, telemetry, events, WebSocket commands, TLS verification, transfer/download integration, and current proxy limitations unless explicitly fixed. | Use `src/connect/`, `src/common/http/`, `src/connect/tls/`, `src/common/http/proxy.*`, `src/transfers/`, Connect host tests, typed Rust protocol contracts, TLS/proxy concern dispositions, and non-local evidence classes for cloud/TLS/runtime proof. [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: src/connect/connect.cpp] [VERIFIED: src/connect/registrator.cpp] [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: src/common/http/proxy.cpp] [VERIFIED: tests/unit/connect/CMakeLists.txt] |
| IFCE-03 | Rust firmware preserves PrusaLink/WUI behavior including HTTP API v1, OctoPrint-compatible endpoints, digest/API-key auth, WUI static assets, SNTP, mDNS, metrics, and syslog. | Use `lib/WUI/http_lifetime.cpp`, `lib/WUI/nhttp/`, `lib/WUI/link_content/`, Phase 7 WUI asset contracts, `lib/WUI/sntp/`, `lib/WUI/mdns/`, `include/buddy/lwipopts.h`, `src/common/metric*`, and `src/logging/log_dest_syslog.cpp` as the oracle set. [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: lib/WUI/http_lifetime.cpp] [VERIFIED: lib/WUI/nhttp/req_parser.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api_octo.cpp] [VERIFIED: lib/WUI/sntp/sntp_client.c] [VERIFIED: lib/WUI/mdns/mdns.c] [VERIFIED: src/common/metric_handlers.cpp] |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Follow repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the pinned Bright Builds standards before planning or implementation. [VERIFIED: AGENTS.md] [VERIFIED: AGENTS.bright-builds.md] [VERIFIED: standards-overrides.md]
- Preserve the project decisions: Big Bang Rust replacement, behavior parity, Bazel primary from the start, required `justfile` workflow, Bright Builds standards, safety evidence before replacement, and named justification for retained foreign/vendor/HAL/generated code. [VERIFIED: AGENTS.md] [VERIFIED: .planning/PROJECT.md]
- Use functional-core/imperative-shell structure: pure Rust domain contracts should parse and validate raw protocol/config values before adapter/runtime code uses them. [CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md] [VERIFIED: rust/crates/domain/src/lib.rs]
- Keep Rust code idiomatic, forbid unsafe in pure crates, avoid `unwrap()`/`expect()` except proven-infallible, parse raw input into domain types, and return `Result` for fallible construction. [CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md] [VERIFIED: Cargo.toml]
- Unit tests should follow behavior-focused Arrange, Act, Assert structure where it improves clarity, and bug fixes should add regression coverage. [CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md]
- Do not put token values, Wi-Fi credentials, PrusaLink passwords, certificate bytes, private keys, signing material, or raw crash dump contents in manifests, fixtures, logs, commits, or planning artifacts. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: doc/prusa_printer_settings.ini]
- No project-local `.claude/skills/` or `.agents/skills/` directory exists, so there are no repo skill patterns to apply. [VERIFIED: find . -maxdepth 3]

## Standard Stack

### Core

| Library / Component | Version | Purpose | Why Standard |
|---------------------|---------|---------|--------------|
| Rust workspace / `buddy-domain` | edition 2024, rust-version 1.85 | Pure domain contracts for protocol, service, transfer, evidence, and feature-gate invariants. | Existing project architecture already uses `buddy-domain` as the functional core for checked primitives and state machines. [VERIFIED: Cargo.toml] [VERIFIED: rust/crates/domain/src/lib.rs] |
| Bazel `shell_binary` verifier pattern | Bazel 9.1.1 locally | Authoritative local verification target exposed through `//tools/bazel:*`. | Phases 4-8 already expose verifiers through `tools/bazel/BUILD.bazel`; Phase 9 should follow that pattern. [VERIFIED: bazel --version] [VERIFIED: tools/bazel/BUILD.bazel] |
| `justfile` facade | just 1.48.0 locally | Stable developer command for `phase9-verify`. | Existing phase verifier recipes use `just phaseN-verify`; Phase 9 should add the same facade. [VERIFIED: just --version] [VERIFIED: justfile] |
| Python verifier | Python 3.14.4 locally | Manifest/schema/source coverage/overclaim/redaction/lifecycle checks. | Existing phase verifier scripts are Python and are run by Bazel shell targets. [VERIFIED: python3 --version] [VERIFIED: tools/bazel/phase8_verify.py] |
| Connect reference implementation | Repo source | Registration, token/fingerprint identity, telemetry/events, WebSocket commands, sleep/backoff, host compression, connection reuse. | Locked oracle for IFCE-02. [VERIFIED: src/connect/connect.cpp] [VERIFIED: src/connect/registrator.cpp] [VERIFIED: src/connect/hostname.cpp] |
| Custom nhttp/WUI server | Repo source | Local HTTP API v1, OctoPrint-compatible endpoints, digest/API-key auth, static assets, uploads, parser/server limits. | Locked oracle for IFCE-03 and intentionally resource constrained. [VERIFIED: lib/WUI/nhttp/README.md] [VERIFIED: lib/WUI/http_lifetime.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp] |
| Transfer subsystem | Repo source | Single-slot transfer monitor, range downloads, partial files, AES-CTR encrypted downloads, recovery, error mapping. | Connect and WUI transfers share this behavior and must be treated as one surface. [VERIFIED: src/transfers/monitor.hpp] [VERIFIED: src/transfers/download.cpp] [VERIFIED: src/transfers/transfer.cpp] |
| mbedTLS | 2.28.0 vendored | TLS 1.2 and AES-CTR support for Connect and transfers. | Existing TLS and transfer crypto depend on this vendored stack; do not replace in Phase 9. [VERIFIED: lib/Middlewares/Third_Party/mbedtls/include/mbedtls/version.h] [VERIFIED: include/mbedtls/cipher_config_ece.h] |
| LwIP | 2.1.2 vendored | TCP/IP, DNS, UDP, mDNS dependency, raw/altcp network plumbing. | Existing WUI, Connect sockets, SNTP, metrics, and syslog all ride on LwIP. [VERIFIED: lib/Middlewares/Third_Party/LwIP/src/include/lwip/init.h] [VERIFIED: include/buddy/lwipopts.h] |

### Supporting

| Library / Component | Version | Purpose | When to Use |
|---------------------|---------|---------|-------------|
| FreeRTOS | Kernel V10.6.2 vendored | Network, metric, WUI, and firmware task orchestration. | Use for parity classification and non-local scheduling evidence; do not redesign tasking in Phase 9. [VERIFIED: lib/Middlewares/Third_Party/FreeRTOS/Source/tasks.c] [VERIFIED: lib/WUI/wui.cpp] |
| Catch2 | 2.13.7 vendored | Existing C++ host tests for Connect, WUI/nhttp, and transfers. | Use as reference evidence or fixtures; do not rely on stale module Connect target. [VERIFIED: lib/Catch2/include/catch.hpp] [VERIFIED: tests/unit/connect/CMakeLists.txt] [VERIFIED: tests/module/Connect/CMakeLists.txt] |
| Docker / Docker Compose metrics stack | Docker 29.3.1 available locally | Optional developer metrics collector stack under `utils/metrics`. | Treat as documentation/dev tooling only; local Phase 9 verification must not require an external metrics service. [VERIFIED: docker --version] [VERIFIED: doc/metrics.md] |
| OpenSSL CLI | OpenSSL 3.6.2 locally | Generate synthetic DER/certificate fixtures if Phase 9 fixes custom DER handling. | Use for test fixture generation only; do not use as firmware TLS implementation. [VERIFIED: openssl version] [VERIFIED: src/connect/tls/tls.cpp] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom nhttp/WUI oracle | General-purpose embedded HTTP framework | Reject for Phase 9 because the reference server intentionally uses streaming parsing, shared buffers, active/idle connection states, generated automata, and graceful refusal of unsupported features. [VERIFIED: lib/WUI/nhttp/README.md] |
| Vendored mbedTLS oracle | Rust TLS stack | Reject for Phase 9 because behavior parity depends on existing TLS version policy, cipher suite configuration, mbedTLS socket glue, custom cert behavior, and embedded memory/CPU constraints. [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: include/mbedtls/cipher_config_ece.h] |
| Single-slot transfer monitor | Multi-transfer redesign | Reject for Phase 9 because the single active slot is a locked compatibility contract and concurrency redesign is deferred to v2. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: src/transfers/monitor.hpp] |

**Installation:**

```bash
# No new packages for Phase 9 research/planning.
# Use the repo-vendored C/C++ networking stack, existing Rust workspace, Python stdlib verifier style, Bazel, and just.
```

**Version verification:** No npm packages apply to this phase. Versions above were verified from local CLI output or vendored source headers instead of training data. [VERIFIED: bazel --version] [VERIFIED: just --version] [VERIFIED: cargo --version] [VERIFIED: rustc --version] [VERIFIED: lib/Middlewares/Third_Party/mbedtls/include/mbedtls/version.h] [VERIFIED: lib/Middlewares/Third_Party/LwIP/src/include/lwip/init.h]

## Architecture Patterns

### Recommended Project Structure

```text
rust/crates/domain/src/
  network.rs                      # Phase 9 checked service/protocol/transfer contracts
  lib.rs                          # Re-export Phase 9 domain types

tools/bazel/
  manifests/
    phase9_connect_contracts.json
    phase9_wui_contracts.json
    phase9_transfer_contracts.json
    phase9_network_service_contracts.json
    phase9_network_concern_dispositions.json
  phase9_verify.py
  phase9_verify_test.py
  BUILD.bazel

.planning/phases/09-network-web-services-and-transfers/
  09-VALIDATION.md
```

This structure matches the prior phase pattern of domain contracts plus source-backed manifests plus a Python verifier exposed through Bazel and `just`. [VERIFIED: rust/crates/domain/src/lib.rs] [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: justfile] [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

### Pattern 1: Source-Backed Manifest Rows

**What:** Each parity claim names its source path(s), protocol/service surface, evidence class, proof scope, requirement ID, lifecycle ID, and intentional-delta status. [VERIFIED: tools/bazel/phase8_verify.py]  
**When to use:** Use for Connect, WUI, transfer, TLS/proxy, SNTP, mDNS, metrics, and syslog claims before implementation waves claim parity. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

**Example:**

```json
{
  "id": "connect-websocket-large-command",
  "requirement_id": "IFCE-02",
  "surface": "connect-websocket-command",
  "source_paths": [
    "src/connect/connect.cpp",
    "src/common/http/websocket.cpp"
  ],
  "behavior": "Large or multi-buffer WebSocket commands are rejected as oversized instead of consuming transfer/shared buffers.",
  "evidence_class": "source-audit",
  "proof_scope": "local",
  "intentional_delta_status": "none",
  "phase_lifecycle_id": "9-2026-06-14T02-15-21"
}
```

The example mirrors existing Phase 8 verifier concepts and avoids secret values. [VERIFIED: tools/bazel/phase8_verify.py] [VERIFIED: src/connect/connect.cpp]

### Pattern 2: Pure Rust Domain Contracts Before Adapters

**What:** Add newtypes/enums for raw network values and protocol states so invalid tokens, fingerprints, command IDs, transfer ranges, evidence classes, proxy modes, WUI auth modes, and service surfaces fail before adapter code runs. [VERIFIED: rust/crates/domain/src/protocol.rs] [VERIFIED: rust/crates/domain/src/gui.rs]  
**When to use:** Use for every unchecked string/number that appears in manifests or runtime config contracts. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

**Example:**

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NetworkEvidenceClass {
    ManifestCheck,
    SourceAudit,
    StaticSourceAudit,
    HostTest,
    RustHostTest,
    SimulatorFlow,
    HardwareSmoke,
    ManualHardwareRequired,
}

impl NetworkEvidenceClass {
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "manifest-check" => Ok(Self::ManifestCheck),
            "source-audit" => Ok(Self::SourceAudit),
            "static-source-audit" => Ok(Self::StaticSourceAudit),
            "host-test" => Ok(Self::HostTest),
            "rust-host-test" => Ok(Self::RustHostTest),
            "simulator-flow" => Ok(Self::SimulatorFlow),
            "hardware-smoke" => Ok(Self::HardwareSmoke),
            "manual-hardware-required" => Ok(Self::ManualHardwareRequired),
            _ => Err(InvariantError::InvalidNetworkEvidenceClass),
        }
    }
}
```

This follows the existing `EvidenceClass` and `GuiEvidenceClass` parse style. [VERIFIED: rust/crates/domain/src/safety.rs] [VERIFIED: rust/crates/domain/src/gui.rs]

### Pattern 3: Concern Disposition Ledger

**What:** Every known Phase 9 risk gets a row with `preserved`, `fixed-intentional-delta`, or `deferred`, plus source path, requirement mapping, proof scope, and regression evidence. [VERIFIED: .planning/codebase/CONCERNS.md] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]  
**When to use:** Use for custom DER cert read, weak digest modules compiled into mbedTLS, TLS handshake resource sensitivity, proxy limitations, stale module Connect tests, whole-response buffers, transfer media races, transfer monitor lock-order hazards, and duplicate command/shared-buffer behavior. [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: include/mbedtls/cipher_config_ece.h] [VERIFIED: tests/module/Connect/CMakeLists.txt] [VERIFIED: src/transfers/monitor.hpp] [VERIFIED: src/connect/planner.cpp]

### Pattern 4: Overclaim Guard

**What:** The Phase 9 verifier rejects artifacts claiming local green evidence for live cloud, physical networking, USB/media races, long-running transfers, simulator network flows, or final cutover unless the row records the correct non-local evidence class. [VERIFIED: tools/bazel/phase8_verify.py] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]  
**When to use:** Use in `phase9_verify.py` and its tests from Wave 0. [VERIFIED: tools/bazel/phase8_verify_test.py]

### Anti-Patterns to Avoid

- **Replacing WUI with a generic server:** This would discard streaming parser, active/idle connection limits, shared buffers, generated automata, and unsupported-protocol refusal semantics. [VERIFIED: lib/WUI/nhttp/README.md]
- **Treating Connect and transfer as separate proof surfaces:** Connect download commands, WUI transfer endpoints, and `src/transfers/` share the same monitor/recovery/file semantics. [VERIFIED: src/connect/command.hpp] [VERIFIED: lib/WUI/nhttp/gcode_upload.cpp] [VERIFIED: src/transfers/transfer.cpp]
- **Logging or fixture-capturing secrets:** Phase 9 may name secret-bearing keys but must not include values or cert bytes. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: doc/prusa_printer_settings.ini]
- **Using stale Connect module tests as current evidence:** `tests/module/Connect/CMakeLists.txt` still references obsolete `src/Connect/...` paths, while current code lives under `src/connect/...`. [VERIFIED: tests/module/Connect/CMakeLists.txt] [VERIFIED: src/connect/connect.cpp]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TLS, certificate verification, AES-CTR | A custom TLS or crypto implementation | Existing mbedTLS integration and transfer decryptor | Current behavior depends on TLS 1.2, required verification, a specific ECDHE/ECDSA AES-GCM suite, mbedTLS socket glue, and AES-CTR transfer metadata. [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: include/mbedtls/cipher_config_ece.h] [VERIFIED: src/transfers/decrypt.hpp] |
| WUI HTTP serving | A generic web server abstraction | `lib/WUI/nhttp` contracts and source-backed parity | The embedded server is intentionally streaming, memory-constrained, generated-automata based, and active-slot limited. [VERIFIED: lib/WUI/nhttp/README.md] [VERIFIED: lib/WUI/nhttp/server.cpp] |
| Transfer concurrency | Multi-slot scheduler | Existing `transfers::Monitor` single-slot model | Single active transfer is locked compatibility behavior for Phase 9. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: src/transfers/monitor.hpp] |
| Digest/API-key auth | New auth scheme | Existing parser/auth semantics in `lib/WUI/nhttp/req_parser.cpp` | Existing behavior includes digest nonce age/stale handling, MD5 HA1/HA2, and API-key full-match behavior. [VERIFIED: lib/WUI/nhttp/req_parser.cpp] |
| Metrics collector | External service dependency in local verification | Manifest/source checks and optional Docker docs only | Metrics documentation uses Docker for a dev collector, but local Phase 9 verification must not require external services. [VERIFIED: doc/metrics.md] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] |
| URL/path validation | Ad hoc path string checks in verifier or adapters | Existing WUI path parser behavior plus Rust domain newtypes | Existing API path parsing remaps OctoPrint roots and restricts file operations to `/usb` or `/usb/...`. [VERIFIED: lib/WUI/link_content/prusa_link_api.cpp] [VERIFIED: lib/WUI/nhttp/req_parser.cpp] |

**Key insight:** The hard part in Phase 9 is preserving embedded limits, failure modes, and proof scope; custom replacements would erase the exact behavior the phase is meant to preserve. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: lib/WUI/nhttp/README.md] [VERIFIED: src/transfers/partial_file.cpp]

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | Network and service config store keys include PrusaLink enabled/password, Connect host/token/proxy/TLS/custom-cert/ports, Wi-Fi SSID/password, hostname, metrics host/port, syslog port, and enable-metrics flag. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp] | Preserve key names and value semantics in contracts; do not migrate or rename keys in Phase 9 unless a separate migration is explicitly planned. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Stored data | Connect default host is compressed as `buddy-a.\x01\x01`, default Connect port is 443, token/proxy defaults are empty, and metrics defaults differ by build configuration. [VERIFIED: src/persistent_stores/store_instances/config_store/defaults.hpp] | Manifest host compression and defaults as source facts; avoid embedding actual runtime tokens, passwords, or Wi-Fi secrets. [VERIFIED: src/connect/hostname.cpp] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] |
| Live service config | Prusa Connect registration creates/preserves a cloud token identity and uses printer fingerprint/token headers, but live cloud proof is not local evidence. [VERIFIED: src/connect/registrator.cpp] [VERIFIED: src/connect/connect.cpp] | Record live Connect registration as `manual-hardware-required` or equivalent non-local evidence unless a live test environment is explicitly run. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] |
| Live service config | Optional metrics dev collector lives outside firmware under Docker-based docs. [VERIFIED: doc/metrics.md] | Do not require external collector availability for `phase9-verify`; verify payload/config contracts locally. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] |
| OS-registered state | None found in repo-local Phase 9 surfaces; firmware tasks are FreeRTOS runtime tasks, not host OS registrations. [VERIFIED: lib/WUI/wui.cpp] [VERIFIED: src/common/metric.cpp] | No OS re-registration task is needed for planning. [VERIFIED: rg OS/service audit] |
| Secrets/env vars | Secret-bearing fields exist in config/import surfaces: Connect token, Wi-Fi password, PrusaLink password, certificate bytes, and signing key paths. [VERIFIED: doc/prusa_printer_settings.ini] [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp] | Use named-only redacted evidence; verifier should reject fields such as `token_value`, `password_value`, `private_key`, and certificate byte payloads. [VERIFIED: tools/bazel/phase8_verify.py] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] |
| Build artifacts | Existing Phase 4-8 Bazel verifier labels and `just` recipes are present; Phase 9 labels and recipe are not yet present. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: justfile] | Add `phase9_verify`, `phase9_verify_tests`, root aliases, and `phase9-verify`. [VERIFIED: tools/bazel/BUILD.bazel] |
| Build artifacts | Stale module Connect test target points at `src/Connect/...`, not current `src/connect/...`. [VERIFIED: tests/module/Connect/CMakeLists.txt] | Do not use that target as current evidence; either disposition it or keep it as stale manual material in the concern ledger. [VERIFIED: .planning/codebase/CONCERNS.md] |

## Common Pitfalls

### Pitfall 1: Overclaiming Local Network Evidence

**What goes wrong:** A plan marks cloud registration, TLS handshakes, Wi-Fi/Ethernet runtime behavior, USB/media races, or long-running transfers as locally verified when only manifests or host tests ran. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]  
**Why it happens:** Prior phase verifier checks are local and deterministic, while this phase includes physical, cloud, media, and timing-dependent behavior. [VERIFIED: tools/bazel/phase8_verify.py] [VERIFIED: src/transfers/partial_file.cpp]  
**How to avoid:** Require `proof_scope` and `evidence_class` fields, then reject local proof scope for simulator/hardware/manual-only behavior. [VERIFIED: tools/bazel/phase8_verify.py]  
**Warning signs:** Words like "complete", "cutover-ready", "cloud verified", or "hardware verified" appear without non-local evidence references. [VERIFIED: tools/bazel/phase8_verify.py]

### Pitfall 2: Losing Embedded HTTP Server Limits

**What goes wrong:** A Rust/WUI plan models endpoints but omits active/idle connection state, shared send buffers, generated parser automata, limited active requests, and refusal of unsupported protocol behavior. [VERIFIED: lib/WUI/nhttp/README.md]  
**Why it happens:** Desktop HTTP server assumptions hide memory and streaming constraints. [VERIFIED: lib/WUI/nhttp/README.md]  
**How to avoid:** Put server resource limits in `phase9_wui_contracts.json` and add verifier-required source paths for `lib/WUI/nhttp/server.cpp`, `req_parser.cpp`, and automata generation. [VERIFIED: lib/WUI/nhttp/server.cpp] [VERIFIED: tests/unit/lib/WUI/nhttp/CMakeLists.txt]  
**Warning signs:** A WUI endpoint row only lists URL/method/status and omits resource-model fields. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

### Pitfall 3: Treating Transfer Writes Like Normal Filesystem Writes

**What goes wrong:** A plan misses direct-sector partial-file writes, contiguous allocation, recovery backups, range jumps, delete/recreate race assumptions, and unplug/replug behavior. [VERIFIED: src/transfers/partial_file.cpp] [VERIFIED: src/transfers/transfer.cpp]  
**Why it happens:** Transfer behavior crosses HTTP, monitor state, FatFs/media behavior, and recovery metadata. [VERIFIED: src/transfers/download.cpp] [VERIFIED: src/transfers/transfer_recovery.cpp]  
**How to avoid:** Keep a dedicated transfer manifest with source paths for `monitor`, `download`, `transfer`, `partial_file`, `transfer_recovery`, and WUI upload/inject paths. [VERIFIED: src/transfers/monitor.hpp] [VERIFIED: lib/WUI/nhttp/gcode_upload.cpp] [VERIFIED: lib/WUI/nhttp/server.cpp]  
**Warning signs:** Transfer proof lacks `single-slot`, `range`, `recovery`, `partial-file`, or `media-race` classification. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

### Pitfall 4: Hiding TLS/Proxy Defects

**What goes wrong:** The custom DER cert read bug, SHA1/MD5 module exposure, no proxy auth, plaintext printer-to-proxy leg, and handshake resource sensitivity are neither preserved nor fixed as named deltas. [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: include/mbedtls/cipher_config_ece.h] [VERIFIED: doc/proxy_support.md]  
**Why it happens:** TLS code can look "secure enough" from cipher-suite configuration while still carrying integration and provisioning defects. [VERIFIED: src/connect/tls/tls.cpp]  
**How to avoid:** Require a concern disposition row for each TLS/proxy issue and map fixed items to IFCE-02 intentional deltas. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]  
**Warning signs:** TLS rows only mention "mbedTLS" or "cert verification" without custom cert, weak digest module, proxy, and handshake fields. [VERIFIED: .planning/codebase/CONCERNS.md]

### Pitfall 5: Missing Auth Edge Semantics

**What goes wrong:** The plan preserves endpoint families but omits digest nonce/stale behavior, API-key full-match behavior, empty-password login disable behavior, and generated password failure semantics. [VERIFIED: lib/WUI/nhttp/req_parser.cpp] [VERIFIED: lib/WUI/wui.cpp]  
**Why it happens:** Auth details are split across WUI password generation, config store, and request parser code. [VERIFIED: lib/WUI/wui.cpp] [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp]  
**How to avoid:** Give auth its own `WuiAuthMode` Rust contract and required WUI manifest rows. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

## Code Examples

### Manifest Schema Guard

```python
REQUIRED_CONNECT_FIELDS = {
    "id",
    "requirement_id",
    "surface",
    "source_paths",
    "behavior",
    "evidence_class",
    "proof_scope",
    "intentional_delta_status",
    "phase_lifecycle_id",
}
```

Use a required-field set per manifest family, then reuse common helpers for lifecycle, redaction, source-path existence, evidence/proof compatibility, and overclaim wording. [VERIFIED: tools/bazel/phase8_verify.py]

### Secret Redaction Guard

```python
FORBIDDEN_SECRET_FIELDS = {
    "token_value",
    "password_value",
    "wifi_password",
    "private_key",
    "certificate_bytes",
    "crash_dump_payload",
}
```

The verifier should reject value-bearing secret fields while allowing named config keys such as `connect_token`, `prusalink_password`, and `wifi_ap_password`. [VERIFIED: tools/bazel/phase8_verify.py] [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp]

### Rust Transfer Range Contract

```rust
pub struct TransferRange {
    start: u64,
    maybe_inclusive_end: Option<u64>,
}

impl TransferRange {
    pub fn new(start: u64, maybe_inclusive_end: Option<u64>) -> Result<Self, InvariantError> {
        if let Some(inclusive_end) = maybe_inclusive_end {
            if inclusive_end < start {
                return Err(InvariantError::InvalidTransferRange);
            }
        }

        Ok(Self {
            start,
            maybe_inclusive_end,
        })
    }
}
```

The shape matches project Rust naming and constructor patterns; the exact error/type names should fit the final `buddy-domain` module. [VERIFIED: AGENTS.md] [VERIFIED: rust/crates/domain/src/resource.rs] [VERIFIED: src/transfers/download.cpp]

## State of the Art

| Old / Risky Approach | Current Approach for Phase 9 | When Changed / Source | Impact |
|----------------------|------------------------------|-----------------------|--------|
| Plan from endpoint names only | Plan from source-backed manifests with evidence classes and concern dispositions | Established by Phase 5-8 verifier pattern. [VERIFIED: tools/bazel/phase5_verify.py] [VERIFIED: tools/bazel/phase8_verify.py] | Prevents broad claims without source and proof mapping. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] |
| Treat WUI as ordinary HTTP API | Preserve custom nhttp streaming/resource model | Current WUI README and server code. [VERIFIED: lib/WUI/nhttp/README.md] [VERIFIED: lib/WUI/nhttp/server.cpp] | Avoids regressions in memory-constrained firmware behavior. [VERIFIED: lib/WUI/nhttp/README.md] |
| Treat transfer as download-only | Treat Connect commands, WUI upload/transfer endpoints, monitor, media, recovery, and AES-CTR as one surface | Current transfer and WUI integration. [VERIFIED: src/connect/command.hpp] [VERIFIED: src/transfers/transfer.cpp] [VERIFIED: lib/WUI/nhttp/gcode_upload.cpp] | Preserves single-slot and recovery semantics across entry points. [VERIFIED: src/transfers/monitor.hpp] |
| Ignore stale manual Connect tests | Disposition stale module tests and use current host/unit surfaces | `tests/module/Connect` points to `src/Connect`, while current code uses `src/connect`. [VERIFIED: tests/module/Connect/CMakeLists.txt] [VERIFIED: src/connect/connect.cpp] | Prevents false confidence from obsolete test wiring. [VERIFIED: .planning/codebase/CONCERNS.md] |
| Rely on ASVS 4 category assumptions | Use current ASVS 5.0.0 categories for security mapping | OWASP lists ASVS 5.0.0 as latest stable. [CITED: https://owasp.org/www-project-application-security-verification-standard/] | Security mapping should include current web/API/file/config categories, but only where they apply to firmware. [CITED: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/] |

**Deprecated/outdated:**

- `tests/module/Connect` is outdated for current Connect source layout because it references `src/Connect/...` paths that do not match the current lowercase `src/connect/...` implementation. [VERIFIED: tests/module/Connect/CMakeLists.txt] [VERIFIED: src/connect/connect.cpp]
- Treating custom certificate support as simply "available" is unsafe because current `tls.cpp` opens and sizes `/internal/connect/connect.der` but does not read bytes before `mbedtls_x509_crt_parse_der_nocopy`. [VERIFIED: src/connect/tls/tls.cpp]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| - | No assumed claims. | All sections | All technical claims are tied to repo inspection, phase context, local command output, or cited official docs. |

## Open Questions

1. **Will Phase 9 fix the custom DER certificate read bug?**  
   What we know: The source opens `/internal/connect/connect.der`, determines file length, allocates a buffer, and calls `mbedtls_x509_crt_parse_der_nocopy`, but the audited path lacks a data read before parse. [VERIFIED: src/connect/tls/tls.cpp]  
   What's unclear: Whether the phase execution budget includes valid/missing/invalid DER fixtures and provisioning docs. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]  
   Recommendation: Plan the fix as an IFCE-02 intentional delta only if Wave 0 adds regression fixtures; otherwise preserve and mark for cutover review. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

2. **How exhaustive should WUI endpoint manifests be in this phase?**  
   What we know: WUI routing includes PrusaLink API v1, OctoPrint-compatible endpoints, USB files, previews, static assets, and unknown-request handling. [VERIFIED: lib/WUI/http_lifetime.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api_octo.cpp]  
   What's unclear: Whether the planner wants one row per endpoint or one row per endpoint family. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]  
   Recommendation: Use endpoint-family rows with representative method/status/auth/error fields, then add child fixture IDs only where behavior differs materially. [VERIFIED: tools/bazel/phase8_verify.py]

3. **Is live Connect/cloud or network hardware available during execution?**  
   What we know: Local environment has Bazel, just, Rust, Python, Docker, CMake, Ninja, and OpenSSL, but no live printer/cloud credentials were provided. [VERIFIED: bazel --version] [VERIFIED: just --version] [VERIFIED: cargo --version] [VERIFIED: python3 --version]  
   What's unclear: Whether hardware, simulator network, or Connect test credentials will be available in a later verification phase. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]  
   Recommendation: Keep all such proof as non-local evidence unless the executor records concrete run artifacts. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Bazel | Phase 9 verifier labels and queryability | yes | 9.1.1 | Blocking if missing; install Bazel before execution. [VERIFIED: bazel --version] |
| just | `phase9-verify` developer facade | yes | 1.48.0 | Use direct Bazel commands if just is unavailable. [VERIFIED: just --version] |
| Rust/Cargo | `buddy-domain` types and Rust tests | yes | cargo 1.91.1, rustc 1.91.1 | Blocking if missing or older than workspace rust-version 1.85. [VERIFIED: cargo --version] [VERIFIED: rustc --version] [VERIFIED: Cargo.toml] |
| Python 3 | Verifier scripts/tests | yes | 3.14.4 | Blocking for verifier execution. [VERIFIED: python3 --version] |
| CMake | Existing C++ host-test reference surfaces | yes | 3.27.9 | Repo bootstrap can provide pinned dependencies if needed; local version exceeds project minimum 3.22. [VERIFIED: cmake --version] [VERIFIED: CMakeLists.txt] |
| Ninja | Existing C++ host-test reference surfaces | yes | 1.13.2 | Use repo bootstrap if a pinned Ninja is required. [VERIFIED: ninja --version] [VERIFIED: utils/bootstrap.py] |
| Docker | Optional metrics collector docs | yes | 29.3.1 | Do not require for local Phase 9 verification; metrics collector is optional dev tooling. [VERIFIED: docker --version] [VERIFIED: doc/metrics.md] |
| OpenSSL CLI | Optional synthetic DER/cert fixtures | yes | 3.6.2 | Pre-generate fixtures or use repo scripts if OpenSSL is unavailable. [VERIFIED: openssl version] [VERIFIED: tests/module/Connect/test-server/tls/gen_cert.sh] |

**Missing dependencies with no fallback:** None found for local research/planning and Phase 9 verifier work. [VERIFIED: environment audit]

**Missing dependencies with fallback:** Repo-pinned `.dependencies/cmake-3.28.3/bin/cmake` is not present, but system CMake 3.27.9 is available and satisfies the root CMake minimum for host reference tests. [VERIFIED: .dependencies probe] [VERIFIED: CMakeLists.txt]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib verifier tests, Rust unit tests, Bazel `shell_binary`, and existing Catch2 host-test references. [VERIFIED: tools/bazel/phase8_verify_test.py] [VERIFIED: Cargo.toml] [VERIFIED: tests/unit/connect/CMakeLists.txt] |
| Config file | `.planning/config.json` enables `workflow.nyquist_validation`; Bazel targets live in `tools/bazel/BUILD.bazel`; Rust workspace config lives in `Cargo.toml`; `justfile` exposes phase commands. [VERIFIED: .planning/config.json] [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: Cargo.toml] [VERIFIED: justfile] |
| Quick run command | `bazel run //tools/bazel:phase9_verify_tests && bazel run //tools/bazel:phase9_verify` after Wave 0 creates the targets. [VERIFIED: tools/bazel/BUILD.bazel] |
| Full suite command | `just phase9-verify` after Wave 0 adds the recipe. [VERIFIED: justfile] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| IFCE-02 | Connect registration, token/fingerprint headers, telemetry/events, command/WebSocket behavior, TLS/proxy, transfer integration. | manifest verifier + Rust unit + source audit + existing Catch2 references | `bazel run //tools/bazel:phase9_verify` and `cargo test -p buddy-domain network` | No for Phase 9 verifier/domain module; existing C++ refs exist. [VERIFIED: tests/unit/connect/CMakeLists.txt] [VERIFIED: rust/crates/domain/src/lib.rs] |
| IFCE-02 | Custom certificate/proxy limitations and known network concerns. | verifier regression + optional fixture test | `bazel run //tools/bazel:phase9_verify_tests` | No; Wave 0 gap. [VERIFIED: src/connect/tls/tls.cpp] |
| IFCE-03 | PrusaLink/WUI API v1, OctoPrint endpoints, auth, static assets, SNTP, mDNS, metrics, syslog. | manifest verifier + Rust unit + source audit + existing Catch2 references | `bazel run //tools/bazel:phase9_verify` and `cargo test -p buddy-domain network` | No for Phase 9 verifier/domain module; existing WUI/nhttp refs exist. [VERIFIED: tests/unit/lib/WUI/nhttp/CMakeLists.txt] |
| IFCE-03 | Metrics/syslog and discovery service contracts. | manifest verifier + source audit | `bazel run //tools/bazel:phase9_verify` | No; Wave 0 gap. [VERIFIED: src/common/metric_handlers.cpp] [VERIFIED: src/logging/log_dest_syslog.cpp] [VERIFIED: lib/WUI/mdns/mdns.c] |

### Sampling Rate

- **Per task commit:** Run `cargo test -p buddy-domain network` for Rust domain changes and `bazel run //tools/bazel:phase9_verify_tests` for verifier changes after those targets exist. [VERIFIED: Cargo.toml] [VERIFIED: tools/bazel/BUILD.bazel]
- **Per wave merge:** Run `bazel run //tools/bazel:phase9_verify_tests && bazel run //tools/bazel:phase9_verify`. [VERIFIED: tools/bazel/BUILD.bazel]
- **Phase gate:** Run `just phase9-verify`, `just bazel-query`, and the relevant Rust checks before `/gsd-verify-work`. [VERIFIED: justfile] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]

### Wave 0 Gaps

- [ ] `rust/crates/domain/src/network.rs` or equivalent module: checked Phase 9 Connect/WUI/transfer/network evidence types. [VERIFIED: rust/crates/domain/src/lib.rs]
- [ ] `tools/bazel/manifests/phase9_connect_contracts.json`: Connect/TLS/proxy/command/telemetry/transfer source rows. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]
- [ ] `tools/bazel/manifests/phase9_wui_contracts.json`: WUI endpoint/auth/static/resource rows. [VERIFIED: lib/WUI/http_lifetime.cpp]
- [ ] `tools/bazel/manifests/phase9_transfer_contracts.json`: single-slot/range/encryption/recovery/error rows. [VERIFIED: src/transfers/transfer.cpp]
- [ ] `tools/bazel/manifests/phase9_network_service_contracts.json`: SNTP/mDNS/DNS/metrics/syslog rows. [VERIFIED: lib/WUI/sntp/sntp_client.c] [VERIFIED: lib/WUI/mdns/mdns.c] [VERIFIED: src/common/metric_handlers.cpp]
- [ ] `tools/bazel/manifests/phase9_network_concern_dispositions.json`: TLS/proxy/transfer/auth/stale-test concern rows. [VERIFIED: .planning/codebase/CONCERNS.md]
- [ ] `tools/bazel/phase9_verify.py` and `tools/bazel/phase9_verify_test.py`: schema, source, redaction, overclaim, Bazel label, lifecycle, and concern-disposition checks. [VERIFIED: tools/bazel/phase8_verify.py]
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, and `justfile`: add Phase 9 verifier/test labels and recipe. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: justfile]
- [ ] `.planning/phases/09-network-web-services-and-transfers/09-VALIDATION.md`: Nyquist validation artifact for requirements and non-local proof classification. [VERIFIED: .planning/config.json]

## Security Domain

### Applicable ASVS Categories

OWASP lists ASVS 5.0.0 as the latest stable version, and ASVS is intended as a basis for web application and technical security-control verification. [CITED: https://owasp.org/www-project-application-security-verification-standard/] The ASVS 5 category map includes authentication, session management, access control, validation/sanitization/encoding, stored cryptography, error handling/logging, data protection, communication, files/resources, API/web service, and configuration categories. [CITED: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/]

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | yes | Preserve WUI digest/API-key auth and Connect token/fingerprint identity; keep credential values redacted. [VERIFIED: lib/WUI/nhttp/req_parser.cpp] [VERIFIED: src/connect/connect.cpp] |
| V3 Session Management | partial | WUI uses digest nonces and idle/active HTTP connection state, not browser sessions; preserve nonce age/stale behavior and server timeouts. [VERIFIED: lib/WUI/nhttp/req_parser.cpp] [VERIFIED: lib/WUI/nhttp/server.cpp] |
| V4 Access Control | yes | Preserve auth-gated WUI API/file/USB handlers and `/usb` path restrictions. [VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp] [VERIFIED: lib/WUI/link_content/usb_files.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api.cpp] |
| V5 Validation, Sanitization and Encoding | yes | Preserve URL decoding, traversal rejection, command-size rejection, and Rust checked constructors for raw values. [VERIFIED: lib/WUI/nhttp/req_parser.cpp] [VERIFIED: src/connect/connect.cpp] [VERIFIED: rust/crates/domain/src/protocol.rs] |
| V6 Stored Cryptography | yes | Do not hand-roll crypto; preserve mbedTLS TLS/AES-CTR use and explicitly disposition MD5/SHA1 module exposure. [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: src/transfers/decrypt.hpp] [VERIFIED: include/mbedtls/cipher_config_ece.h] |
| V7 Error Handling and Logging | yes | Preserve syslog formatting/UDP behavior and avoid logging secrets or raw crash dumps. [VERIFIED: src/logging/log_dest_syslog.cpp] [VERIFIED: src/syslog/syslog_transport.cpp] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] |
| V8 Data Protection | yes | Token/password/certificate evidence must be named-only redacted. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: tools/bazel/phase8_verify.py] |
| V9 Communication | yes | Preserve TLS verification, TLS 1.2 policy, proxy limitations, SNTP/DNS behavior, and non-local proof classification. [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: doc/proxy_support.md] [VERIFIED: lib/WUI/sntp/sntp_client.c] |
| V12 Files and Resources | yes | Preserve static WUI asset serving, USB file operations, transfer storage preconditions, and Phase 7 resource ownership. [VERIFIED: lib/WUI/link_content/static_file.cpp] [VERIFIED: lib/WUI/link_content/usb_files.cpp] [VERIFIED: src/transfers/transfer.cpp] [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| V13 API and Web Service | yes | Preserve PrusaLink API v1 and OctoPrint-compatible endpoint families with auth/error/status behavior. [VERIFIED: lib/WUI/link_content/prusa_link_api_v1.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api_octo.cpp] |
| V14 Configuration | yes | Preserve config-store keys/defaults and reject unsupported feature/service combinations in Rust contracts. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp] [VERIFIED: rust/crates/domain/src/feature.rs] |

### Known Threat Patterns for Phase 9 Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Token/password/certificate leakage through manifests or logs | Information Disclosure | Named-only redaction and verifier rejection for value-bearing secret fields. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md] [VERIFIED: tools/bazel/phase8_verify.py] |
| WUI path traversal or unauthorized USB file access | Tampering / Elevation of Privilege | Preserve URL decoding, traversal checks, `/usb` root restriction, and auth-gated handlers. [VERIFIED: lib/WUI/nhttp/req_parser.cpp] [VERIFIED: lib/WUI/link_content/prusa_link_api.cpp] |
| Duplicate, oversized, or malformed Connect commands | Tampering / Denial of Service | Preserve command ID duplicate rejection, broken-command handling, 512-byte response buffer limitation, and WebSocket command-size checks. [VERIFIED: src/connect/planner.cpp] [VERIFIED: src/connect/connect.cpp] |
| TLS MITM or invalid custom certificate behavior | Spoofing / Information Disclosure | Preserve required certificate verification and disposition custom DER handling with fixtures if fixed. [VERIFIED: src/connect/tls/tls.cpp] |
| Proxy traffic assumptions | Information Disclosure | Document minimal proxy limitations: no proxy auth, printer-to-proxy leg unencrypted, proxy active only with TLS. [VERIFIED: doc/proxy_support.md] |
| Transfer corruption or media race | Tampering / Denial of Service | Preserve single-slot monitor, recovery backup CRC/version checks, range handling, direct-sector evidence classification, and non-local media race proof. [VERIFIED: src/transfers/monitor.hpp] [VERIFIED: src/transfers/transfer_recovery.cpp] [VERIFIED: src/transfers/partial_file.cpp] |
| mDNS resource exhaustion | Denial of Service | Preserve one-active-interface mDNS behavior and LwIP timeout/packet limits. [VERIFIED: lib/WUI/wui.cpp] [VERIFIED: include/buddy/lwipopts.h] |
| Metrics/syslog UDP loss or stack deadlock | Denial of Service / Repudiation | Preserve best-effort UDP transport, message pool limits, and syslog guard that avoids logging from inside LwIP core lock. [VERIFIED: src/syslog/syslog_transport.cpp] [VERIFIED: src/logging/log_dest_syslog.cpp] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md` - locked decisions, discretion, deferred scope, manifest suggestions, lifecycle ID. [VERIFIED]
- `.planning/REQUIREMENTS.md` - IFCE-02 and IFCE-03 requirement text and traceability. [VERIFIED]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and pinned Bright Builds standards - project constraints and coding/verification rules. [VERIFIED] [CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/index.md]
- `src/connect/`, `src/connect/tls/`, `src/common/http/`, `src/transfers/`, `lib/WUI/`, `src/common/metric*`, `src/logging/log_dest_syslog.cpp`, `src/syslog/syslog_transport.cpp` - reference implementation source. [VERIFIED]
- `rust/crates/domain/src/`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, and `justfile` - established Rust/Bazel/just verifier patterns. [VERIFIED]
- `tests/unit/connect/`, `tests/unit/transfers/`, `tests/unit/lib/WUI/nhttp/`, and `tests/module/Connect/` - available and stale test surfaces. [VERIFIED]
- Vendored version headers for mbedTLS, LwIP, FreeRTOS, and Catch2. [VERIFIED]

### Secondary (MEDIUM confidence)

- OWASP ASVS official project page and OWASP Developer Guide category summary for current security category mapping. [CITED: https://owasp.org/www-project-application-security-verification-standard/] [CITED: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/]

### Tertiary (LOW confidence)

- None. No unverified web-only findings were used. [VERIFIED: research source log]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - verified from local source, vendored headers, and installed CLI versions. [VERIFIED: environment audit] [VERIFIED: vendored headers]
- Architecture: HIGH - follows existing Phase 4-8 patterns and locked Phase 9 context. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md]
- Pitfalls: HIGH - each pitfall maps to source code, codebase concerns, or locked context. [VERIFIED: .planning/codebase/CONCERNS.md] [VERIFIED: src/connect/tls/tls.cpp] [VERIFIED: src/transfers/partial_file.cpp]
- Security: MEDIUM - ASVS mapping is current and cited, but firmware-specific applicability is an engineering classification rather than a formal certification. [CITED: https://owasp.org/www-project-application-security-verification-standard/] [VERIFIED: source audit]

**Research date:** 2026-06-14  
**Valid until:** 2026-07-14 for repo-local planning facts; re-check OWASP/security and local tool versions after 30 days. [CITED: https://owasp.org/www-project-application-security-verification-standard/] [VERIFIED: environment audit]
