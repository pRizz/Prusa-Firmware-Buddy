#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase10_verify_test import *  # noqa: F403


class Phase10VerifierFailureTest(Phase10VerifierFixture, unittest.TestCase):

    def test_requires_all_phase10_manifests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            (root /
             "tools/bazel/manifests/phase10_mmu_transport.json").unlink()

            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase10_mmu_transport.json", result.stdout)

    def test_requires_auxiliary_controller_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            rows = [
                row for row in self.manifest_rows(
                    root,
                    "tools/bazel/manifests/phase10_auxiliary_controllers.json",
                ) if row["id"] not in {
                    "aux-controller-family-dwarf",
                    "aux-controller-family-modular-bed",
                    "aux-controller-family-xbuddy-extension",
                    "dwarf-runtime-fifo-loadcell-toolhead",
                    "modular-bed-runtime-bedlet-faults",
                    "xbuddy-extension-runtime-h503-special",
                    "aux-runtime-state-contract",
                }
            ]
            self.write_manifest_rows(
                root,
                "tools/bazel/manifests/phase10_auxiliary_controllers.json",
                rows,
            )

            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for row_id in REQUIRED_AUXILIARY_CONTROLLER_ROW_IDS:
            self.assertIn(row_id, result.stdout)

    def test_requires_mmu_transport_and_concern_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            mmu_rows = [
                row for row in self.manifest_rows(
                    root, "tools/bazel/manifests/phase10_mmu_transport.json")
                if row["id"] not in {
                    "mmu2-availability-reporting-stub",
                    "mmu2-usemmu-config-runtime-state",
                    "mmu2-bootloader-update-manager",
                    "mmu2-uart-transport",
                    "mmu2-puppy-modbus-bridge",
                    "mmu-firmware-runtime-resource",
                }
            ]
            concern_rows = [
                row for row in self.manifest_rows(
                    root,
                    "tools/bazel/manifests/phase10_concern_dispositions.json",
                ) if row["id"] not in REQUIRED_CONCERN_ROW_IDS
            ]
            self.write_manifest_rows(
                root, "tools/bazel/manifests/phase10_mmu_transport.json",
                mmu_rows)
            self.write_manifest_rows(
                root,
                "tools/bazel/manifests/phase10_concern_dispositions.json",
                concern_rows,
            )

            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for row_id in [*REQUIRED_MMU_ROW_IDS, *REQUIRED_CONCERN_ROW_IDS]:
            self.assertIn(row_id, result.stdout)

    def test_rejects_mmu_manifest_state_not_accepted_by_rust_parser(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            auxiliary_path = root / "rust/crates/domain/src/auxiliary/transport.rs"
            auxiliary_text = auxiliary_path.read_text(encoding="utf-8")
            auxiliary_text = auxiliary_text.replace(
                '            "active" => Ok(Self::Active),\n', "")
            auxiliary_path.write_text(auxiliary_text, encoding="utf-8")

            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mmu_transport_state 'active'", result.stdout)
        self.assertIn("MmuTransportState::parse", result.stdout)

    def test_ignores_commented_mmu_parser_arms(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            auxiliary_path = root / "rust/crates/domain/src/auxiliary/transport.rs"
            auxiliary_text = auxiliary_path.read_text(encoding="utf-8")
            auxiliary_text = auxiliary_text.replace(
                '            "active" => Ok(Self::Active),\n',
                '            // "active" => Ok(Self::Active),\n',
            )
            auxiliary_path.write_text(auxiliary_text, encoding="utf-8")

            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mmu_transport_state 'active'", result.stdout)
        self.assertIn("MmuTransportState::parse", result.stdout)

    def test_requires_modbus_toolchanger_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            modbus_rows = [
                row for row in self.manifest_rows(
                    root, "tools/bazel/manifests/phase10_modbus_rs485.json")
                if row["id"] not in REQUIRED_MODBUS_ROW_IDS
            ]
            toolchanger_rows = [
                row for row in self.manifest_rows(
                    root,
                    "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json",
                ) if row["id"] not in REQUIRED_TOOLCHANGER_ROW_IDS
            ]
            self.write_manifest_rows(
                root,
                "tools/bazel/manifests/phase10_modbus_rs485.json",
                modbus_rows,
            )
            self.write_manifest_rows(
                root,
                "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json",
                toolchanger_rows,
            )

            # Act
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for row_id in [
                *REQUIRED_MODBUS_ROW_IDS, *REQUIRED_TOOLCHANGER_ROW_IDS
        ]:
            self.assertIn(row_id, result.stdout)

    def test_requires_build_update_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            rows = [
                row for row in self.manifest_rows(
                    root,
                    "tools/bazel/manifests/phase10_auxiliary_build_update.json",
                ) if row["id"] not in REQUIRED_BUILD_UPDATE_ROW_IDS
            ]
            self.write_manifest_rows(
                root,
                "tools/bazel/manifests/phase10_auxiliary_build_update.json",
                rows,
            )

            # Act
            result = self.run_verifier(["--package-update-only"],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for row_id in REQUIRED_BUILD_UPDATE_ROW_IDS:
            self.assertIn(row_id, result.stdout)

    def test_rejects_payload_and_secret_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            self.write_validation_contract(
                root, extra_text=" ".join(FORBIDDEN_MARKERS))

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("firmware_payload", result.stdout)
        self.assertIn("SIGNING_KEY_VALUE", result.stdout)
        self.assertIn("BEGIN PRIVATE KEY", result.stdout)

    def test_rejects_non_local_evidence_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            rows = self.manifest_rows(
                root, "tools/bazel/manifests/phase10_modbus_rs485.json")
            for row in rows:
                if row["id"] == "puppy-rs485-flow-control":
                    row["proof_scope"] = "local"
                    row["evidence_class"] = "hardware-smoke"
            self.write_manifest_rows(
                root,
                "tools/bazel/manifests/phase10_modbus_rs485.json",
                rows,
            )
            self.write_validation_contract(
                root, extra_text=" ".join(OVERCLAIM_STRINGS))

            # Act
            result = self.run_verifier(["--evidence-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("puppy-rs485-flow-control", result.stdout)
        self.assertIn("hardware-smoke", result.stdout)
        self.assertIn("RS485 hardware verified locally", result.stdout)
        self.assertIn("cutover evidence complete", result.stdout)

    def test_requires_auxiliary_rust_api_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            self.write_rust_api_surface(
                root,
                auxiliary_text="pub enum AuxiliaryControllerKind {}\n",
                lib_text=
                "#![forbid(unsafe_code)]\npub mod auxiliary;\npub use auxiliary::AuxiliaryControllerKind;\n",
            )

            # Act
            result = self.run_verifier(["--rust-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for needle in [
                "AuxiliaryRuntimeState",
                "FirmwareImageSource",
                "MmuTransportState",
                "MmuTransportSurface",
                "AuxiliaryParityContract",
                "AuxiliaryControllerContract",
        ]:
            self.assertIn(needle, result.stdout)

    def test_requires_package_update_mode(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            rows = self.manifest_rows(
                root,
                "tools/bazel/manifests/phase10_auxiliary_build_update.json",
            )
            for row in rows:
                row["runtime_paths"] = []
                row["prebuilt_path_variables"] = []
                row["descriptor_command"] = "none"
                row["skip_flash_option"] = "none"
                row["update_build_surface"] = "none"
            self.write_manifest_rows(
                root,
                "tools/bazel/manifests/phase10_auxiliary_build_update.json",
                rows,
            )

            # Act
            result = self.run_verifier(["--package-update-only"],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for needle in PACKAGE_UPDATE_STRINGS:
            self.assertIn(needle, result.stdout)

    def test_requires_bazel_and_just_wiring_fixture(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_good_wiring_fixture(root)

            # Act
            passing_result = self.run_verifier(
                ["--wiring-only", "--repo-root",
                 root.as_posix()],
                maybe_root=root,
            )

            # Assert
            self.assertEqual(passing_result.returncode, 0,
                             passing_result.stdout)

            # Arrange
            self.write_file(root, "BUILD.bazel",
                            'alias(name = "phase10_verify")\n')
            self.write_file(root, "tools/bazel/BUILD.bazel",
                            'sh_binary(name = "phase10_verify")\n')
            self.write_file(root, "tools/bazel/rust_workflow.sh",
                            'case "$command_name" in esac\n')
            self.write_file(
                root, "justfile",
                "phase10:\n    bazel run //tools/bazel:phase10_verify\n")

            # Act
            failing_result = self.run_verifier(
                ["--wiring-only", "--repo-root",
                 root.as_posix()],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(failing_result.returncode, 0)
        self.assertIn("phase10_verify_tests", failing_result.stdout)
        self.assertIn("phase10_auxiliary_controller_docs",
                      failing_result.stdout)
        self.assertIn("phase10_auxiliary_build_update_manifest",
                      failing_result.stdout)
        self.assertIn("phase10-verify:", failing_result.stdout)

    def test_requires_validation_lifecycle_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            self.write_file(
                root,
                f"{PHASE_DIR}/10-VALIDATION.md",
                "\n".join([
                    "---",
                    "phase: 10",
                    "---",
                    "python3 tools/bazel/phase10_verify.py --quick",
                ]),
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE_LIFECYCLE_ID, result.stdout)
        self.assertIn("Wave 0", result.stdout)
        self.assertIn("phase10-verify", result.stdout)
        self.assertIn("manual-hardware-required", result.stdout)
