# Phase 07: Persistence, Storage, and Resource Compatibility - Research

**Researched:** 2026-06-06
**Domain:** Embedded firmware persistence, filesystem, generated-resource, Rust domain-contract, and Bazel verifier compatibility
**Confidence:** HIGH for source-backed architecture and verifier shape; MEDIUM for local generator execution because this workstation is not fully bootstrapped

<user_constraints>
## User Constraints (from CONTEXT.md)

Copied verbatim from `.planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md`. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

### Locked Decisions

### Persistence and config schema compatibility
- **D-01:** Treat the current C++ persistent store, old EEPROM schemas, defaults, migrations, journal backend, and generated journal hashes as the Phase 7 reference oracle. Rust behavior is accepted only when tied to exact source paths, manifests, or fixtures.
- **D-02:** Build explicit Phase 7 manifests for config-store items, defaults, deprecated/old EEPROM IDs, migration windows, credential-bearing keys, journal hash evidence, and storage drivers. Every manifest row should name the retained source path, Rust surface, requirement ID, evidence class, and whether proof is local or non-local.
- **D-03:** Extend the existing `buddy-domain` storage model instead of replacing it with primitive strings. New pure Rust types should model storage keys, schema versions, migration windows, journal/hash facts, credential redaction policy, and fixture identities with fallible constructors.
- **D-04:** Preserve deprecated item IDs and migration behavior as compatibility contracts. A config item rename, removal, or hash change is only allowed as an intentional delta with migration evidence and generated hash drift coverage.
- **D-05:** Do not put credential values, passwords, tokens, certificates, EEPROM bytes, or private signing material into manifests, fixtures, logs, or commits. Phase 7 may name credential-bearing keys and paths, but secret value handling stays redacted. The current lack of visible encryption-at-rest is a known reference fact, not a Phase 7 local fix unless later approved as an intentional delta.

### Filesystem and storage media compatibility
- **D-06:** Model `/usb` FatFs, `/internal` littlefs, BBF/resource littlefs, optional `/semihosting`, root device listing, EEPROM/storage drivers, POSIX-like libsysbase behavior, and resource bootstrap paths as named compatibility surfaces.
- **D-07:** Local verification can prove manifest coverage, Rust state/contract behavior, source-path traceability, and fixture classification. Actual USB media behavior, flash wear behavior, filesystem mount timing, crash-dump persistence, and printer hardware storage proof must stay classified as `simulator-flow`, `hardware-smoke`, or `manual-hardware-required`.

### Resources, translations, and generated assets
- **D-08:** Keep generated resource, translation, font, icon, WUI, ESP, bootloader, MMU, and language-pack surfaces tied to the existing CMake/Python/source asset pipeline. Bazel should expose check/update labels and manifests without silently hand-editing generated outputs.
- **D-09:** Treat tracked generated outputs and generated-at-build outputs separately. Tracked outputs remain reviewed source artifacts when the repo already tracks them; Bazel/just checks should detect drift and named update targets may call existing generators.
- **D-10:** Resource package parity should compare semantic content, declared inputs, generated hashes/revisions, file names, and required runtime visibility. Do not claim full release artifact or byte-for-byte firmware parity from Phase 7 unless the plan creates a narrow, normalized fixture.

### Known concerns and intentional deltas
- **D-11:** Phase 7 must explicitly disposition known concerns related to generated-file drift, unsafe translation/font shell scripts, unencrypted credential storage, config-schema migration/hash fragility, journal hash space limits, block-device test randomness, dependency drift affecting `littlefs-python`, and tracked generated font/header churn.
- **D-12:** If the Rust rewrite fixes one of these reference concerns during Phase 7, the fix must be named as an intentional delta with requirement mapping and regression evidence. Otherwise, preserve the reference behavior and document the risk for later cutover review.

### Verification and lifecycle
- **D-13:** Add a repo-owned Phase 7 verifier exposed through Bazel and `just`, following the Phase 4-6 pattern. It should check required manifests, Rust API shape, unsafe-free pure domain modules, source-path coverage, credential redaction, generated/drift target wiring, concern dispositions, and lifecycle metadata.
- **D-14:** Relevant local verification should include Rust formatting/lint/build/tests, Phase 7 verifier regression tests, `just phase7-verify`, Bazel queryability for new labels, and schema/lifecycle validation. Heavy firmware builds, full generator runs, simulator flows, and hardware media checks may be recorded as explicit non-local evidence.
- **D-15:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 7-2026-06-06T04-24-25`.

### the agent's Discretion
- Exact manifest names and schema field order are flexible if they remain source-backed, reviewable, and covered by verifier tests.
- The planner may split Phase 7 into focused plans by config/journal, filesystem/media, resources/generators, Rust domain contracts, and aggregate verification.
- Fixture granularity is flexible, but each fixture must prove one compatibility concern and avoid embedding secret values.

### Deferred Ideas (OUT OF SCOPE)
- Runtime GUI display of persisted settings and localization flows belongs to Phase 8 unless Phase 7 needs a narrow storage/resource fixture.
- Connect/WUI API behavior, token use over the network, TLS custom certificate parsing, and HTTP static asset serving behavior belong to Phase 9.
- Auxiliary-controller update/runtime parity, puppy/MMU toolchanger resources in motion, and Modbus behavior belong to Phase 10.
- Full parity pyramid, hardware media smoke, simulator flows, and release-candidate cutover evidence belong to Phase 11.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IFCE-04 | Rust firmware preserves persistent config, schema migrations, defaults, deprecated item IDs, credentials, settings import/export, EEPROM/internal flash behavior, FatFs/littlefs mounts, USB/internal/semihosting paths, and config hash/journal behavior. [VERIFIED: .planning/REQUIREMENTS.md] | Plan config/journal, filesystem/media, credential-redaction, and storage-fixture manifests tied to `src/persistent_stores/`, `src/buddy/filesystem*.cpp`, `lib/libsysbase/`, and `tests/unit/persistent_stores/`. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/persistent_stores/journal/backend.cpp; VERIFIED: src/buddy/filesystem.cpp; VERIFIED: tests/unit/persistent_stores/CMakeLists.txt] |
| IFCE-05 | Rust firmware preserves resources, translations, fonts, icons, littlefs images, bootloader resources, ESP blobs, WUI assets, language packs, and generated headers visible to runtime or release artifacts. [VERIFIED: .planning/REQUIREMENTS.md] | Plan resource/generator manifests tied to `src/resources/CMakeLists.txt`, `cmake/Littlefs.cmake`, `utils/mklittlefs.py`, `src/lang/CMakeLists.txt`, `utils/translations_and_fonts/`, and Phase 3 generated-drift labels. [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: cmake/Littlefs.cmake; VERIFIED: utils/mklittlefs.py; VERIFIED: src/lang/CMakeLists.txt; VERIFIED: tools/bazel/generated_drift.py] |
</phase_requirements>

## Summary

Phase 7 should be planned as compatibility-contract work, not as a rewrite of EEPROM, FatFs, littlefs, gettext, BBF packaging, or generator internals. The current C++ config store, old EEPROM schemas, journal backend, filesystem devoptabs, resource bootstrap path, and CMake/Python resource pipeline are the reference oracle, while Rust should add typed domain contracts and Bazel/just should add source-backed manifests and verifier checks. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/persistent_stores/journal/backend.cpp; VERIFIED: src/buddy/filesystem.cpp; VERIFIED: src/resources/CMakeLists.txt]

The highest-risk planning detail is preserving identity across names, hashes, and files. Config items use `journal::hash("...")` names, including credential-bearing names with spaces such as `WIFI AP Password`, while the existing Rust `StorageKey` only accepts ASCII alphanumeric plus `_`, `-`, and `.` and rejects whitespace, so Phase 7 needs separate Rust types for raw reference hash names and Rust-safe manifest identifiers. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: rust/crates/domain/src/storage.rs]

The default local gate should be static and deterministic: validate JSON manifests, source paths, Rust API strings, no unsafe in pure Rust storage/resource modules, lifecycle metadata, redaction, and Bazel/just wiring. Full generator execution, physical media, flash wear, filesystem timing, simulator flows, and hardware storage proof should be explicit non-local evidence unless the plan creates a narrow normalized fixture. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: tools/bazel/generated_drift.py]

**Primary recommendation:** create Phase 7 manifests plus `buddy-domain` storage/resource extensions first, then add `tools/bazel/phase7_verify.py`, verifier tests, Bazel labels, and `just phase7-verify` to enforce IFCE-04/IFCE-05 without running unbootstrapped heavy generators by default. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

## Project Constraints (from AGENTS.md)

- Read `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant canonical Bright Builds standards before planning, implementation, review, or audit work. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards-overrides.md]
- Treat the Rust port as a Big Bang replacement with behavior parity for supported printers, release artifacts, generated assets, tests, network behavior, persistent config, and safety-critical behavior unless explicitly descoped. [VERIFIED: AGENTS.md; VERIFIED: .planning/PROJECT.md]
- Bazel is authoritative from the start and `justfile` wrappers are required for common workflows. [VERIFIED: AGENTS.md; VERIFIED: .planning/PROJECT.md; VERIFIED: justfile]
- Bright Builds architecture, code-shape, verification, testing, and Rust module guidance applies because `standards-overrides.md` contains no active local override. [VERIFIED: standards-overrides.md; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/core/architecture.md; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/languages/rust.md]
- New Rust domain code should parse raw data at boundaries, use fallible constructors/newtypes/enums, keep pure logic out of adapters, and forbid unsafe in pure domain modules. [VERIFIED: Cargo.toml; VERIFIED: rust/crates/domain/src/lib.rs; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/core/architecture.md; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/languages/rust.md]
- Repo-owned verification must run through the repo entrypoints and should include relevant format, lint, build, tests, and diff review before completion; this research does not commit because the user explicitly requested no commit/push. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: user prompt]
- Do not store credential values, private signing key material, EEPROM bytes, certificates, tokens, or password values in Phase 7 artifacts. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/INTEGRATIONS.md]

