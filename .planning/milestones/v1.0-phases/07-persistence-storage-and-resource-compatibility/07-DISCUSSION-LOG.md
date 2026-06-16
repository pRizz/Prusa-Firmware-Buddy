# Phase 7: Persistence, Storage, and Resource Compatibility - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-06T04:25:41.416Z
**Phase:** 07-persistence-storage-and-resource-compatibility
**Mode:** Yolo
**Areas discussed:** Persistence and config schema compatibility, Filesystem and storage media compatibility, Resources/translations/generated assets, Known concerns and intentional deltas, Verification and lifecycle

---

## Persistence and config schema compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Source-backed manifests and typed Rust contracts | Derive compatibility rows from config-store definitions, defaults, migrations, old EEPROM schemas, journal hashes, and storage drivers. | ✓ |
| Freehand rewrite of config models | Recreate storage/config concepts directly in Rust without explicit source path traceability. | |
| Defer config modeling to later phases | Only document persistence paths now and postpone typed contracts. | |

**User's choice:** Auto-selected source-backed manifests and typed Rust contracts.
**Notes:** Recommended because IFCE-04 is compatibility-sensitive and prior phases require behavior parity, source-backed contracts, and illegal-state modeling.

---

## Filesystem and storage media compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Model named mount/media surfaces with evidence classes | Represent `/usb`, `/internal`, BBF/resource littlefs, optional `/semihosting`, EEPROM, journal, and root listing contracts locally while classifying hardware proof as non-local. | ✓ |
| Claim local filesystem parity from static checks | Treat source-path coverage as sufficient proof of actual media behavior. | |
| Skip filesystem surfaces until cutover | Leave media compatibility unmodeled until Phase 11. | |

**User's choice:** Auto-selected named mount/media surfaces with evidence classes.
**Notes:** Recommended because Phase 7 must make storage compatibility inspectable without overclaiming hardware/media proof.

---

## Resources, translations, and generated assets

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve existing generator ownership with Bazel/just drift checks | Keep current tracked/generated resource assets tied to CMake/Python/source inputs and expose Bazel check/update labels. | ✓ |
| Hand-edit generated artifacts for parity | Modify tracked generated outputs directly to satisfy local checks. | |
| Rewrite generators during Phase 7 | Replace translation/font/resource generation wholesale now. | |

**User's choice:** Auto-selected existing generator ownership with Bazel/just drift checks.
**Notes:** Recommended because Phase 3 already established generator ownership and Phase 7 should extend it for storage/resource compatibility, not re-litigate it.

---

## Known concerns and intentional deltas

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit concern dispositions with no secret values | Track generated drift, shell safety, credential storage, hash collisions, and block-device concerns as preserved behavior, intentional deltas, or deferred work. | ✓ |
| Opportunistically fix concerns without delta records | Improve fragile areas silently as implementation proceeds. | |
| Ignore known concerns in Phase 7 | Treat concerns as later audit-only material. | |

**User's choice:** Auto-selected explicit concern dispositions with no secret values.
**Notes:** Recommended because Phase 1 and Phase 6 already require known defects and fragile areas to be tied to fixtures or intentional-delta evidence.

---

## Verification and lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 7 verifier with regression tests, Bazel/just wiring, and lifecycle metadata | Add a repo-owned verifier that checks manifests, Rust API shape, redaction, source coverage, target wiring, and lifecycle consistency. | ✓ |
| Manual-only review of artifacts | Rely on human inspection of manifests and docs. | |
| Reuse Phase 6 verifier for Phase 7 | Add storage/resource checks into the prior phase verifier. | |

**User's choice:** Auto-selected Phase 7 verifier with regression tests, Bazel/just wiring, and lifecycle metadata.
**Notes:** Recommended because Phase 4-6 established a repeatable local verifier pattern and the wrapper can only push after clean verification.

---

## the agent's Discretion

- Exact manifest file names, schema field ordering, and plan splits are left to the planner/executor as long as source traceability, credential redaction, local/non-local evidence classification, and lifecycle metadata remain enforceable.

## Deferred Ideas

- Runtime GUI persisted-setting flows, Connect/WUI API behavior, auxiliary-controller resource runtime parity, full simulator/hardware media proof, and cutover evidence remain later-phase work.
