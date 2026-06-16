---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 7-2026-06-06T04-24-25
generated_at: 2026-06-06T04:25:41.416Z
---

# Phase 7: Persistence, Storage, and Resource Compatibility - Context

**Gathered:** 2026-06-06
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 7 preserves persistent configuration, storage formats, filesystem mounts, generated resources, translations, fonts, WUI assets, ESP blobs, bootloader resources, and bundled runtime assets under the Rust+Bazel firmware. It should establish source-backed Rust contracts, manifests, fixtures, and local verification for IFCE-04 and IFCE-05. Runtime GUI, Connect, WUI API behavior, auxiliary-controller runtime parity, full firmware builds, simulator flows, and hardware media proof remain later phases unless a narrow storage/resource compatibility fixture is needed now.

</domain>

<decisions>
## Implementation Decisions

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and prior decisions
- `.planning/ROADMAP.md` — Phase 7 goal, dependencies, success criteria, and milestone ordering.
- `.planning/REQUIREMENTS.md` — IFCE-04 and IFCE-05 requirement text plus traceability table.
- `.planning/PROJECT.md` — Big Bang, Behavior Parity, Bazel Primary Now, `justfile`, safety, and retained-code constraints.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-CONTEXT.md` — baseline oracle, reference-capture, safety evidence, and no-secret artifact decisions.
- `.planning/phases/03-artifact-and-generator-parity/03-CONTEXT.md` — generated-output ownership, check/update targets, artifact/resource packaging, and reference comparison policy.
- `.planning/phases/04-rust-architecture-and-invariant-model/04-CONTEXT.md` — pure Rust domain modeling, storage invariant seed, and Rust verification decisions.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md` — retained foreign-code boundaries, unsafe audit, and non-local hardware evidence rules.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md` — source-backed manifest pattern, non-local evidence classification, and lifecycle verification discipline.

### Codebase map and concerns
- `.planning/codebase/ARCHITECTURE.md` — persistence/filesystem/resource layers, startup flow, data flow, and shared architectural patterns.
- `.planning/codebase/STRUCTURE.md` — ownership map for `src/persistent_stores`, `src/resources`, `src/lang`, `src/buddy/filesystem*`, and generator tooling.
- `.planning/codebase/STACK.md` — FatFs/littlefs, Python generator, bootstrap, packaging, and resource dependency facts.
- `.planning/codebase/INTEGRATIONS.md` — config-store-backed credentials, Connect/WUI storage consumers, USB/littlefs integrations, and resource packaging surfaces.
- `.planning/codebase/TESTING.md` — persistent-store, block-device, lang/translation, and generated-report testing facts.
- `.planning/codebase/CONCERNS.md` — generated drift, translation/font shell safety, credential storage, config schema/hash fragility, journal hash limits, and related concerns.

### Persistence and filesystem reference surfaces
- `src/persistent_stores/store_instances/config_store/store_definition.hpp` — config item definitions, deprecated IDs, credential-bearing keys, and schema comments.
- `src/persistent_stores/store_instances/config_store/store_definition.cpp` — config-store behavior and migration hooks.
- `src/persistent_stores/store_instances/config_store/defaults.hpp` — runtime defaults for network, Connect, WUI, metrics, and feature state.
- `src/persistent_stores/store_instances/config_store/migrations.cpp` — migration behavior.
- `src/persistent_stores/store_instances/config_store/old_eeprom/` — old EEPROM schema compatibility inputs.
- `src/persistent_stores/journal/backend.cpp` — append-only journal backend, CRC, and bank-selection behavior.
- `src/persistent_stores/journal/store.hpp` — journal store contracts.
- `src/persistent_stores/storage_drivers/eeprom_storage.cpp` — EEPROM storage driver behavior and direct byte writes.
- `src/persistent_stores/GenerateJournalHashes.cmake` — generated hash integration.
- `utils/persistent_stores/journal_hashes_generator.py` — journal hash generation and duplicate detection.
- `utils/persistent_stores/visit_all_struct_fields_generator.py` — generated reflection helper owner.
- `include/common/visit_all_struct_fields.hpp` — tracked generated reflection output.
- `src/buddy/filesystem.cpp` — filesystem initialization orchestration.
- `src/buddy/filesystem_fatfs.cpp` — `/usb` FatFs behavior.
- `src/buddy/filesystem_littlefs_internal.cpp` — `/internal` littlefs behavior.
- `src/buddy/filesystem_littlefs_bbf.cpp` — BBF/resource littlefs behavior.
- `src/buddy/filesystem_root.cpp` — root device listing behavior.
- `src/buddy/filesystem_semihosting.cpp` — optional semihosting filesystem behavior.
- `lib/libsysbase` — POSIX-like filesystem/devoptab support consumed by firmware layers.

### Resources, translations, and generated assets
- `src/resources/CMakeLists.txt` — resource image wiring, ESP blobs, WUI assets, and packaged resources.
- `src/resources/bootstrap.cpp` — runtime resource bootstrap behavior.
- `src/resources/hash.cpp` — resource hash behavior.
- `src/resources/revision.cpp` — resource revision behavior.
- `src/resources/QoiGenerator.cmake` — QOI generation integration.
- `src/resources/web/` — tracked WUI static asset inputs.
- `src/resources/esp32/` — ESP32 firmware/resource blob inputs.
- `src/resources/esp8266/` — ESP8266 firmware/resource blob inputs.
- `cmake/Littlefs.cmake` — littlefs image generation.
- `utils/resources/generate_hash_file.py` — resource hash generation.
- `utils/mklittlefs.py` — littlefs image helper.
- `utils/pack_fw.py` — firmware/resource packaging helper.
- `src/lang/CMakeLists.txt` — language resource build wiring.
- `src/lang/translation_provider_FILE.cpp` — external-file translation provider.
- `src/lang/translation_provider_CPUFLASH.cpp` — CPU-flash translation provider.
- `src/lang/gettext_string_hash.cpp` — gettext string hashing.
- `src/lang/po/Prusa-Firmware-Buddy.pot` — tracked translation template.
- `utils/translations_and_fonts/lang.py` — translation generation logic.
- `utils/translations_and_fonts/README_TRANSLATIONS.md` — translation workflow and manual regeneration notes.
- `utils/translations_and_fonts/README_FONTS.md` — font workflow.
- `utils/translations_and_fonts/generate_pot.sh` — translation template generation.
- `utils/translations_and_fonts/generate_all_fonts.sh` — font generation entrypoint.
- `utils/translations_and_fonts/generate_single_font.sh` — single-font generation entrypoint.
- `utils/translations_and_fonts/generate-translations-report.sh` — translation report generation.

### Existing Rust and verification surfaces
- `rust/crates/domain/src/storage.rs` — current storage key/schema/migration invariant seed.
- `rust/crates/domain/src/artifact.rs` — artifact/resource kind modeling pattern.
- `rust/crates/domain/src/product.rs` — validated product profile source for resource/config gates.
- `tools/bazel/BUILD.bazel` — existing phase verifier target pattern.
- `tools/bazel/rust_workflow.sh` — Rust and phase verifier dispatch pattern.
- `BUILD.bazel` — root aliases and filegroups.
- `justfile` — developer facade and existing phase verifier recipes.

### Tests and fixtures
- `tests/unit/persistent_stores/EEPROM_journal_test.cpp` — persistent journal unit-test reference.
- `tests/blockdevice/test_block_device.py` — block-device behavior and randomness concern.
- `tests/unit/lang/eeprom/tests.cpp` — language EEPROM translation tests.
- `tests/unit/lang/translator/` — translation hashing/provider tests.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `rust/crates/domain/src/storage.rs`: Existing pure Rust storage key, schema version, and migration window types can be extended with config/journal/filesystem/resource compatibility contracts.
- `rust/crates/domain/src/artifact.rs`: Existing artifact kind and filename parsing pattern can inform resource image/package identity and generated-output fixture names.
- `tools/bazel/rust_workflow.sh`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, and `justfile`: Existing Phase 4-6 verifier wiring is the local pattern for `phase7_verify`, verifier tests, root aliases, and `just phase7-verify`.
- `tools/bazel/manifests/*.json`: Existing manifest style for retained-code, unsafe, and Phase 6 contracts should be reused instead of inventing an unrelated schema style.

### Established Patterns
- Persistence uses typed config-store items, old EEPROM schema headers, append-only journal transactions, generated 14-bit hashes, CRC validation, bank selection, and EEPROM storage drivers.
- Filesystems are initialized through `src/buddy/filesystem.cpp`, mounted as named devices such as `/usb`, `/internal`, and `/semihosting`, and consumed through libsysbase/POSIX-like calls.
- Resources are CMake/Python-generated and packaged into firmware/resource images, with tracked WUI/ESP/font/translation/resource outputs kept as source-reviewable artifacts where the current repo already tracks them.
- Prior phases prefer pure Rust domain contracts plus manifest/verifier checks for local proof, while simulator and hardware behavior remains explicitly non-local evidence.

### Integration Points
- `src/buddy/main.cpp` initializes EEPROM/config store, filesystems, resources, USB, ESP flashing, display/connect/puppy tasks, and startup dependencies.
- GUI, Connect, WUI, transfers, crash dumps, MMU/ESP update flows, and language providers consume persistent config, filesystems, and resources.
- Phase 7 should connect to existing Bazel/just verifier patterns without reintroducing CMake/Python as normal authority; reference commands remain compatibility evidence.

</code_context>

<specifics>
## Specific Ideas

- Use source-backed manifests as the common contract across config items, storage media, resources, generated outputs, and concern dispositions.
- Prefer fixture and verifier tests that prove one compatibility fact at a time: migration window validity, deprecated item/hash preservation, credential redaction, mount/resource identity, and generated asset drift coverage.
- Keep local checks lightweight and deterministic; classify full media/hardware/generator behavior honestly instead of overclaiming.

</specifics>

<deferred>
## Deferred Ideas

- Runtime GUI display of persisted settings and localization flows belongs to Phase 8 unless Phase 7 needs a narrow storage/resource fixture.
- Connect/WUI API behavior, token use over the network, TLS custom certificate parsing, and HTTP static asset serving behavior belong to Phase 9.
- Auxiliary-controller update/runtime parity, puppy/MMU toolchanger resources in motion, and Modbus behavior belong to Phase 10.
- Full parity pyramid, hardware media smoke, simulator flows, and release-candidate cutover evidence belong to Phase 11.

</deferred>

---

*Phase: 07-persistence-storage-and-resource-compatibility*
*Context gathered: 2026-06-06*
