---
phase: 07-persistence-storage-and-resource-compatibility
reviewed: 2026-06-06T14:37:04Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - rust/crates/domain/src/lib.rs
  - rust/crates/domain/src/resource.rs
  - rust/crates/domain/src/storage.rs
  - tools/bazel/BUILD.bazel
  - tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json
  - tools/bazel/manifests/phase7_concern_dispositions.json
  - tools/bazel/manifests/phase7_config_store.json
  - tools/bazel/manifests/phase7_generated_outputs.json
  - tools/bazel/manifests/phase7_resources.json
  - tools/bazel/manifests/phase7_storage_media.json
  - tools/bazel/phase7_verify.py
  - tools/bazel/phase7_verify_test.py
  - tools/bazel/rust_workflow.sh
findings:
  critical: 0
  warning: 5
  info: 0
  total: 5
status: issues_found
---

# Phase 7: Code Review Report

**Reviewed:** 2026-06-06T14:37:04Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Reviewed the Phase 7 Bazel/just wiring, Python verifier and tests, JSON manifests, and Rust storage/resource domain surfaces. Repo guidance considered: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the pinned Bright Builds architecture, code-shape, verification, testing, and Rust standards. No local project skills were present under `.claude/skills` or `.agents/skills`.

No actual secret value, raw EEPROM byte payload, or critical vulnerability was found in the reviewed files. The warnings below are verifier false-positive/false-negative risks and Rust domain contract gaps that can let Phase 7 appear covered while important compatibility or leakage constraints are not actually enforced.

Verification run during review:

- `python3 tools/bazel/phase7_verify.py --quick` passed
- `python3 tools/bazel/phase7_verify_test.py` passed, 13 tests
- `cargo test -p buddy-domain` passed, 52 tests
- `bazel query '//tools/bazel:phase7_verify + //tools/bazel:phase7_verify_tests + //:phase7_verify + //:phase7_verify_tests'` returned all four labels

## Warnings

### WR-01: Generated-output rows can be wired to the wrong labels and still pass

**File:** `tools/bazel/phase7_verify.py:565`
**Issue:** `check_generated_outputs_manifest()` validates required row IDs and required check/update labels as independent sets. A manifest can swap labels between rows, for example giving `resource-assets` the font update label, and the verifier still passes as long as every required label appears somewhere. That makes generated-surface verification vulnerable to false positives for IFCE-05 label wiring.
**Fix:** Validate the expected check/update labels per row ID, and add a regression test that intentionally swaps two labels.

```python
EXPECTED_GENERATED_LABEL_PREFIX_BY_ROW_ID = {
    "product-profiles": "generated_product_profiles",
    "option-data": "generated_option_data",
    "resource-assets": "generated_resources",
    "translation-pot": "generated_translations",
    "font-assets": "generated_fonts",
    "wui-assets": "generated_wui_assets",
    "esp-blobs": "generated_esp_blobs",
    "puppy-descriptors": "generated_puppy_descriptors",
    "mmu-descriptors": "generated_mmu_descriptors",
    "package-metadata": "generated_package_metadata",
    "tracked-generated-outputs": "tracked_generated_outputs",
}

for row in rows:
    row_id = require_string(row, "id", row_name)
    prefix = EXPECTED_GENERATED_LABEL_PREFIX_BY_ROW_ID[row_id]
    expected_check = f"//tools/bazel:{prefix}_check"
    expected_update = f"//tools/bazel:{prefix}_update"
    if check_label != expected_check or update_label != expected_update:
        raise VerificationError(f"{row_name} has mismatched generated labels")
```

### WR-02: Rust API checks can be satisfied by comments or string literals

**File:** `tools/bazel/phase7_verify.py:698`
**Issue:** `check_rust_api_surface()` checks `#![forbid(unsafe_code)]` and required API names with raw substring searches. `--quick` and `--rust-only` can pass after the actual public domain type is removed if the name remains in a comment, test fixture string, or ordinary string constant. That weakens the Phase 7 Rust domain invariant check.
**Fix:** Search the stripped Rust code returned by `rust_code_without_comments_or_strings()`, and match declarations or re-exports instead of bare names. Add tests proving comments and strings do not satisfy the API surface.

```python
code = rust_code_without_comments_or_strings(text)
required_declarations = [
    r"\bpub\s+struct\s+ReferenceHashName\b",
    r"\bpub\s+struct\s+JournalHashFact\b",
    r"\bpub\s+enum\s+CredentialRedactionPolicy\b",
]
missing = [
    pattern
    for pattern in required_declarations
    if not re.search(pattern, code)
]
```

