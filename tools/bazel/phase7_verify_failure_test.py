#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase7_verify_test import (
    PHASE_DIR,
    REQUIRED_CATALOG_ROW_IDS,
    REQUIRED_GENERATED_LABELS,
    Phase7VerifierFixture,
)


class Phase7VerifierFailureTest(Phase7VerifierFixture, unittest.TestCase):

    def test_manifests_only_reports_missing_config_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "missing required file: tools/bazel/manifests/phase7_config_store.json",
            result.stdout)

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
            self.write_config_manifest(
                root, extra_note="password_value BEGIN PRIVATE KEY")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("credential", result.stdout)
        self.assertIn("password_value", result.stdout)

    def test_quick_rejects_migration_catalog_missing_selftest_and_hash_coverage(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            missing_rows = [
                row_id for row_id in REQUIRED_CATALOG_ROW_IDS
                if row_id not in {
                    "old-eeprom-v4-migration", "selftest-calibration-state",
                    "journal-hash-facts"
                }
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
            self.write_migration_catalog(
                root,
                extra_note="raw_eeprom byte_array eeprom_bytes token_value")

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
            self.write_storage_manifest(
                root, maybe_evidence_class="hardware verified locally")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware verified locally", result.stdout)

    def test_quick_rejects_missing_generated_resource_check_label(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase7_quick_surface(root)
            labels = [
                label for label in REQUIRED_GENERATED_LABELS
                if label != "generated_resources"
            ]
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
            self.write_rust_api_surface(
                root, storage_text="pub struct JournalHashFact;\n")

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
            self.write_rust_api_surface(
                root, resource_text="pub struct ResourceRuntimePath;\n")

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
                storage_text="\n".join([
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
                ]),
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
            self.write_file(root, f"{PHASE_DIR}/07-99-SUMMARY.md",
                            "byte-for-byte firmware parity\n")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("byte-for-byte firmware parity", result.stdout)