## Standard Stack

### Core

| Library/Surface | Version | Purpose | Why Standard |
|-----------------|---------|---------|--------------|
| `buddy-domain` | `0.1.0`, Rust edition 2024, workspace rust-version 1.85 | Pure Rust storage/resource/config artifact contracts. | It is already the project-owned functional core and has existing storage/artifact invariant seeds. [VERIFIED: rust/crates/domain/Cargo.toml; VERIFIED: Cargo.toml; VERIFIED: rust/crates/domain/src/storage.rs; VERIFIED: rust/crates/domain/src/artifact.rs] |
| C++ persistent store oracle | local source | Current config item/default/deprecated-ID/migration behavior. | Phase 7 decisions lock this as the oracle; `CurrentStore::newest_config_version` is 5 and deprecated items must keep hashed IDs. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp] |
| Journal backend and hash generator | local source | Append-only transactions, CRC/bank validation, migration reads, and generated 14-bit journal IDs. | Existing tests and generator logic cover the reference storage protocol and duplicate detection. [VERIFIED: src/persistent_stores/journal/backend.cpp; VERIFIED: src/persistent_stores/journal/store.hpp; VERIFIED: utils/persistent_stores/journal_hashes_generator.py; VERIFIED: tests/unit/persistent_stores/CMakeLists.txt] |
| FatFs, littlefs, libsysbase devoptabs | local in-repo dependencies | `/usb`, `/internal`, `/bbf`, `/semihosting`, and root filesystem compatibility. | These surfaces are retained foreign-code boundaries and Phase 7 owns storage/resource adapter contracts. [VERIFIED: tools/bazel/manifests/foreign_code_inventory.json; VERIFIED: src/buddy/filesystem_fatfs.cpp; VERIFIED: src/buddy/filesystem_littlefs_internal.cpp; VERIFIED: src/buddy/filesystem_littlefs_bbf.cpp; VERIFIED: src/buddy/filesystem_semihosting.cpp; VERIFIED: lib/libsysbase/iosupport.c] |
| Existing CMake/Python resource pipeline | local source | LittleFS images, resource hashes, WUI assets, ESP blobs, bootloader resources, MMU resources, translations, fonts, and generated headers. | Phase 7 must expose Bazel/just check/update contracts while retaining the existing generator pipeline as the oracle. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: cmake/Littlefs.cmake; VERIFIED: src/lang/CMakeLists.txt; VERIFIED: utils/translations_and_fonts/lang.py] |
| Bazel shell targets plus `justfile` | Bazel 9.1.1 local, just 1.48.0 local | Phase verifier execution and developer facade. | Phase 4-6 use this pattern, and Phase 7 decisions require the same Bazel/just exposure. [VERIFIED: local command `bazel --version`; VERIFIED: local command `just --version`; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile] |

### Supporting

| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| `littlefs-python` | `0.8` pinned | `utils/mklittlefs.py` image creation, file insertion, and content-hash calculation. | Use for generator/reference runs after bootstrap; host Python in this session cannot import it. [VERIFIED: requirements.txt; VERIFIED: utils/mklittlefs.py; VERIFIED: local command `python3 -c import littlefs`] |
| GNU gettext `msgfmt`/`xgettext` | local command reports GNU gettext-tools 1.0 | `.po` to `.mo` compilation and POT generation. | Use only through existing CMake/shell generator paths or named update/check labels. [VERIFIED: local command `msgfmt --version`; VERIFIED: local command `xgettext --version`; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: utils/translations_and_fonts/generate_pot.sh] |
| Catch2/CTest | in-repo Catch2 plus CMake/CTest | Existing persistent-store and translation provider reference tests. | Use as reference evidence for journal, hashes, and translation behavior; do not make Phase 7 local verifier depend on a full native CMake build unless planned explicitly. [VERIFIED: .planning/codebase/TESTING.md; VERIFIED: tests/unit/persistent_stores/CMakeLists.txt; VERIFIED: tests/unit/lang/translator/CMakeLists.txt] |
| Python `unittest` verifier tests | standard library | Regression tests for `tools/bazel/phase7_verify.py`. | Mirror `phase6_verify_test.py` for manifest lifecycle, redaction, source-path, and API-surface failures. [VERIFIED: tools/bazel/phase6_verify_test.py] |
| Phase 3 generated drift registry | local source | Queryable check/update labels for generated resources, translations, fonts, WUI assets, ESP blobs, package metadata, and tracked generated outputs. | Phase 7 should require these labels instead of duplicating generator wrappers. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: tools/bazel/generator_rules.bzl; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Existing journal hash generator | A new Rust hash calculator | Do not do this in Phase 7; compatibility depends on the existing generator's 14-bit SHA-256 mask and duplicate detection. [VERIFIED: utils/persistent_stores/journal_hashes_generator.py; VERIFIED: src/persistent_stores/journal/store.hpp] |
| Existing `utils/mklittlefs.py`/`littlefs-python` | Custom LittleFS image writer | Do not do this in Phase 7; image semantics and content-hash behavior already exist in the Python helper and C++ runtime hash code. [VERIFIED: utils/mklittlefs.py; VERIFIED: src/resources/hash.cpp] |
| Phase 3 generated-drift labels | New ad hoc shell scripts | Reusing the Phase 3 registry keeps generated surface evidence queryable and already split into check/update labels. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: tools/bazel/generator_rules.bzl] |
| Manifest/static verifier default | Full firmware/generator/hardware runs on every local check | Heavy runs are non-local evidence by Phase 7 decision and local environment currently lacks some bootstrapped generator dependencies. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: local command `python3 -c import littlefs`; VERIFIED: local command `pre-commit --version`] |

**Installation:** No new package installation is recommended for Phase 7 planning. Use repo-pinned dependencies and bootstrap paths; generator execution that needs `littlefs-python`, pinned CMake 3.28.3, or pre-commit should be gated behind explicit bootstrap/fallback handling. [VERIFIED: requirements.txt; VERIFIED: utils/bootstrap.py; VERIFIED: local command `.dependencies/cmake-3.28.3/bin/cmake --version`; VERIFIED: local command `pre-commit --version`]

**Version verification:** This phase recommends no new npm/PyPI/Rust dependency additions. Versions above were verified from local manifests and local commands instead of registry lookups. [VERIFIED: requirements.txt; VERIFIED: Cargo.toml; VERIFIED: rust/crates/domain/Cargo.toml; VERIFIED: local command outputs]

## Architecture Patterns

### Recommended Project Structure

```text
rust/crates/domain/src/
|-- storage.rs          # Extend existing schema/migration/key seed.
|-- storage/            # Add focused modules if storage.rs exceeds Bright Builds size guidance.
|-- resource.rs         # Resource image/package/runtime visibility contracts if planner chooses a new module.
`-- artifact.rs         # Reuse/extend artifact kind and filename identity where it fits.

tools/bazel/
|-- manifests/
|   |-- phase7_config_store.json
|   |-- phase7_storage_media.json
|   |-- phase7_resources.json
|   |-- phase7_generated_outputs.json
|   `-- phase7_concern_dispositions.json
|-- phase7_verify.py
`-- phase7_verify_test.py

.planning/phases/07-persistence-storage-and-resource-compatibility/
|-- 07-CONTEXT.md
|-- 07-RESEARCH.md
`-- 07-VALIDATION.md
```

This structure mirrors existing Rust domain modules, Phase 6 verifier/manifests, and root Bazel/just facade patterns. [VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: tools/bazel/manifests/phase6_printing_core.json; VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: BUILD.bazel; VERIFIED: justfile]

### Pattern 1: Source-Backed Manifest Rows

**What:** Every compatibility fact should be a JSON row with a stable ID, requirement, source paths, Rust surface, evidence class, local/non-local classification, redaction policy when relevant, and intentional-delta status. [VERIFIED: tools/bazel/manifests/phase6_printing_core.json; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

**When to use:** Use this for config items/defaults/deprecated IDs, EEPROM migration windows, storage drivers, filesystem devices, resource package members, translation/font/generated outputs, and concern dispositions. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/resources/CMakeLists.txt]

**Example:**

```json
{
  "id": "config-connect-token",
  "requirement": "IFCE-04",
  "source_paths": [
    "src/persistent_stores/store_instances/config_store/store_definition.hpp",
    "src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp"
  ],
  "reference_name": "Connect Token",
  "compatibility_surface": "credential-bearing-config-item",
  "evidence_class": "source-audit",
  "local_evidence": true,
  "redaction_policy": "name-only-no-value",
  "rust_surface": "rust/crates/domain/src/storage.rs::CredentialBearingStorageItem",
  "intentional_delta": null
}
```

Source pattern: Phase 6 manifests use source-backed rows and Phase 7 decisions require credential-bearing keys to be name-only/redacted. [VERIFIED: tools/bazel/manifests/phase6_printing_core.json; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp]

### Pattern 2: Distinguish Reference Hash Names from Rust-Safe IDs

**What:** Use separate Rust types for raw reference `journal::hash("...")` names and manifest-safe identifiers. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: rust/crates/domain/src/storage.rs]

**When to use:** Use this whenever the source name may include spaces or legacy strings but the manifest/API ID must remain stable and parser-friendly. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: rust/crates/domain/src/storage.rs]

**Example:**

```rust
// Source pattern: rust/crates/domain/src/storage.rs uses fallible constructors.
pub struct ReferenceHashName(String);
pub struct ManifestStorageId(String);
```

The exact names are planner discretion, but the type split is required because existing C++ hash names include spaces and current `StorageKey::parse` rejects whitespace. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: rust/crates/domain/src/storage.rs]

### Pattern 3: Retain Runtime Adapters, Model Contracts in Rust

**What:** Keep FatFs, littlefs, libsysbase, EEPROM drivers, and resource bootstrap as retained reference/adapters while Rust models the allowed mounts, path prefixes, resource identities, and evidence classes. [VERIFIED: tools/bazel/manifests/foreign_code_inventory.json; VERIFIED: src/buddy/filesystem.cpp; VERIFIED: lib/libsysbase/iosupport.c]

**When to use:** Use this for `/usb`, `/internal`, `/bbf`, `/semihosting`, root listing, and resource bootstrap paths. [VERIFIED: src/buddy/filesystem_fatfs.cpp; VERIFIED: src/buddy/filesystem_littlefs_internal.cpp; VERIFIED: src/buddy/filesystem_littlefs_bbf.cpp; VERIFIED: src/buddy/filesystem_semihosting.cpp; VERIFIED: src/resources/bootstrap.cpp]

**Example:**

```rust
// Source pattern: ProductProfile and ArtifactRequest parse raw values before use.
pub enum StorageMount {
    Usb,
    Internal,
    Bbf,
    Semihosting,
    Root,
}
```

