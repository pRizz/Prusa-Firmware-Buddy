---
status: partial
phase: 16-live-network-and-transfer-qualification
source: [16-VERIFICATION.md]
started: 2026-06-18T02:59:18Z
updated: 2026-06-18T02:59:18Z
---

# Phase 16 Human UAT

## Current Test

Awaiting human testing.

## Tests

### 1. Approved Connect Or Controlled-Service Run

expected: Supply redacted operator evidence JSON for Connect registration, telemetry, WebSocket commands, token/fingerprint behavior, proxy limitations, TLS, and transfer rows. The verifier accepts complete live/control-service evidence, writes guarded artifacts, and moves only supplied rows from `pending-live-input` to the supplied valid status.
result: pending

### 2. PrusaLink/WUI Controlled Endpoint With Auth

expected: Supply operator evidence for WUI API, digest auth, API-key auth, SNTP, mDNS, syslog, metrics, and WUI upload transfer rows. Evidence validates with guarded artifact refs and redacted summaries; no passwords, API keys, digest responses, cookies, or raw payloads are retained.
result: pending

### 3. TLS/Certificate And Crash-Dump Evidence

expected: Supply fixture names, hashes, redacted outcomes, and external artifact refs for TLS/custom CA and crash-dump upload evidence. Private certs/keys, raw crash dumps, raw HTTP/TLS logs, and production payloads are rejected; secret-safe evidence is retained.
result: pending

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
