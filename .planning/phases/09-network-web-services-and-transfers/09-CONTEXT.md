---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 9-2026-06-14T02-15-21
generated_at: 2026-06-14T02:17:00.942Z
---

# Phase 9: Network, Web Services, and Transfers - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 9 preserves network-facing behavior for the Rust+Bazel firmware. The scope is Prusa Connect registration, token/fingerprint identity, telemetry, events, WebSocket commands, TLS verification, proxy behavior, transfer/download integration, PrusaLink/WUI HTTP API v1, OctoPrint-compatible endpoints, digest/API-key auth, static web assets, SNTP, mDNS, metrics, and syslog. New network features, redesigned transfer concurrency, broader proxy/TLS capabilities, and final cutover proof belong to later phases unless they are explicitly documented as intentional deltas with parity evidence.

</domain>

<decisions>
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and phase scope

- `.planning/PROJECT.md` - Rust+Bazel rewrite constraints, validated prior phase outcomes, and Phase 9 focus.
- `.planning/REQUIREMENTS.md` - IFCE-02 and IFCE-03 requirements plus verification and cutover boundaries.
- `.planning/ROADMAP.md` - Phase 9 goal, dependencies, and success criteria.
- `.planning/STATE.md` - Current milestone state and active Phase 09 focus.

### Prior phase contracts

- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md` - retained foreign-code, unsafe, runtime, and FreeRTOS boundary decisions.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md` - printing/safety/feature-gate parity and non-local hardware evidence language.
- `.planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md` - credential redaction, storage/media, WUI asset, and resource compatibility decisions.
- `.planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md` - GUI Connect-entry, PrusaLink credential display, localization, and non-local UI evidence decisions.

### Codebase maps and concerns

- `.planning/codebase/INTEGRATIONS.md` - Connect, PrusaLink/WUI, downloads, SNTP, mDNS, metrics, syslog, auth, TLS, proxy, and runtime configuration map.
- `.planning/codebase/CONCERNS.md` - known network/TLS/transfer/security/test gaps that Phase 9 must disposition.
- `.planning/codebase/TESTING.md` - available unit, simulator, stale Connect module, and integration-test surfaces.
- `.planning/codebase/ARCHITECTURE.md` - source-layer integration points for Connect, WUI, transfers, state, syslog, and persistent stores.
- `.planning/codebase/CONVENTIONS.md` - naming, formatting, generated-file, logging, and test conventions.

### Network and service docs

- `doc/proxy_support.md` - current Connect proxy behavior and limitations.
- `doc/prusa_printer_settings.ini` - settings import/export key names for network, Wi-Fi, Connect, TLS, and proxy configuration. Treat sample secrets as examples only; do not copy credential values into artifacts.
- `doc/metrics.md` - metrics configuration, metric definitions, throttling, line-protocol-compatible payload shape, and development collector expectations.
- `src/common/http/README.md` - HTTP utility scope.
- `lib/WUI/nhttp/README.md` - embedded HTTP server design, resource model, parser/handler structure, limits, and current problems.

### Source reference surfaces

- `src/connect/` - Prusa Connect client, registration, command, planner, status, rendering, host, and printer abstraction behavior.
- `src/connect/tls/` - TLS, certificate, hardware RNG, and socket glue.
- `src/common/http/` - HTTP client, proxy, WebSocket, parser, socket, and request helpers.
- `src/transfers/` - download, transfer monitor, partial-file, recovery, changed-path, decryption, and file checks.
- `lib/WUI/` - local web service lifetime, WUI API, network device setup, SNTP, mDNS, PrusaLink API, OctoPrint API, static file, upload, and nhttp server surfaces.
- `src/common/metric.cpp`, `src/common/metric_handlers.cpp`, `src/logging/log_dest_syslog.cpp`, and `src/syslog/syslog_transport.cpp` - metrics and syslog behavior.
- `src/persistent_stores/store_instances/config_store/store_definition.hpp` and `defaults.hpp` - network, PrusaLink, Connect, metrics, syslog, TLS, proxy, and credential-bearing config fields.
- `rust/crates/domain/src/protocol.rs`, `feature.rs`, and `resource.rs` - existing Rust domain style for Connect endpoint, registration, WUI/Connect feature flags, and WUI static asset paths.
- `tests/unit/connect/`, `tests/unit/transfers/`, and `tests/unit/lib/WUI/` - available host unit-test surfaces and stubs.
- `tests/integration/` and `tests/module/Connect/` - simulator integration and stale manual Connect test material.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `rust/crates/domain/src/protocol.rs`: existing `RegistrationCode`, `ConnectEndpoint`, and connection state-machine style can be extended for Phase 9 protocol contracts.
- `rust/crates/domain/src/feature.rs`: existing `Feature::WebUi` and `Feature::Connect` gates provide a natural anchor for product/feature-gated network surfaces.
- `rust/crates/domain/src/resource.rs`: existing `ResourceSurface::WuiStaticAssets` and path parsing patterns should carry forward for static WUI asset contracts.
- `tools/bazel/phase5_verify.py`, `phase6_verify.py`, `phase7_verify.py`, and `phase8_verify.py`: prior phase verifier pattern for manifest coverage, Rust API shape, Bazel labels, lifecycle metadata, and overclaim guards.
- `tests/unit/connect/`, `tests/unit/transfers/`, and `tests/unit/lib/WUI/nhttp/`: host-test stubs and fixture style for Connect planner, registration/rendering, transfer state, nhttp request parsing, server behavior, and transfer renderers.

