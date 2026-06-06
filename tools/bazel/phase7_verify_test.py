#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase7_verify.py"

PHASE = "07-persistence-storage-and-resource-compatibility"
PHASE_LIFECYCLE_ID = "7-2026-06-06T04-24-25"
PHASE_DIR = ".planning/phases/07-persistence-storage-and-resource-compatibility"

OLD_EEPROM_VERSIONS = ["v4", "v6", "v7", "v9", "v10", "v11", "v12", "v22", "v32787", "v32789"]
MIGRATION_ROW_IDS = [f"old-eeprom-{version}-migration" for version in OLD_EEPROM_VERSIONS]
REQUIRED_CATALOG_ROW_IDS = [
    *MIGRATION_ROW_IDS,
    "current-schema-v5",
    "settings-import-export",
    "credential-redaction",
    "selftest-calibration-state",
    "journal-hash-facts",
]

REQUIRED_STORAGE_ROW_IDS = [
    "storage-driver-eeprom",
    "filesystem-usb-fatfs",
    "filesystem-internal-littlefs",
    "filesystem-bbf-littlefs",
    "filesystem-semihosting",
    "filesystem-root-listing",
    "libsysbase-devoptab-dispatch",
    "block-device-test-randomness",
]

REQUIRED_RESOURCE_ROW_IDS = [
    "resource-standard-image",
    "resource-bootloader-image",
    "resource-esp32-blobs",
    "resource-esp8266-blobs",
    "resource-wui-static-assets",
    "resource-qoi-data",
    "resource-language-packs",
    "resource-font-assets",
    "resource-mmu-firmware",
    "resource-hash-and-revision",
    "resource-runtime-bootstrap",
]

REQUIRED_GENERATED_LABELS = [
    "generated_product_profiles",
    "generated_option_data",
    "generated_resources",
    "generated_translations",
    "generated_fonts",
    "generated_wui_assets",
    "generated_esp_blobs",
    "generated_puppy_descriptors",
    "generated_mmu_descriptors",
    "generated_package_metadata",
    "tracked_generated_outputs",
]

GENERATED_ROW_IDS_BY_LABEL = {
    "generated_product_profiles": "product-profiles",
    "generated_option_data": "option-data",
    "generated_resources": "resource-assets",
    "generated_translations": "translation-pot",
    "generated_fonts": "font-assets",
    "generated_wui_assets": "wui-assets",
    "generated_esp_blobs": "esp-blobs",
    "generated_puppy_descriptors": "puppy-descriptors",
    "generated_mmu_descriptors": "mmu-descriptors",
    "generated_package_metadata": "package-metadata",
    "tracked_generated_outputs": "tracked-generated-outputs",
}

REQUIRED_CONCERN_ROW_IDS = [
    "concern-generated-file-drift",
    "concern-translation-font-shell-safety",
    "concern-unencrypted-credential-storage",
    "concern-config-schema-hash-fragility",
    "concern-journal-hash-space-limit",
    "concern-block-device-randomness",
    "concern-littlefs-python-dependency-drift",
    "concern-tracked-font-header-churn",
]

REQUIRED_CONCERN_IDS = [
    "phase7-generated-file-drift",
    "phase7-unsafe-translation-font-shell-scripts",
    "phase7-unencrypted-credential-storage",
    "phase7-config-schema-hash-fragility",
    "phase7-journal-hash-space-limit",
    "phase7-block-device-randomness",
    "phase7-littlefs-python-dependency-drift",
    "phase7-tracked-font-header-churn",
]


