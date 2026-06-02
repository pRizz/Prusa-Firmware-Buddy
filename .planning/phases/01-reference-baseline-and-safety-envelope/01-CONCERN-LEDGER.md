# Phase 1 Intentional-Delta Concern Ledger

## Requirement Coverage

- **BASE-03:** Maintainer can review an intentional-delta ledger that classifies each known defect from `.planning/codebase/CONCERNS.md` as preserved temporarily, fixed during rewrite, or explicitly deferred.

## Disposition Values

Allowed dispositions:

- `preserve-temporarily` - The Rust port should initially preserve current behavior until a later phase intentionally changes it with evidence.
- `fix-during-rewrite` - The Rust port should intentionally correct the issue in the owning subsystem phase with tests or safety evidence.
- `defer` - The issue is known but outside v1 parity unless explicitly promoted later.

## Ledger

| ID | Category | Current Behavior Or Risk | Affected Files | disposition | Target Phase | Verification Expectation |
|----|----------|--------------------------|----------------|-------------|--------------|--------------------------|
| CL-001 | tech-debt | Global target/include coupling can hide subsystem ownership and optional dependency mistakes. | `CMakeLists.txt`, `ProjectOptions.cmake` | fix-during-rewrite | Phase 2, Phase 5 | Bazel target graph and retained-code inventory expose explicit ownership. |
| CL-002 | tech-debt | MMU reporting includes empty methods, hard-coded availability, and disabled sound behavior. | `src/mmu2/mmu2_reporting.cpp`, `src/mmu2/mmu2_serial.cpp` | fix-during-rewrite | Phase 10 | Auxiliary/MMU state tests prove availability and reporting are explicit. |
| CL-003 | generated-assets | Presets, logging docs, fonts, translations, and generated helpers can drift from sources. | `CMakePresets.json`, `.pre-commit-config.yaml`, `utils/translations_and_fonts/` | fix-during-rewrite | Phase 3, Phase 7 | Bazel/just drift checks fail on stale tracked generated outputs. |
| CL-004 | tooling | Translation/font shell scripts do not consistently use safe shell defaults. | `utils/translations_and_fonts/generate_all_fonts.sh`, `utils/translations_and_fonts/new_translations.sh` | fix-during-rewrite | Phase 3, Phase 7 | Generator wrappers fail fast and are covered by drift checks. |
| CL-005 | testing | Disabled Connect module test target references stale `src/Connect` paths. | `tests/CMakeLists.txt`, `tests/module/Connect/CMakeLists.txt`, `src/connect/` | fix-during-rewrite | Phase 9, Phase 11 | Network parity gate has current Connect/WUI coverage or archived stale tests. |
| CL-006 | known-bug | Custom TLS certificate path allocates DER buffer but does not read certificate bytes before parsing. | `src/connect/tls/tls.cpp` | fix-during-rewrite | Phase 9 | Negative custom-certificate fixture proves DER bytes are read and weak paths fail safely. |
| CL-007 | known-bug | Probe variance mean is knowingly wrong and classifier thresholds depend on the bug. | `src/common/probe_analysis.cpp` | preserve-temporarily | Phase 6 | Fixture records current classifier behavior; any fix updates thresholds as intentional delta. |
| CL-008 | known-bug | Home screen can remain active with events disabled when flash action fails to start. | `src/gui/screen_home.cpp` | fix-during-rewrite | Phase 8 | GUI/error-flow parity tests cover no-op flash action and event re-enable behavior. |
| CL-009 | known-bug | Transfer partial-file progress logging is disabled due to AsyncIO stack overflow. | `src/transfers/partial_file.cpp` | defer | Phase 9 or v2 | Transfer parity keeps current disabled behavior unless telemetry redesign is approved. |
| CL-010 | test-bug | Block-device random test can address one block past declared range. | `tests/blockdevice/test_block_device.py` | fix-during-rewrite | Phase 7, Phase 11 | Storage validation uses valid block selection and catches migration regressions. |
| CL-011 | security | Crash dumps include RAM/CCMRAM and optional upload uses plain socket HTTP when configured. | `src/common/crash_dump/dump.cpp`, `src/common/crash_dump/crash_dump_distribute.cpp`, `src/gui/screen_home.cpp` | fix-during-rewrite | Phase 6, Phase 9 | Safety/security gate documents dump handling, consent, redaction, and transport expectations. |
| CL-012 | security | Network credentials are stored in persistent config without visible encryption-at-rest. | `src/persistent_stores/store_instances/config_store/store_definition.hpp`, `src/persistent_stores/storage_drivers/eeprom_storage.cpp` | preserve-temporarily | Phase 7, Phase 11 | Storage parity records physical-access assumption and avoids exporting credential regions. |
| CL-013 | security | TLS config compiles legacy SHA-1 and MD5 modules although runtime ciphersuite is modern. | `include/mbedtls/cipher_config_ece.h`, `src/connect/tls/tls.cpp` | fix-during-rewrite | Phase 9 | TLS fixture rejects weak signatures or documents required compatibility exception. |
| CL-014 | security | Generic production RNG can fall back to deterministic software LCG after hardware RNG failure. | `src/common/random_hw.cpp`, `src/connect/tls/hardware_rng.cpp` | fix-during-rewrite | Phase 6, Phase 9 | Crypto callers use secure entropy only; non-crypto random fallback is named and tested. |
| CL-015 | security | Fixture keys exist in vendored/test trees and must not be mistaken for production secrets. | `lib/Middlewares/Third_Party/mbedtls/tests/data_files/`, `tests/module/Connect/test-server/tls/` | preserve-temporarily | Phase 9, Phase 11 | Packaging/release checks exclude test fixture keys; docs label them non-production. |
| CL-016 | performance | LwIP packet ordering workaround limits throughput. | `include/buddy/lwipopts.h` | preserve-temporarily | Phase 9 | Network parity preserves current behavior unless BFW-2357 root cause is fixed with tests. |
| CL-017 | performance | TLS handshake is CPU and memory sensitive on constrained pools. | `src/connect/tls/tls.cpp`, `include/mbedtls/cipher_config_ece.h` | preserve-temporarily | Phase 9 | Connect parity captures handshake latency/memory expectations under load. |
| CL-018 | performance | Connect response parsing uses bounded whole-response buffers. | `src/connect/connect.cpp`, `src/connect/command.cpp`, `src/connect/render.cpp` | preserve-temporarily | Phase 9 | Protocol fixtures include large response and command-buffer behavior. |
| CL-019 | generated-assets | Generated font headers dominate source size and build/review churn. | `src/gui/res/cc/*.hpp`, `utils/translations_and_fonts/README_TRANSLATIONS.md` | defer | Phase 7 or v2 | Resource parity accepts current tracked headers unless binary asset strategy is approved. |
| CL-020 | fragile-area | Partial-file transfer bypasses filesystem allocation state and has media races. | `src/transfers/partial_file.cpp`, `src/transfers/transfer.cpp` | fix-during-rewrite | Phase 9 | Transfer fixtures cover unplug/replug, delete/recreate, and non-contiguous file cases. |
| CL-021 | fragile-area | Transfer monitor exposes lock-order deadlocks as API rules. | `src/transfers/monitor.hpp`, `src/transfers/monitor.cpp` | fix-during-rewrite | Phase 9 | Rust transfer model prevents invalid lock ordering or tests snapshot-only API behavior. |
| CL-022 | fragile-area | Connect planner/background command state uses asserts and shared buffers. | `src/connect/planner.cpp`, `src/connect/background.cpp`, `src/connect/printer.hpp` | fix-during-rewrite | Phase 9 | Duplicate-command and long-G-code fixtures cover background command ownership. |
| CL-023 | fragile-area | Persistent config schema is collision-sensitive and migration-heavy. | `src/persistent_stores/store_instances/config_store/store_definition.hpp`, `utils/persistent_stores/journal_hashes_generator.py` | preserve-temporarily | Phase 7 | Migration/hash fixtures prove deprecated IDs and duplicates are handled intentionally. |
| CL-024 | fragile-area | STM32G0 already-enabled interrupt configuration path is unimplemented. | `src/common/Pin.cpp` | fix-during-rewrite | Phase 5, Phase 6 | Hardware/simulator evidence covers repeated IRQ configuration or makes it unrepresentable. |
| CL-025 | scaling | Aggregate struct visitor hard-caps generated arity below 256 fields. | `include/common/visit_all_struct_fields.hpp`, `utils/persistent_stores/visit_all_struct_fields_generator.py` | preserve-temporarily | Phase 7 | Persistence rewrite records schema arity and generator replacement decision. |
| CL-026 | scaling | Persistent journal hash space uses 14-bit IDs and collision risk grows. | `utils/persistent_stores/journal_hashes_generator.py`, `src/persistent_stores/journal/store.hpp` | preserve-temporarily | Phase 7 | Hash collision drift checks remain active and wider-ID migration is explicit if needed. |
| CL-027 | scaling | Transfer subsystem supports a single active transfer slot. | `src/transfers/` | preserve-temporarily | Phase 9 | Transfer parity fixtures preserve single-slot behavior unless v2 redesign is approved. |

## Verification Expectations

- Every concern above must retain one allowed disposition value.
- Later subsystem phases should cite the relevant `CL-*` entries in plan must-haves or verification notes.
- Fixing any current defect requires an intentional-delta test or safety evidence; no silent fixes.
- Deferred items remain out of v1 unless promoted by roadmap update.