### Established Patterns

- Prior phases use source-backed manifests plus pure Rust domain contracts before claiming adapter/runtime parity.
- Local verification proves deterministic artifacts, schema/API shape, unit-test behavior, and source traceability; simulator, physical hardware, live cloud, media race, and long-running network proof are classified as non-local evidence.
- Secret-bearing fields are named by config key or path only. Values, certificate bytes, tokens, passwords, private keys, and raw crash dump contents are excluded from manifests and commits.
- Known reference defects are either preserved temporarily or fixed as named intentional deltas with requirement mapping and regression evidence.

### Integration Points

- Connect starts through `src/connect/run.cpp`, delegates printer operations through `src/connect/printer.hpp` and `marlin_printer.*`, and shares transfer/download behavior through `src/transfers/`.
- PrusaLink/WUI starts through `lib/WUI/http_lifetime.cpp` and routes requests through `lib/WUI/nhttp/server.cpp` plus `lib/WUI/link_content/`.
- TLS and proxy behavior connects `src/connect/tls/`, `src/common/http/proxy.*`, and config-store network settings.
- Transfer behavior connects Connect commands, WUI/PrusaLink endpoints, filesystem/media compatibility from Phase 7, and GUI transfer/error surfaces from Phase 8.
- Metrics/syslog/discovery connect `src/common/metric*`, `src/logging`, `src/syslog`, `lib/WUI/sntp/`, `lib/WUI/mdns/`, and LwIP option/config surfaces.

</code_context>

<specifics>
## Specific Ideas

- Use a `phase9_connect_contracts.json` manifest for Connect registration, token/fingerprint headers, telemetry/events, command/WebSocket flows, host/proxy/TLS config, connection reuse, and known limitations.
- Use a `phase9_wui_contracts.json` manifest for PrusaLink API v1, OctoPrint-compatible endpoints, static web UI, digest/API-key auth, server resource limits, parser/handler behavior, and generated automata dependencies.
- Use a `phase9_transfer_contracts.json` manifest for transfer slot state, sources, range/encryption metadata, recovery, partial-file/media evidence, and error classifications.
- Use a `phase9_network_concern_dispositions.json` manifest for custom DER certificate loading, weak digest module exposure, proxy limitations, stale Connect module tests, whole-response buffers, transfer media races, lock-order deadlocks, single active transfer, and network/TLS coverage gaps.
- Add pure Rust domain contracts such as `ConnectIdentity`, `ConnectCommandState`, `TlsEvidenceClass`, `ProxyMode`, `WuiEndpoint`, `WuiAuthMode`, `TransferSlotState`, `TransferEvidenceClass`, and `NetworkServiceSurface` if those names fit the existing `buddy-domain` style.
- Add an overclaim guard that rejects local-pass wording for live Connect cloud integration, physical Wi-Fi/Ethernet behavior, live TLS handshakes, USB/media race behavior, long-running transfers, simulator network flows, and cutover evidence unless the artifact records the correct non-local evidence class.

</specifics>

<deferred>
## Deferred Ideas

- Broader proxy authentication, MITM support, or TLS policy expansion beyond the current reference behavior belongs to v2 unless approved as an intentional delta.
- Transfer concurrency redesign beyond the single active slot belongs to v2.
- Full byte-for-byte release, live cloud, hardware network, media race, and cutover proof belongs to Phase 11.
- Auxiliary-controller, MMU, toolchanger, and puppy network/update behavior beyond the transfer integration boundary belongs to Phase 10.

</deferred>

---

*Phase: 09-network-web-services-and-transfers*
*Context gathered: 2026-06-14*
