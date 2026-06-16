# Phase 9: Network, Web Services, and Transfers - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-14T02:17:00.942Z
**Phase:** 9-Network, Web Services, and Transfers
**Mode:** Yolo
**Areas discussed:** Prusa Connect cloud behavior, PrusaLink and WUI local services, Transfer and download semantics, TLS/proxy/certificates/security, Telemetry/discovery/metrics/syslog, Verification and lifecycle

---

## Prusa Connect cloud behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve reference contracts | Model current Connect registration, telemetry, events, WebSocket commands, headers, config, connection reuse, and limitations as source-backed parity contracts. | yes |
| Fix broad behavior now | Redesign command buffering, streaming parse behavior, proxy support, and response handling in one pass. | |
| Leave to later cutover | Defer Connect details until Phase 11. | |

**User's choice:** Yolo selected preserve reference contracts.
**Notes:** This keeps IFCE-02 focused on behavior parity while allowing named intentional deltas for known bugs when regression evidence exists.

---

## PrusaLink and WUI local services

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve embedded server model | Keep streaming parser, limited active connections, shared buffers, generated automata, local auth, static assets, and endpoint families as explicit contracts. | yes |
| Replace with generic HTTP design | Use a broader web-server abstraction that may not match embedded resource constraints. | |
| Static assets only | Track WUI resources but skip API, auth, and handler parity. | |

**User's choice:** Yolo selected preserve embedded server model.
**Notes:** Phase 9 should reflect `lib/WUI/nhttp/README.md` and route/API behavior rather than normalizing it into a desktop/server web stack.

---

## Transfer and download semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve single-slot semantics | Treat Connect, WUI, HTTP download, range/encryption, partial-file, recovery, and storage integration as one source-backed parity surface. | yes |
| Redesign concurrency | Add multi-transfer support or broader storage redesign now. | |
| Cover only Connect downloads | Skip PrusaLink/WUI transfer endpoints and media edge cases. | |

**User's choice:** Yolo selected preserve single-slot semantics.
**Notes:** Transfer concurrency redesign is deferred. Local verification should be honest about media race and long-running network evidence.

---

## TLS, Proxy, Certificates, And Security

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve policy and disposition risks | Keep current TLS/proxy policy as reference, explicitly classify known defects and security-sensitive surfaces, and fix only with named intentional-delta evidence. | yes |
| Strengthen all TLS/proxy behavior now | Expand proxy auth, certificate policy, and diagnostics beyond reference behavior. | |
| Ignore custom certificate path | Leave DER loading and weak digest concerns out of Phase 9. | |

**User's choice:** Yolo selected preserve policy and disposition risks.
**Notes:** The custom DER read bug may be fixed if planned narrowly with tests; otherwise it must stay visible as a known reference defect.

---

## Telemetry, Discovery, Metrics, And Syslog

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve local service surfaces | Track SNTP, mDNS, DNS, metrics, syslog, runtime config, and default behavior as source-backed contracts. | yes |
| Treat as observability-only | Cover metrics/syslog but skip SNTP, mDNS, and DNS/service startup behavior. | |
| Defer all service behavior | Leave non-Connect services to final cutover. | |

**User's choice:** Yolo selected preserve local service surfaces.
**Notes:** These surfaces belong to IFCE-03 and should be feature/product gated with local-vs-non-local evidence classifications.

---

## Verification And Lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Follow Phase 4-8 verifier pattern | Add manifests, Rust domain contracts, Bazel/just labels, verifier tests, lifecycle checks, and overclaim guards. | yes |
| Use documentation only | Write the context and rely on later phases for verification. | |
| Run heavy integration locally | Attempt live cloud, full firmware, simulator network, and hardware/media proof in routine local verification. | |

**User's choice:** Yolo selected follow Phase 4-8 verifier pattern.
**Notes:** Heavy proof remains non-local unless a specific plan adds a controlled local fixture or simulator path.

---

## the agent's Discretion

- Exact manifest names, Rust type names, verifier helper structure, and plan slicing are delegated to planning and execution.
- Fixture granularity is flexible as long as one fixture proves one compatibility concern and secrets remain redacted.

## Deferred Ideas

- Broader proxy authentication or TLS policy expansion beyond reference behavior.
- Multi-transfer concurrency redesign.
- Full live cloud, hardware network/media, simulator network, release, and cutover proof.
- Auxiliary-controller/MMU/toolchanger network and update behavior outside the Phase 9 transfer integration boundary.