### WR-03: Secret and raw-byte leakage scanning is too narrow

**File:** `tools/bazel/phase7_verify.py:512`
**Issue:** Secret marker rejection runs only for the config-store manifest and the migration catalog, and it uses exact case-sensitive marker strings. Credential or raw-byte material placed in `phase7_storage_media.json`, `phase7_resources.json`, `phase7_generated_outputs.json`, or `phase7_concern_dispositions.json` is not scanned, and variants such as `PASSWORD_VALUE`, `tokenValue`, `rawEeprom`, or `private_key` can be missed.
**Fix:** Scan every Phase 7 manifest/catalog artifact with case-insensitive denylist patterns that target value material, while still allowing credential key names such as `WIFI AP Password` and `Connect Token`.

```python
SENSITIVE_PATTERNS = [
    re.compile(r"\b(password|token|secret|certificate)[_-]?value\b", re.IGNORECASE),
    re.compile(r"\braw[_-]?eeprom\b", re.IGNORECASE),
    re.compile(r"\beeprom[_-]?bytes\b", re.IGNORECASE),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY", re.IGNORECASE),
]

PHASE7_REDACTION_SCANNED_PATHS = [
    CONFIG_MANIFEST,
    STORAGE_MANIFEST,
    RESOURCES_MANIFEST,
    GENERATED_MANIFEST,
    CONCERN_MANIFEST,
    MIGRATION_CATALOG,
]
```

### WR-04: Bazel and just facade checks only prove substrings exist

**File:** `tools/bazel/phase7_verify.py:715`
**Issue:** `check_bazel_surface()` and `check_just_surface()` use plain substring searches. The Bazel check returns as soon as `phase7_verify` is found and the four needle strings appear anywhere in `tools/bazel/BUILD.bazel`; it does not prove the `shell_binary` targets use `rust_workflow.sh`, include the required data files, have root aliases, or that `rust_workflow.sh` contains matching cases. The justfile check has the same substring weakness for the `phase7-verify` facade. Direct `--quick` verification can therefore pass with broken Bazel/just wiring.
**Fix:** Validate exact target and recipe structure. At minimum, extract the relevant `shell_binary` blocks and `phase7-verify` recipe and assert their required fields; also check root aliases and `rust_workflow.sh` cases. Add tests that remove a data dependency or replace one just command.

```python
phase7_target = extract_bazel_rule(tools_build, "phase7_verify")
require_substrings(
    phase7_target,
    [
        'src = "rust_workflow.sh"',
        '"manifests/phase7_config_store.json"',
        '"manifests/phase7_storage_media.json"',
        '"manifests/phase7_resources.json"',
        '"fixtures/phase7_storage/redacted_migration_catalog.json"',
    ],
)
```

### WR-05: Rust resource surface paths do not match the manifest contract

**File:** `rust/crates/domain/src/resource.rs:3`
**Issue:** `ResourceSurface::required_runtime_paths()` under-represents several Phase 7 resource surfaces compared with `tools/bazel/manifests/phase7_resources.json`. For example, the standard image manifest lists ESP, WUI, QOI, language, and revision paths, but `STANDARD_IMAGE_RUNTIME_PATHS` only lists `qoi.data` and `resources/revision_standard.hpp`. The bootloader domain path list omits `resources/revision_bootloader.hpp` and `bootloader/required_version.hpp`, the ESP8266 list omits `/esp/stub_text.bin` and `/esp/stub_data.bin`, and runtime bootstrap points at `src/resources/bootstrap.cpp` instead of the runtime paths `/internal/res`, `/bbf`, and the revision header. Domain code can therefore claim a resource surface while missing manifest-required paths.
**Fix:** Make the Rust constants mirror the manifest rows, or generate/validate both from a shared source. Add unit tests that compare every `ResourceSurface` path list against the corresponding manifest `runtime_paths`.

```rust
const ESP8266_BLOB_RUNTIME_PATHS: &[&str] = &[
    "/esp/uart_wifi.bin",
    "/esp/bootloader.bin",
    "/esp/partition-table.bin",
    "/esp/stub_text.bin",
    "/esp/stub_data.bin",
];

const RUNTIME_BOOTSTRAP_PATHS: &[&str] = &[
    "/internal/res",
    "/bbf",
    "resources/revision_standard.hpp",
];
```

---

_Reviewed: 2026-06-06T14:37:04Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
