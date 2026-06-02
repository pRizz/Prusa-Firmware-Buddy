# Phase 3: Artifact and Generator Parity - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-02T21:04:24.009Z
**Phase:** 3 - Artifact and Generator Parity
**Mode:** Yolo
**Areas discussed:** Release artifact surface, Generator ownership, Deterministic drift checks, Reference comparison boundary

---

## Release Artifact Surface

| Option | Description | Selected |
|--------|-------------|----------|
| Master firmware package tranche | Bring `.bin`, `.map`, provenance, `.bbf`, `.dfu`, boot/noboot, and resource package outputs under Bazel first. Keep ESP/puppy/MMU/auxiliary outputs as declared inputs/manifests until later runtime parity phases. | yes |
| Generator/resource tranche first | Make product profiles, option data, LittleFS resources, translations, fonts, WUI assets, ESP blobs, and descriptors deterministic before broad packaging. | |
| Full release matrix package surface | Cover master and auxiliary firmware packages, boot/noboot, DFU, BBF, resources, ESP blobs, descriptors, and metadata together. | |

**User's choice:** Auto-selected recommended yolo default: master firmware package tranche.
**Notes:** This unlocks artifact comparison without claiming full firmware/runtime parity. Signing flow and full matrix coverage must be explicit and non-secret.

---

## Generator Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Reference-wrapper status quo | Preserve current CMake/Python behavior and leave Bazel mostly as a launcher. | |
| Tiered Bazel ownership | Move build-critical generated outputs into declared Bazel actions; keep reviewable tracked generated files checked in with Bazel drift/update checks. | yes |
| Full Bazel generator migration | Retire CMake generator authority now and model all generators directly in Bazel/Starlark. | |
| Output-tree-only generated files | Remove source-tree generated outputs and keep all derived files under Bazel output directories. | |

**User's choice:** Auto-selected recommended yolo default: tiered Bazel ownership.
**Notes:** This matches the current mixed source tree while still making Phase 3 materially stronger than Phase 2's reference wrappers.

---

## Deterministic Drift Checks

| Option | Description | Selected |
|--------|-------------|----------|
| Local Bazel golden-diff checks | Use Bazel tests with declared data deps to compare normalized generated outputs against checked references. | yes |
| Normalized release-metadata manifest checks | Validate filenames, products, boards, MCUs, artifact types, tool versions, and package schema without full local firmware builds. | yes |
| Tiered local + CI artifact parity | Keep local checks fast and move checksum/full-matrix/simulator/hardware evidence to explicit CI/manual gates. | yes |
| Full local artifact rebuild comparison | Rebuild and compare full artifacts locally as the default. | |

**User's choice:** Auto-selected recommended yolo default: combine local Bazel golden diffs, normalized metadata manifests, and explicit CI/manual parity tiers.
**Notes:** Local checks should be read-only, deterministic, and proportionate. Full firmware checksums, simulator flows, hardware evidence, and signing-sensitive release checks remain explicit heavier gates.

---

## Reference Comparison Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen Phase 1 reference fixtures + Bazel conformance tests | Compare against checked baseline artifacts and manifests without invoking live CMake in the default path. | yes |
| Manual/CI-only live CMake reference comparison | Run live CMake/Python reference comparison only as a quarantined reference check. | yes |
| Semantic artifact manifest comparison | Validate release metadata and package structure without claiming byte-level firmware parity. | yes |
| Strict byte-for-byte diff with diagnostic reports | Use exact diffs where deterministic byte identity is the actual contract. | yes |

**User's choice:** Auto-selected recommended yolo default: layered comparison boundary.
**Notes:** Bazel owns artifact production and tests; CMake remains reference-only. Semantic manifests are the default release artifact boundary, while strict byte diffs are reserved for deterministic generated outputs and packaging diagnostics.

---

## the agent's Discretion

- Exact Bazel labels, helper script names, manifest schema, representative product set, fixture layout, and verification command shape.
- Whether small helper logic lives in standard-library Python, shell wrappers, or Starlark, as long as the chosen surface is deterministic and easy to verify.

## Deferred Ideas

None - discussion stayed within phase scope.