class Phase7VerifierTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
        maybe_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase7_verify.py"
        return subprocess.run(
            [sys.executable, verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=maybe_env,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel").mkdir(parents=True)
        shutil.copy2(VERIFIER, root / "tools/bazel/phase7_verify.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def write_source_paths(self, root: Path, paths: list[str]) -> None:
        for source_path in paths:
            if source_path.endswith("/"):
                (root / source_path).mkdir(parents=True, exist_ok=True)
                continue

            self.write_file(root, source_path, "// reference source")

    def write_config_manifest(
        self,
        root: Path,
        lifecycle_id: str = PHASE_LIFECYCLE_ID,
        extra_note: str = "",
    ) -> None:
        source_paths = [
            "src/persistent_stores/store_instances/config_store/store_definition.hpp",
            "src/persistent_stores/store_instances/config_store/store_definition.cpp",
            "src/persistent_stores/store_instances/config_store/defaults.hpp",
            "src/persistent_stores/store_instances/config_store/migrations.cpp",
            "src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp",
            "utils/persistent_stores/journal_hashes_generator.py",
            "include/common/visit_all_struct_fields.hpp",
        ]
        self.write_source_paths(root, source_paths)
        rows = [
            "current-config-store-schema-v5",
            "current-config-items-and-defaults",
            "deprecated-store-hashed-ids",
            "old-eeprom-version-chain",
            "old-eeprom-last-migration",
            "config-store-runtime-migrations",
            "credential-bearing-config-keys",
            "settings-import-export-keys",
            "selftest-calibration-state",
            "journal-hash-generation",
            "journal-backend-crc-bank-selection",
            "generated-struct-reflection",
        ]
        required_text = (
            "CurrentStore::newest_config_version = 5 WIFI AP Password Connect Token "
            "name-only-redacted DeprecatedStore selftest-calibration-state Selftest Result "
            "selftest_result calibration selftest 0x3FFF current v4 v6 v7 v9 v10 v11 v12 "
            "v22 v32787 v32789"
        )
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": lifecycle_id,
            "config_contracts": [
                {
                    "id": row_id,
                    "requirement": "IFCE-04",
                    "source_paths": source_paths,
                    "reference_surface": f"{row_id} {required_text}",
                    "rust_surface": f"Rust storage surface for {row_id}",
                    "evidence_class": "source-audit",
                    "proof_scope": "source-audit",
                    "credential_policy": "name-only-redacted",
                    "intentional_delta": "none",
                    "notes": f"{required_text} {extra_note}",
                }
                for row_id in rows
            ],
        }
        self.write_file(root, "tools/bazel/manifests/phase7_config_store.json", json.dumps(manifest))

    def write_migration_catalog(
        self,
        root: Path,
        maybe_rows: list[str] | None = None,
        extra_note: str = "",
    ) -> None:
        source_paths = [
            "src/persistent_stores/store_instances/config_store/store_definition.hpp",
            "src/persistent_stores/store_instances/config_store/old_eeprom/last_migration.cpp",
            "src/common/selftest_result.hpp",
            "utils/persistent_stores/journal_hashes_generator.py",
        ]
        self.write_source_paths(root, source_paths)
        row_ids = maybe_rows or REQUIRED_CATALOG_ROW_IDS
        required_text = (
            "Selftest Result selftest_result calibration selftest "
            "CurrentStore::newest_config_version = 5 journal::hash 0x3FFF duplicate detection "
            "synthetic-redacted name-only-redacted byte_material_policy"
        )
        catalog = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "catalog_id": "phase7-redacted-storage-migration-catalog",
            "fixtures": [
                {
                    "id": row_id,
                    "requirement": "IFCE-04",
                    "source_paths": source_paths,
                    "fixture_identity": f"synthetic {row_id} fixture identity",
                    "reference_surface": f"{row_id} {required_text}",
                    "rust_surface": f"Rust fixture surface for {row_id}",
                    "evidence_class": "source-audit",
                    "proof_scope": "source-audit",
                    "redaction_policy": "synthetic-redacted",
                    "credential_policy": "name-only-redacted",
                    "byte_material_policy": "none",
                    "intentional_delta": "none",
                    "notes": f"{required_text} {extra_note}",
                }
                for row_id in row_ids
            ],
        }
        self.write_file(
            root,
            "tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json",
            json.dumps(catalog),
        )

    def write_storage_manifest(
        self,
        root: Path,
        maybe_evidence_class: str | None = None,
    ) -> None:
        source_paths = [
            "src/persistent_stores/storage_drivers/eeprom_storage.cpp",
            "src/buddy/filesystem.cpp",
            "src/buddy/filesystem_fatfs.cpp",
            "src/buddy/filesystem_littlefs_internal.cpp",
            "src/buddy/filesystem_littlefs_bbf.cpp",
            "src/buddy/filesystem_semihosting.cpp",
            "src/buddy/filesystem_root.cpp",
            "lib/libsysbase/iosupport.c",
            "tests/blockdevice/test_block_device.py",
        ]
        self.write_source_paths(root, source_paths)
        runtime_paths = [
            "EEPROM/internal flash",
            "/usb",
            "/internal",
            "/bbf",
            "/semihosting",
            "/",
            "POSIX-like devoptab",
            "tests/blockdevice",
        ]
        rows = []
        for index, row_id in enumerate(REQUIRED_STORAGE_ROW_IDS):
            evidence_class = maybe_evidence_class or ("manual-hardware-required" if index in {1, 4} else "source-audit")
            rows.append(
                {
                    "id": row_id,
                    "requirement": "IFCE-04",
                    "source_paths": source_paths,
                    "mount_name": row_id,
                    "runtime_path": runtime_paths[index],
                    "reference_surface": f"{row_id} {runtime_paths[index]}",
                    "rust_surface": f"Rust storage media surface for {row_id}",
                    "evidence_class": evidence_class,
                    "proof_scope": "source-audit",
                    "non_local_evidence": "manual-hardware-required"
                    if index in {1, 4}
                    else "not-applicable",
                    "notes": "storage media row",
                }
            )
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "storage_surfaces": rows,
        }
        self.write_file(root, "tools/bazel/manifests/phase7_storage_media.json", json.dumps(manifest))

    def write_resources_manifest(self, root: Path) -> None:
        source_paths = [
            "src/resources/CMakeLists.txt",
            "cmake/Littlefs.cmake",
            "utils/mklittlefs.py",
            "utils/resources/generate_hash_file.py",
            "src/lang/CMakeLists.txt",
            "utils/translations_and_fonts/lang.py",
        ]
        self.write_source_paths(root, source_paths)
        rows = [
            {
                "id": row_id,
                "requirement": "IFCE-05",
                "source_paths": source_paths,
                "declared_inputs": ["declared input"],
                "runtime_paths": ["/web/index.html", "/esp/uart_wifi.bin", "qoi.data"],
                "reference_surface": f"reference resource surface {row_id}",
                "rust_surface": f"ResourceSurface::{row_id}",
                "evidence_class": "source-audit",
                "proof_scope": "semantic-resource-contract",
                "generated_label": "//tools/bazel:generated_resources_check",
                "notes": "resource manifest row",
            }
            for row_id in REQUIRED_RESOURCE_ROW_IDS
        ]
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "resource_surfaces": rows,
        }
        self.write_file(root, "tools/bazel/manifests/phase7_resources.json", json.dumps(manifest))

    def write_generated_outputs_manifest(
        self,
        root: Path,
        maybe_labels: list[str] | None = None,
    ) -> None:
        labels = maybe_labels or REQUIRED_GENERATED_LABELS
        source_paths = ["tools/bazel/generated_drift.py", "tools/bazel/BUILD.bazel"]
        self.write_source_paths(root, source_paths)
        rows = [
            {
                "id": GENERATED_ROW_IDS_BY_LABEL[label],
                "requirement": "IFCE-05",
                "ownership": "tracked-reviewed-source",
                "tracked_outputs": ["tracked-output"],
                "declared_sources": source_paths,
                "check_label": f"//tools/bazel:{label}_check",
                "update_label": f"//tools/bazel:{label}_update",
                "evidence_class": "manifest-check",
                "writes_source_tree": True,
                "proof_scope": "phase3-label-wiring-check",
                "notes": f"{label} generated output row",
            }
            for label in labels
        ]
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "generated_surfaces": rows,
        }
        self.write_file(
            root,
            "tools/bazel/manifests/phase7_generated_outputs.json",
            json.dumps(manifest),
        )

    def write_concern_manifest(self, root: Path) -> None:
        source_paths = [".planning/codebase/CONCERNS.md"]
        self.write_source_paths(root, source_paths)
        rows = []
        for row_id, concern_id in zip(REQUIRED_CONCERN_ROW_IDS, REQUIRED_CONCERN_IDS):
            rows.append(
                {
                    "id": row_id,
                    "concern_id": concern_id,
                    "requirement": "IFCE-05" if "font" in row_id or "generated" in row_id else "IFCE-04",
                    "source_paths": source_paths,
                    "disposition": "preserve-with-explicit-risk",
                    "phase7_handling": f"preserve-with-explicit-risk handling for {concern_id}",
                    "evidence_class": "source-audit",
                    "intentional_delta": "none",
                    "regression_guard": f"regression guard for {concern_id}",
                }
            )
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "concerns": rows,
        }
        self.write_file(
            root,
            "tools/bazel/manifests/phase7_concern_dispositions.json",
            json.dumps(manifest),
        )

    def write_rust_api_surface(
        self,
        root: Path,
        storage_text: str | None = None,
        resource_text: str | None = None,
        lib_text: str | None = None,
    ) -> None:
        self.write_file(root, "rust/crates/domain/src/lib.rs", lib_text or "#![forbid(unsafe_code)]\npub mod storage;\npub mod resource;\n")
        self.write_file(
            root,
            "rust/crates/domain/src/storage.rs",
            storage_text
            or "\n".join(
                [
                    "pub struct ReferenceHashName;",
                    "pub struct JournalHashFact;",
                    "pub enum CredentialRedactionPolicy {}",
                    "pub enum EvidenceClass {}",
                    "pub enum FilesystemSurface {}",
                    "pub struct StorageCompatibilitySurface;",
                    "pub struct FixtureIdentity;",
                    'const COMMENT_ONLY: &str = "unsafe { unsafe fn";',
                    "// unsafe block should be ignored in comments",
                ]
            ),
        )
        self.write_file(
            root,
            "rust/crates/domain/src/resource.rs",
            resource_text
            or "\n".join(
                [
                    "pub struct ResourceRuntimePath;",
                    "pub enum ResourceSurface {}",
                    "pub enum GeneratedOutputOwnership {}",
                    "pub struct BazelLabel;",
                    "pub struct GeneratedSurface;",
                ]
            ),
        )

    def write_facade_files(self, root: Path) -> None:
        self.write_file(root, "BUILD.bazel", "phase7_verify\nphase7_verify_tests\n")
        self.write_file(
            root,
            "tools/bazel/BUILD.bazel",
            "\n".join(
                [
                    "phase7_verify",
                    "phase7_verify_tests",
                    "phase7_verify.py",
                    "phase7_verify_test.py",
                    "phase7_config_store.json",
                    "phase7_storage_media.json",
                    "phase7_resources.json",
                    "phase7_generated_outputs.json",
                    "phase7_concern_dispositions.json",
                    "redacted_migration_catalog.json",
                ]
            ),
        )
        self.write_file(
            root,
            "tools/bazel/rust_workflow.sh",
            "\n".join(
                [
                    'case "$command_name" in',
                    "  phase7_verify)",
                    "    python3 tools/bazel/phase7_verify.py --all",
                    "    ;;",
                    "  phase7_verify_tests)",
                    "    python3 tools/bazel/phase7_verify_test.py",
                    "    ;;",
                    "esac",
                    "",
                ]
            ),
        )
        self.write_file(
            root,
            "justfile",
            "phase7-verify:\n    bazel run //tools/bazel:phase7_verify_tests\n    bazel run //tools/bazel:phase7_verify\n",
        )

    def write_phase7_quick_surface(self, root: Path) -> None:
        self.write_config_manifest(root)
        self.write_migration_catalog(root)
        self.write_storage_manifest(root)
        self.write_resources_manifest(root)
        self.write_generated_outputs_manifest(root)
        self.write_concern_manifest(root)
        self.write_rust_api_surface(root)
        self.write_facade_files(root)
        self.write_file(
            root,
            f"{PHASE_DIR}/07-VALIDATION.md",
            "Quick run command\npython3 tools/bazel/phase7_verify.py --quick\nFull suite command\njust phase7-verify\n",
        )

    def test_help_lists_phase7_modes(self) -> None:
        # Act
        result = self.run_verifier(["--help"])

        # Assert
        self.assertEqual(result.returncode, 0, msg=result.stdout)
        for flag in [
            "--quick",
            "--all",
            "--manifests-only",
            "--config-only",
            "--storage-only",
            "--resources-only",
            "--generated-only",
            "--concerns-only",
            "--rust-only",
        ]:
            self.assertIn(flag, result.stdout)

    def test_manifests_only_reports_missing_config_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file: tools/bazel/manifests/phase7_config_store.json", result.stdout)

    def test_quick_rejects_invalid_phase_lifecycle_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_config_manifest(root, lifecycle_id="wrong-lifecycle-id")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase_lifecycle_id", result.stdout)

    def test_quick_rejects_unredacted_credential_material(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_config_manifest(root, extra_note="password_value BEGIN PRIVATE KEY")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("credential", result.stdout)
        self.assertIn("password_value", result.stdout)

    def test_quick_rejects_migration_catalog_missing_selftest_and_hash_coverage(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            missing_rows = [
                row_id
                for row_id in REQUIRED_CATALOG_ROW_IDS
                if row_id not in {"old-eeprom-v4-migration", "selftest-calibration-state", "journal-hash-facts"}
            ]
            self.write_migration_catalog(root, maybe_rows=missing_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("selftest-calibration-state", result.stdout)
        self.assertIn("Selftest Result", result.stdout)
        self.assertIn("old-eeprom-v4-migration", result.stdout)
        self.assertIn("journal-hash-facts", result.stdout)

    def test_quick_rejects_migration_catalog_byte_material(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_migration_catalog(root, extra_note="raw_eeprom byte_array eeprom_bytes token_value")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("raw_eeprom", result.stdout)
        self.assertIn("byte material", result.stdout)

    def test_quick_rejects_local_hardware_storage_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_storage_manifest(root, maybe_evidence_class="hardware verified locally")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware verified locally", result.stdout)

    def test_quick_rejects_missing_generated_resource_check_label(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            labels = [label for label in REQUIRED_GENERATED_LABELS if label != "generated_resources"]
            self.write_generated_outputs_manifest(root, maybe_labels=labels)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated_resources_check", result.stdout)

    def test_quick_rejects_missing_storage_rust_api_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_rust_api_surface(root, storage_text="pub struct JournalHashFact;\n")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rust/crates/domain/src/storage.rs", result.stdout)
        self.assertIn("ReferenceHashName", result.stdout)
        self.assertIn("CredentialRedactionPolicy", result.stdout)

    def test_quick_rejects_missing_resource_rust_api_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_rust_api_surface(root, resource_text="pub struct ResourceRuntimePath;\n")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rust/crates/domain/src/resource.rs", result.stdout)
        self.assertIn("ResourceSurface", result.stdout)
        self.assertIn("GeneratedOutputOwnership", result.stdout)

    def test_quick_rejects_unsafe_in_phase7_domain_modules(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_rust_api_surface(
                root,
                storage_text="\n".join(
                    [
                        "pub struct ReferenceHashName;",
                        "pub struct JournalHashFact;",
                        "pub enum CredentialRedactionPolicy {}",
                        "pub enum EvidenceClass {}",
                        "pub enum FilesystemSurface {}",
                        "pub struct StorageCompatibilitySurface;",
                        "pub struct FixtureIdentity;",
                        'const COMMENT_ONLY: &str = "unsafe { unsafe fn";',
                        "// unsafe trait should be ignored in comments",
                        "pub fn trigger() { unsafe { core::arch::asm!(\"nop\"); } }",
                    ]
                ),
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe block", result.stdout)

    def test_quick_rejects_release_scope_overclaim_in_summary(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            self.write_file(root, f"{PHASE_DIR}/07-99-SUMMARY.md", "byte-for-byte firmware parity\n")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("byte-for-byte firmware parity", result.stdout)

    def test_all_runs_quick_checks_and_cargo_verification(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            cargo_log = root / "cargo.log"
            cargo = bin_dir / "cargo"
            cargo.write_text(
                "#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> \"$PWD/cargo.log\"\n",
                encoding="utf-8",
            )
            cargo.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"

            # Act
            result = self.run_verifier(["--all"], maybe_root=root, maybe_env=env)

            # Assert
            self.assertEqual(result.returncode, 0, msg=result.stdout)
            self.assertEqual(
                cargo_log.read_text(encoding="utf-8").splitlines(),
                [
                    "fmt --all -- --check",
                    "clippy --all-targets --all-features -- -D warnings",
                    "build --all-targets --all-features",
                    "test --all-features",
                ],
            )


if __name__ == "__main__":
    unittest.main()