Use pure enums/newtypes for identity, then leave actual open/read/write/erase behavior to retained adapters until simulator or hardware evidence exists. [VERIFIED: rust/crates/domain/src/artifact.rs; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

### Pattern 4: Split Tracked Generated Outputs from Build-Generated Outputs

**What:** Keep tracked generated outputs reviewable in source while generated-at-build outputs are produced or compared through Bazel labels and manifests. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-CONTEXT.md; VERIFIED: tools/bazel/generated_drift.py]

**When to use:** Use this for `CMakePresets.json`, `doc/logging_components.md`, `include/common/visit_all_struct_fields.hpp`, `src/lang/po/Prusa-Firmware-Buddy.pot`, font/resource headers, PNGs, WUI assets, ESP blobs, resource images, and translation `.mo` outputs. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: src/lang/CMakeLists.txt; VERIFIED: include/common/visit_all_struct_fields.hpp]

### Anti-Patterns to Avoid

- **Primitive string storage contracts:** Primitive strings will hide invalid or legacy identities; use fallible Rust types and source-backed manifests. [VERIFIED: rust/crates/domain/src/storage.rs; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/languages/rust.md]
- **Deleting deprecated store items because Rust does not need them:** Deprecated items keep hashed IDs and may still be migration inputs. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/persistent_stores/store_instances/config_store/migrations.cpp]
- **Default local verifier runs full generator/hardware flows:** Phase 7 decisions classify those as non-local unless a narrow fixture is created. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]
- **Byte-parity claims for full resource/release artifacts:** Phase 7 should compare semantic content, declared inputs, hashes/revisions, filenames, and runtime visibility unless a normalized fixture is explicitly created. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Journal ID calculation | A new hash implementation in Rust or Python | `utils/persistent_stores/journal_hashes_generator.py` and generated hash evidence | The reference hashes are SHA-256-derived, masked with `0x3FFF`, and duplicate-checked by the existing generator. [VERIFIED: utils/persistent_stores/journal_hashes_generator.py] |
| EEPROM/config migration logic | A parallel Rust migration that is not fixture/source-backed | Source-backed manifests plus fixtures around `store_definition.hpp`, `migrations.cpp`, and `old_eeprom/last_migration.cpp` | The current path migrates old EEPROM versions and credential-bearing fields into journal transactions; Phase 7 must preserve identity. [VERIFIED: src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp; VERIFIED: src/persistent_stores/store_instances/config_store/migrations.cpp] |
| LittleFS image creation | Custom image writer | `cmake/Littlefs.cmake` invoking `utils/mklittlefs.py` with `littlefs-python==0.8` | The helper creates erased images, adds files, and computes content hashes that align with runtime hash logic. [VERIFIED: cmake/Littlefs.cmake; VERIFIED: utils/mklittlefs.py; VERIFIED: requirements.txt; VERIFIED: src/resources/hash.cpp] |
| Gettext `.mo` parsing/generation | Custom translation compiler | Existing `msgfmt`, `lang.py`, and C++ gettext hash/provider code | CMake already compiles `.po` to `.mo`, and runtime providers use `.mo` paths under `/internal/res/lang`. [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: src/lang/translation_provider_FILE.cpp; VERIFIED: src/lang/gettext_string_hash.cpp] |
| FatFs/POSIX semantics | A local stub that claims `/usb` compatibility | Model `/usb` as a contract and retain FatFs/libsysbase until non-local evidence proves replacement | USB/media behavior crosses FatFs, USB host disk I/O, libsysbase devoptabs, and hardware timing. [VERIFIED: src/buddy/filesystem_fatfs.cpp; VERIFIED: src/buddy/usbh_diskio.cpp; VERIFIED: lib/libsysbase/iosupport.c; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Resource package and BBF semantics | Non-reference BBF/resource encoders | Existing `utils/pack_fw.py`, `cmake/Littlefs.cmake`, and Phase 3 artifact/generated wrappers | Phase 3 already established reference-format status handling and generated check/update labels. [VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md; VERIFIED: tools/bazel/generated_drift.py; VERIFIED: tools/bazel/BUILD.bazel] |
| Credential fixture handling | Sample passwords, tokens, certificates, EEPROM bytes, or signing material | Name-only redacted rows plus verifier scans | Phase 7 explicitly forbids secret values and EEPROM bytes in artifacts/logs/commits. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |

**Key insight:** This phase is about preserving compatibility protocols and visibility, not replacing complex storage/filesystem/generator implementations. The planner should add typed identities, manifests, fixture catalogs, and verifier enforcement around the existing reference surfaces. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: tools/bazel/manifests/foreign_code_inventory.json]

## Runtime State Inventory

This inventory is included because the phase includes migration and storage compatibility, even though it is not a rename/rebrand phase. [VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | Persistent config lives in the firmware config store/journal over EEPROM storage; old EEPROM schemas migrate through `old_eeprom/last_migration.cpp`; internal resources store installed resources under `/internal/res` and the revision at `/internal/resources_revision`; custom Connect CA path is `/internal/connect/connect.der`; USB media is exposed under `/usb`. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp; VERIFIED: src/resources/bootstrap.cpp; VERIFIED: include/resources/revision.hpp; VERIFIED: .planning/codebase/INTEGRATIONS.md] | Create config/default/deprecated-ID/migration/credential manifests; create redacted fixture identities, not raw EEPROM bytes; classify actual media/flash behavior as non-local unless a normalized fixture is planned. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Live service config | Firmware has external Connect/WUI/metrics consumers, but Phase 7 storage compatibility is local to config names/paths and not Connect/WUI API behavior. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/INTEGRATIONS.md] | Do not modify external service behavior; only manifest storage keys/paths such as Connect token, host/proxy/TLS flags, PrusaLink password, WiFi SSID/password, metrics/syslog settings. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: .planning/codebase/INTEGRATIONS.md] |
| OS-registered state | None in firmware scope; this repo builds embedded firmware and no systemd/launchd/pm2-like registration is part of Phase 7 storage/resource compatibility. [VERIFIED: .planning/codebase/STACK.md; VERIFIED: .planning/codebase/INTEGRATIONS.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] | No OS re-registration task needed. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Secrets/env vars | Credential-bearing config items include WiFi password, PrusaLink password, Connect token, and custom TLS certificate flag/path; build-time signing uses `SIGNING_KEY`; `BUDDY_NO_VIRTUALENV` controls bootstrap behavior; CI uses provider-managed secrets. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: .planning/codebase/INTEGRATIONS.md; VERIFIED: .planning/codebase/STACK.md] | Manifest key names and paths only; verifier must reject private-key PEM markers, `SIGNING_KEY=`, certificate bytes, token/password-looking fixture values, and raw EEPROM bytes in Phase 7 manifests/fixtures. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-02-PLAN.md] |
| Build artifacts | Generated-at-build outputs include littlefs images, resource hash headers, `.mo` files, QOI data, ESP parts headers, bootloader/MMU generated headers, and Bazel representative package outputs; tracked generated outputs include `CMakePresets.json`, `doc/logging_components.md`, `include/common/visit_all_struct_fields.hpp`, POT/font/resource assets. [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: src/lang/CMakeLists.txt; VERIFIED: tools/bazel/generated_drift.py; VERIFIED: include/common/visit_all_struct_fields.hpp] | Reuse Phase 3 generated check/update labels and add Phase 7 manifests proving which outputs are tracked source vs generated-at-build. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |

## Common Pitfalls

### Pitfall 1: Conflating Journal Names with Rust Storage Keys

**What goes wrong:** Planner maps `journal::hash("WIFI AP Password")` directly to the current `StorageKey` type and loses compatibility because current Rust parsing rejects whitespace. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: rust/crates/domain/src/storage.rs]

**Why it happens:** Existing Rust storage modeling started with conservative machine-friendly keys, while C++ hash names are legacy user/source strings. [VERIFIED: rust/crates/domain/src/storage.rs; VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp]

**How to avoid:** Add a separate raw reference hash-name type and keep manifest IDs stable and machine-friendly. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: rust/crates/domain/src/storage.rs]

**Warning signs:** Manifest rows contain only Rust-safe IDs and omit `reference_name` or generated hash evidence. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

### Pitfall 2: Treating Deprecated Items as Dead Code

**What goes wrong:** A plan removes deprecated items or changes hashed names because the current Rust shape does not need them. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp]

**Why it happens:** Deprecated config entries are not ordinary active fields; they are compatibility anchors for journal scanning and migration functions. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/persistent_stores/store_instances/config_store/migrations.cpp]

**How to avoid:** Require deprecated-ID manifests, hash drift coverage, migration evidence, and intentional-delta records for any rename/removal/hash change. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

### Pitfall 3: Leaking Secrets Through Helpful Fixtures

**What goes wrong:** A storage fixture embeds a realistic WiFi password, Connect token, custom certificate, signing path/value, or raw EEPROM bytes. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/INTEGRATIONS.md]

**Why it happens:** The old EEPROM migration path names credential-bearing fields, and config-store defaults include credential arrays. [VERIFIED: src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp; VERIFIED: src/persistent_stores/store_instances/config_store/defaults.hpp]

**How to avoid:** Store only key names, path identities, redaction policy, and synthetic fixture IDs; add verifier scans for forbidden markers and value-like secret fields. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-02-PLAN.md]

### Pitfall 4: Overclaiming Local Storage and Resource Proof

**What goes wrong:** `just phase7-verify` passes and the summary claims USB media, flash wear, mount timing, simulator, or hardware resource behavior is proven. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

**Why it happens:** Source-path coverage and manifest checks are easy to confuse with runtime evidence. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: .planning/phases/06-printing-core-safety-and-feature-gates/06-05-PLAN.md]

**How to avoid:** Require evidence-class fields and overclaim guards in the verifier. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

### Pitfall 5: Running Heavy Generators in Default Local Verification

**What goes wrong:** Local Phase 7 verification fails on missing bootstrap dependencies even though the code/manifests are valid. [VERIFIED: local command `python3 -c import littlefs`; VERIFIED: local command `.dependencies/cmake-3.28.3/bin/cmake --version`; VERIFIED: local command `pre-commit --version`]

**Why it happens:** Fonts, LittleFS images, pre-commit, and resource generation depend on repo bootstrap and optional tooling. [VERIFIED: utils/translations_and_fonts/generate_single_font.sh; VERIFIED: utils/mklittlefs.py; VERIFIED: requirements.txt; VERIFIED: .planning/codebase/STACK.md]

**How to avoid:** Default verifier should validate wiring and manifests; generator execution should be explicit update/check labels with bootstrap-required or non-local evidence classification. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

### Pitfall 6: Ignoring Known Concern Dispositions

**What goes wrong:** Phase 7 handles storage/resources but leaves generated drift, shell safety, credential-at-rest, hash-space, block-randomness, littlefs dependency drift, and font/header churn undocumented. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md]

**Why it happens:** These are not all bugs to fix immediately, but D-11 requires explicit disposition. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

**How to avoid:** Add `phase7_concern_dispositions.json` and have the verifier require each known concern ID/category with preserve/fix/defer status and evidence. [VERIFIED: tools/bazel/manifests/phase6_concern_dispositions.json; VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: .planning/codebase/CONCERNS.md]

## Code Examples

### Phase 7 Verifier Dispatch

```bash
# Source pattern: tools/bazel/rust_workflow.sh
phase7_verify)
  python3 tools/bazel/phase7_verify.py --all
  ;;
phase7_verify_tests)
  python3 tools/bazel/phase7_verify_test.py
  ;;
```

Use this pattern because Phase 4-6 verifiers already dispatch through `rust_workflow.sh` and Bazel `shell_binary` targets. [VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: tools/bazel/BUILD.bazel]

### Phase 7 Just Facade

```make
# Source pattern: justfile
phase7-verify:
    bazel run //tools/bazel:phase7_verify_tests
    bazel run //tools/bazel:phase7_verify
```

Use this pattern because Phase 6 already runs verifier tests before the aggregate verifier. [VERIFIED: justfile]

### Rust Fallible Constructor Shape

```rust
// Source pattern: rust/crates/domain/src/storage.rs
impl StorageSchemaVersion {
    pub fn new(raw: u16) -> Result<Self, InvariantError> {
        if raw == 0 {
            return Err(InvariantError::InvalidStorageSchemaVersion);
        }

        Ok(Self(raw))
    }
}
```

Follow this style for `ReferenceHashName`, `CredentialRedactionPolicy`, `FixtureId`, `ResourcePackageMember`, and `StorageMount` types. [VERIFIED: rust/crates/domain/src/storage.rs; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/languages/rust.md]

### Resource Manifest Row Shape

```json
{
  "id": "resource-wui-index",
  "requirement": "IFCE-05",
  "source_paths": [
    "src/resources/CMakeLists.txt",
    "src/resources/web/index.html"
  ],
  "runtime_path": "/web/index.html",
  "generated_surface": "resources",
  "tracked_output": true,
  "evidence_class": "source-audit",
  "rust_surface": "rust/crates/domain/src/resource.rs::ResourcePackageMember",
  "intentional_delta": null
}
```

Source pattern: resource install paths are declared in `src/resources/CMakeLists.txt`, and Phase 3 generated-drift already has a `resources` surface. [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: tools/bazel/generated_drift.py]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CMake/Python is the only visible authority for resources and generated assets. | Bazel remains authoritative while existing CMake/Python generators stay as reference/update paths exposed through queryable labels. | Phase 2 made Bazel primary; Phase 3 added generated check/update surfaces. [VERIFIED: .planning/PROJECT.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md] | Phase 7 should add manifests/verifier checks, not another generator authority. [VERIFIED: tools/bazel/generated_drift.py] |
| Persistent config is implicit in C++ structs and generator side effects. | Phase 7 should freeze source-backed manifests for current items, defaults, deprecated IDs, migration windows, and hash facts. | Phase 7 decisions D-01 through D-04. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] | Planner needs manifest tasks before adapter or Rust extension tasks. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Local checks might be read as proof of physical behavior. | Evidence classes must distinguish local source/manifest/Rust checks from simulator, hardware, and manual evidence. | Phase 1 catalog and Phase 6 verifier pattern. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md; VERIFIED: tools/bazel/phase6_verify.py] | Phase 7 verifier should reject overclaims. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Primitive IDs are accepted late. | Raw values should be parsed into Rust newtypes/enums/fallible constructors before domain use. | Phase 4 Rust invariant model and Bright Builds Rust guidance. [VERIFIED: rust/crates/domain/src/storage.rs; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/languages/rust.md] | Add narrow domain types for storage, hash names, fixtures, resource members, and redaction. [VERIFIED: rust/crates/domain/src/storage.rs; VERIFIED: rust/crates/domain/src/artifact.rs] |

**Deprecated/outdated:**

- Treating pre-commit as the only generated drift gate is insufficient for Phase 7 because pre-commit is not installed locally and Phase 3 already created Bazel-owned generated drift labels. [VERIFIED: local command `pre-commit --version`; VERIFIED: tools/bazel/generated_drift.py]
- Treating block-device random tests as reliable storage validation needs caution because `select_random_block()` uses inclusive `random.randint(0, BLOCK_COUNT)`. [VERIFIED: tests/blockdevice/test_block_device.py]
- Treating credential encryption-at-rest as Phase 7's default fix contradicts D-05; it is a known reference fact unless approved as an intentional delta. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|

All claims in this research were verified against local project files, local command output, or cited Bright Builds standards. No `[ASSUMED]` claim is intentionally present. [VERIFIED: AGENTS.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

## Open Questions

1. **Where should durable Phase 7 storage fixtures live?**
   - What we know: Phase 1 catalog names persistent-store migration fixtures as a local-smoke reference capture, and `rg` found only Phase 3 non-secret artifact/resource fixture files under `tools/bazel/fixtures/`. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md; VERIFIED: local command `find tools/bazel/fixtures -maxdepth 4 -type f`]
   - What's unclear: No committed redacted EEPROM/config migration fixture corpus for Phase 7 was found in this research scan. [VERIFIED: local command `rg -n "EEPROM.*fixture|fixture.*EEPROM|storage fixture|storage.*fixture|migration fixture"`]
   - Recommendation: Plan a Wave 0 fixture catalog using synthetic/redacted fixture identities first, and only add raw/reference captures if a later decision explicitly approves a sanitized format. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

2. **Should Phase 7 fix shell-generator safety or only disposition it?**
   - What we know: D-11 requires disposition; `generate_all_fonts.sh` and `generate_single_font.sh` use `#!/bin/bash` without `set -euo pipefail`, while `generate_pot.sh` and `generate-translations-report.sh` use only `set -e`. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: utils/translations_and_fonts/generate_all_fonts.sh; VERIFIED: utils/translations_and_fonts/generate_single_font.sh; VERIFIED: utils/translations_and_fonts/generate_pot.sh; VERIFIED: utils/translations_and_fonts/generate-translations-report.sh]
   - What's unclear: The context does not mandate fixing these scripts during Phase 7. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]
   - Recommendation: Default to explicit concern disposition plus generator label verification; fix scripts only if the planner creates a narrow intentional-delta task with regression evidence. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

3. **How much generator execution should `just phase7-verify` run locally?**
   - What we know: Bazel, just, Rust, CMake, Ninja, `msgfmt`, and `xgettext` are available; local Python cannot import `littlefs`, `.dependencies/cmake-3.28.3/bin/cmake` is missing, and `pre-commit` is missing. [VERIFIED: local command `bazel --version`; VERIFIED: local command `just --version`; VERIFIED: local command `cargo --version`; VERIFIED: local command `cmake --version`; VERIFIED: local command `ninja --version`; VERIFIED: local command `msgfmt --version`; VERIFIED: local command `python3 -c import littlefs`; VERIFIED: local command `.dependencies/cmake-3.28.3/bin/cmake --version`; VERIFIED: local command `pre-commit --version`]
   - What's unclear: Whether the execution phase will run `utils/bootstrap.py` before Phase 7 generator checks. [VERIFIED: .planning/codebase/STACK.md]
   - Recommendation: Make `--quick` static; make `--all` run Rust checks and verifier tests; leave full generator execution as explicit `generated-check`/`generated-update` or bootstrap-required evidence unless bootstrap is guaranteed. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: tools/bazel/generated_drift.py; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Verifier, generators, requirements tooling | yes | 3.14.4 local | Repo requires Python 3.8+; use repo bootstrap/venv for pinned deps. [VERIFIED: local command `python3 --version`; VERIFIED: .planning/codebase/STACK.md] |
| Bazel | Phase 7 verifier labels and queryability | yes | 9.1.1 local | None needed for label checks. [VERIFIED: local command `bazel --version`; VERIFIED: tools/bazel/BUILD.bazel] |
| just | Developer facade | yes | 1.48.0 local | Direct `bazel run` commands. [VERIFIED: local command `just --version`; VERIFIED: justfile] |
| Rust cargo/rustc | `buddy-domain` checks | yes | cargo 1.91.1, rustc 1.91.1 local | Workspace rust-version is 1.85; local toolchain is newer. [VERIFIED: local command `cargo --version`; VERIFIED: local command `rustc --version`; VERIFIED: Cargo.toml] |
| CMake | Existing C++/resource/test reference flows | yes | system 3.27.9 local | Repo bootstrap downloads 3.28.3; system version satisfies root CMake 3.22 minimum but not scripts that hard-code `.dependencies/cmake-3.28.3/bin/cmake`. [VERIFIED: local command `cmake --version`; VERIFIED: CMakeLists.txt; VERIFIED: utils/translations_and_fonts/generate_single_font.sh; VERIFIED: local command `.dependencies/cmake-3.28.3/bin/cmake --version`] |
| Pinned `.dependencies/cmake-3.28.3/bin/cmake` | Font generator script | no | missing | Run `python3 utils/bootstrap.py` before full font generator runs, or keep Phase 7 verifier static. [VERIFIED: utils/translations_and_fonts/generate_single_font.sh; VERIFIED: local command `.dependencies/cmake-3.28.3/bin/cmake --version`; VERIFIED: utils/bootstrap.py] |
| Ninja | Native CMake/font generator build path | yes | 1.13.2 local | Bootstrap can provide pinned Ninja for reference flows. [VERIFIED: local command `ninja --version`; VERIFIED: .planning/codebase/STACK.md] |
| gettext `msgfmt` | Translation `.mo` generation | yes | GNU gettext-tools 1.0 local | Mark translation generation as bootstrap/CI/reference evidence if tool is absent in other environments. [VERIFIED: local command `msgfmt --version`; VERIFIED: src/resources/CMakeLists.txt] |
| gettext `xgettext` | POT generation | yes | GNU gettext-tools 1.0 local | Use existing `generate_pot.sh` or generated-drift labels. [VERIFIED: local command `xgettext --version`; VERIFIED: utils/translations_and_fonts/generate_pot.sh] |
| `littlefs-python` module | `utils/mklittlefs.py` | no in host Python | pinned `0.8` in requirements | Run bootstrap/venv before generator execution; static verifier can still validate wiring. [VERIFIED: requirements.txt; VERIFIED: utils/mklittlefs.py; VERIFIED: local command `python3 -c import littlefs`] |
| pre-commit | Existing tracked generated output hook path | no | missing | Use Bazel `generated_check` labels for default Phase 7 evidence; install/bootstrap only for explicit hook runs. [VERIFIED: local command `pre-commit --version`; VERIFIED: tools/bazel/generated_drift.py; VERIFIED: .pre-commit-config.yaml] |

**Missing dependencies with no fallback:** None for static Phase 7 research/planning/verifier design. [VERIFIED: environment audit above]

**Missing dependencies with fallback:**

- `littlefs-python` and pinned CMake 3.28.3 are missing for full LittleFS/font generator runs; fallback is repo bootstrap or static manifest/wiring validation. [VERIFIED: requirements.txt; VERIFIED: utils/bootstrap.py; VERIFIED: local command `python3 -c import littlefs`; VERIFIED: local command `.dependencies/cmake-3.28.3/bin/cmake --version`]
- `pre-commit` is missing; fallback is Bazel `generated_check`/`generated_update` surfaces and targeted generator commands. [VERIFIED: local command `pre-commit --version`; VERIFIED: tools/bazel/generated_drift.py]

## Validation Architecture

Nyquist validation applies because `.planning/config.json` sets `workflow.nyquist_validation` to `true`. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Bazel `shell_binary` wrappers plus Python standard-library verifier tests and Rust cargo checks. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/phase6_verify_test.py; VERIFIED: tools/bazel/rust_workflow.sh] |
| Config file | `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `justfile`, `Cargo.toml`, and `pyproject.toml`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile; VERIFIED: Cargo.toml; VERIFIED: pyproject.toml] |
| Quick run command | `python3 tools/bazel/phase7_verify.py --quick` once created. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Full suite command | `just phase7-verify` once created. [VERIFIED: justfile; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| IFCE-04 | Config-store items, defaults, deprecated IDs, old EEPROM migration windows, credential-key redaction, journal hash evidence, and storage-driver source paths are manifest-covered. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp] | static manifest/verifier plus Rust unit tests | `python3 tools/bazel/phase7_verify.py --quick` | no, Wave 0. [VERIFIED: local command `find tools/bazel/manifests -maxdepth 1 -type f`] |
| IFCE-04 | Rust storage domain types reject invalid schema versions, invalid migration windows, unredacted credentials, invalid fixture IDs, and unsafe pure-domain code. [VERIFIED: rust/crates/domain/src/storage.rs; VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] | Rust unit tests and static unsafe scan | `cargo test --all-features` and `python3 tools/bazel/phase7_verify.py --quick` | partial; existing storage tests exist, Phase 7 types do not. [VERIFIED: rust/crates/domain/src/storage.rs] |
| IFCE-04 | Filesystem surfaces `/usb`, `/internal`, `/bbf`, `/semihosting`, and root listing are represented as named compatibility contracts with local/non-local evidence classes. [VERIFIED: src/buddy/filesystem.cpp; VERIFIED: src/buddy/filesystem_fatfs.cpp; VERIFIED: src/buddy/filesystem_littlefs_internal.cpp; VERIFIED: src/buddy/filesystem_littlefs_bbf.cpp; VERIFIED: src/buddy/filesystem_semihosting.cpp; VERIFIED: src/buddy/filesystem_root.cpp] | static manifest/verifier plus Rust unit tests | `python3 tools/bazel/phase7_verify.py --quick` | no, Wave 0. [VERIFIED: tools/bazel/manifests] |
| IFCE-05 | Resource package members, WUI assets, ESP blobs, bootloader/MMU resources, QOI data, language packs, resource hashes/revisions, and generated headers are manifest-covered and tied to Phase 3 generated labels. [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: src/resources/bootstrap.cpp; VERIFIED: src/lang/CMakeLists.txt; VERIFIED: tools/bazel/generated_drift.py] | static manifest/verifier | `python3 tools/bazel/phase7_verify.py --quick` | no, Wave 0. [VERIFIED: tools/bazel/manifests] |
| IFCE-05 | Generated drift surfaces remain queryable through Bazel and update labels are distinct from check labels. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: tools/bazel/generator_rules.bzl; VERIFIED: tools/bazel/BUILD.bazel] | Bazel query/static verifier | `bazel query "//tools/bazel:generated_check + //tools/bazel:generated_update"` and `python3 tools/bazel/phase7_verify.py --quick` | existing Phase 3 labels exist; Phase 7 aggregate checks do not. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel] |

### Sampling Rate

- **Per task commit:** `python3 tools/bazel/phase7_verify.py --quick` plus focused Rust test command for touched Rust modules. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: rust/crates/domain/src/storage.rs]
- **Per wave merge:** `bazel run //tools/bazel:phase7_verify_tests && python3 tools/bazel/phase7_verify.py --all` once labels exist. [VERIFIED: tools/bazel/phase6_verify_test.py; VERIFIED: tools/bazel/rust_workflow.sh]
- **Phase gate:** `just phase7-verify`, `bazel query` for new Phase 7 labels, and explicit record of non-local generator/hardware evidence classes. [VERIFIED: justfile; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]

### Wave 0 Gaps

- [ ] `tools/bazel/phase7_verify.py` - validates manifests, source paths, Rust API surface, redaction, no unsafe, generated label wiring, concern dispositions, lifecycle, and overclaim guards. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]
- [ ] `tools/bazel/phase7_verify_test.py` - regression tests for missing rows, invalid lifecycle, unredacted credentials, missing source paths, missing Rust API strings, missing generated labels, and overclaims. [VERIFIED: tools/bazel/phase6_verify_test.py]
- [ ] `tools/bazel/manifests/phase7_config_store.json` - current items, defaults, deprecated IDs, old EEPROM versions, migration windows, credential-bearing keys, hash evidence. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/persistent_stores/store_instances/config_store/defaults.hpp; VERIFIED: src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp]
- [ ] `tools/bazel/manifests/phase7_storage_media.json` - EEPROM driver, `/usb`, `/internal`, `/bbf`, `/semihosting`, root listing, libsysbase behavior, non-local evidence classes. [VERIFIED: src/persistent_stores/storage_drivers/eeprom_storage.cpp; VERIFIED: src/buddy/filesystem*.cpp; VERIFIED: lib/libsysbase/iosupport.c]
- [ ] `tools/bazel/manifests/phase7_resources.json` - resources image, bootloader image, ESP blobs, WUI assets, translations, QOI, MMU, puppy resources, hashes/revisions, runtime paths. [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: src/resources/bootstrap.cpp; VERIFIED: src/lang/translation_provider_FILE.cpp]
- [ ] `tools/bazel/manifests/phase7_generated_outputs.json` - tracked vs generated-at-build outputs and Phase 3 generated label coverage. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: include/common/visit_all_struct_fields.hpp; VERIFIED: src/lang/po/Prusa-Firmware-Buddy.pot]
- [ ] `tools/bazel/manifests/phase7_concern_dispositions.json` - D-11 concern dispositions. [VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]
- [ ] Rust domain extensions in `rust/crates/domain/src/storage.rs` and/or `rust/crates/domain/src/resource.rs`. [VERIFIED: rust/crates/domain/src/storage.rs; VERIFIED: rust/crates/domain/src/artifact.rs]
- [ ] Bazel and just wiring for `phase7_verify`, `phase7_verify_tests`, root aliases, and `phase7-verify`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile]
- [ ] `.planning/phases/07-persistence-storage-and-resource-compatibility/07-VALIDATION.md` contract with quick/full commands and non-local evidence wording. [VERIFIED: .planning/config.json; VERIFIED: .planning/phases/06-printing-core-safety-and-feature-gates/06-VALIDATION.md]

## Security Domain

Security enforcement is enabled by default because `.planning/config.json` does not set `security_enforcement` to `false`. [VERIFIED: .planning/config.json]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | partial | Phase 7 preserves credential-bearing storage keys only; Connect/WUI auth behavior is deferred to Phase 9. Redact credential values and manifest key names/paths only. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/INTEGRATIONS.md] |
| V3 Session Management | no | No session-management implementation is in Phase 7 scope. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| V4 Access Control | partial | Filesystem path identity is modeled, but runtime permission enforcement and WUI/API file access are later phases. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/INTEGRATIONS.md] |
| V5 Input Validation | yes | Use Rust fallible constructors/newtypes for storage/resource IDs, manifest IDs, migration windows, and fixture identities; validate JSON manifests in the verifier. [VERIFIED: rust/crates/domain/src/storage.rs; VERIFIED: tools/bazel/phase6_verify.py; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/languages/rust.md] |
| V6 Cryptography | partial | Do not hand-roll crypto or journal/resource hash alternatives; preserve reference hash behavior and treat journal/resource hashes as compatibility data, not new security controls. [VERIFIED: utils/persistent_stores/journal_hashes_generator.py; VERIFIED: src/resources/hash.cpp; VERIFIED: .planning/codebase/CONCERNS.md] |
| V9 Data Protection | yes | Do not commit credential values, raw EEPROM bytes, certificates, tokens, or private signing material; unencrypted credential storage is a known reference fact unless explicitly approved as an intentional delta. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md] |

### Known Threat Patterns for Phase 7

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Credential leakage through manifests, fixtures, logs, or generated evidence | Information Disclosure | Name-only credential-bearing keys, redaction policy fields, and verifier scans for private-key, token, certificate, and raw EEPROM markers. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-02-PLAN.md] |
| Config schema/hash drift causing upgrade data loss | Tampering | Manifest current/deprecated IDs, generated hash drift coverage, source-path checks, and migration fixture classification. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: utils/persistent_stores/journal_hashes_generator.py; VERIFIED: .planning/codebase/CONCERNS.md] |
| Journal hash collision or reserved-ID conflict | Tampering/Denial of Service | Preserve generator duplicate detection and `has_unique_items` static assertions; require verifier evidence for hash generator inputs. [VERIFIED: utils/persistent_stores/journal_hashes_generator.py; VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.cpp] |
| Filesystem path confusion across `/usb`, `/internal`, `/bbf`, `/semihosting`, and root | Tampering/Information Disclosure | Model mount identity and runtime paths in Rust/manifests; keep runtime adapter behavior retained until non-local evidence exists. [VERIFIED: src/buddy/filesystem.cpp; VERIFIED: lib/libsysbase/iosupport.c; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Generated asset drift or stale tracked outputs | Tampering | Reuse Phase 3 generated check/update labels and add Phase 7 manifest coverage for tracked vs build-generated outputs. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: .planning/codebase/CONCERNS.md] |
| Overclaiming local proof as hardware/storage proof | Repudiation/Spoofing | Verifier overclaim scan and required evidence-class fields. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md` - locked decisions, discretion, deferred scope, lifecycle ID, canonical refs. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md]
- `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` - Phase 7 goal, success criteria, IFCE-04, IFCE-05. [VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/REQUIREMENTS.md]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` - project and Bright Builds constraints. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards-overrides.md]
- Pinned Bright Builds standards - architecture, code shape, verification, testing, Rust guidance. [CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/core/architecture.md; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/core/code-shape.md; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/core/verification.md; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/core/testing.md; CITED: https://raw.githubusercontent.com/peterryszkiewicz/bright-builds/main/standards/languages/rust.md]
- `src/persistent_stores/store_instances/config_store/`, `src/persistent_stores/journal/`, `utils/persistent_stores/journal_hashes_generator.py`, `tests/unit/persistent_stores/` - persistence oracle and tests. [VERIFIED: listed paths]
- `src/buddy/filesystem*.cpp`, `lib/libsysbase/`, `src/resources/`, `src/lang/`, `cmake/Littlefs.cmake`, `utils/mklittlefs.py`, `utils/translations_and_fonts/` - filesystem/resource/generator oracle. [VERIFIED: listed paths]
- `rust/crates/domain/src/`, `tools/bazel/`, `BUILD.bazel`, `justfile` - Rust invariant and verifier patterns. [VERIFIED: listed paths]

### Secondary (MEDIUM confidence)

- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONCERNS.md` - generated codebase maps and concern inventory, verified against representative source files during this research. [VERIFIED: listed paths]
- Local environment probes for Bazel, just, Rust, Python, CMake, Ninja, gettext, `littlefs-python`, pinned CMake, and pre-commit availability. [VERIFIED: local command outputs]

### Tertiary (LOW confidence)

- None. No unverified web/community sources were used. [VERIFIED: this research session]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - no new dependencies are recommended; stack facts are from repo manifests/source and local command output. [VERIFIED: requirements.txt; VERIFIED: Cargo.toml; VERIFIED: local command outputs]
- Architecture: HIGH - persistence/filesystem/resource surfaces were verified against source files and codebase maps. [VERIFIED: src/persistent_stores/store_instances/config_store/store_definition.hpp; VERIFIED: src/buddy/filesystem.cpp; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: .planning/codebase/ARCHITECTURE.md]
- Pitfalls: HIGH - pitfalls come from locked Phase 7 decisions, source comments, existing verifier patterns, and codebase concerns. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: tools/bazel/phase6_verify.py]
- Environment: MEDIUM - local availability is current for this workstation only and should be rechecked if execution happens in another environment. [VERIFIED: local command outputs]

**Research date:** 2026-06-06
**Valid until:** 2026-07-06 for local architecture and source-backed planning; recheck environment availability before implementation. [VERIFIED: current task date; VERIFIED: local command outputs]
