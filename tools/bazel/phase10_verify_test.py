#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase10_verify.py"

PHASE = "10-auxiliary-controllers-and-expansion-ecosystem"
PHASE_LIFECYCLE_ID = "10-2026-06-14T15-08-30"
PHASE_DIR = ".planning/phases/10-auxiliary-controllers-and-expansion-ecosystem"

MANIFESTS = {
    "tools/bazel/manifests/phase10_auxiliary_controllers.json":
    "auxiliary_controller_contracts",
    "tools/bazel/manifests/phase10_mmu_transport.json":
    "mmu_transport_contracts",
    "tools/bazel/manifests/phase10_modbus_rs485.json":
    "modbus_rs485_contracts",
    "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json":
    "toolchanger_dock_offset_contracts",
    "tools/bazel/manifests/phase10_auxiliary_build_update.json":
    "auxiliary_build_update_contracts",
    "tools/bazel/manifests/phase10_concern_dispositions.json": "concerns",
}

REQUIRED_AUXILIARY_CONTROLLER_ROW_IDS = [
    "aux-controller-family-dwarf",
    "aux-controller-family-modular-bed",
    "aux-controller-family-xbuddy-extension",
    "dwarf-runtime-fifo-loadcell-toolhead",
    "modular-bed-runtime-bedlet-faults",
    "xbuddy-extension-runtime-h503-special",
    "aux-runtime-state-contract",
]

REQUIRED_MMU_ROW_IDS = [
    "mmu2-availability-reporting-stub",
    "mmu2-usemmu-config-runtime-state",
    "mmu2-bootloader-update-manager",
    "mmu2-uart-transport",
    "mmu2-puppy-modbus-bridge",
    "mmu-firmware-runtime-resource",
]

REQUIRED_MODBUS_ROW_IDS = [
    "lightmodbus-retained-dependency",
    "puppy-modbus-master-request-retry-timeout",
    "puppy-rs485-flow-control",
    "puppy-modbus-register-block-limits",
    "xbuddy-extension-mmu-read-write-query-command",
    "xbuddy-extension-mmu-speculative-accepted",
    "xbuddy-extension-mmu-response-timeout-window",
]

REQUIRED_TOOLCHANGER_ROW_IDS = [
    "toolchanger-dwarf-update-loop",
    "toolchanger-dock-identity-dwarf1-6",
    "toolchanger-dock-identity-modular-bed-xbe",
    "toolchanger-dock-settings-ui",
    "tool-offset-nozzle-settings-ui",
    "tool-offset-selftest-flow",
]

REQUIRED_BUILD_UPDATE_ROW_IDS = [
    "aux-build-dwarf-external-project",
    "aux-build-modularbed-external-project",
    "aux-build-xbuddy-extension-external-project",
    "aux-firmware-descriptor-generation",
    "aux-puppy-resource-runtime-paths",
    "mmu-firmware-resource-conversion",
    "prebuilt-binary-paths-dwarf-modularbed-xbe",
    "puppy-skip-flash-mode",
    "startup-flashing-bootloader-gates",
    "puppy-crash-dump-download",
]

REQUIRED_CONCERN_ROW_IDS = [
    "concern-phase10-mmu-availability-reporting",
    "concern-phase10-xbuddy-extension-h503-special",
    "concern-phase10-xbe-mmu-bridge-timing",
    "concern-phase10-buddyheaders-error-codes-coupling",
    "concern-phase10-credential-payload-leakage",
    "concern-phase10-non-local-hardware-proof",
    "concern-phase10-ix-xbuddy-extension-branch",
]

RUST_API_STRINGS = [
    "AuxiliaryControllerKind",
    "AuxiliaryRuntimeState",
    "FirmwareImageSource",
    "AuxiliaryUpdateMode",
    "ModbusUnitIdentity",
    "ModbusRequestKind",
    "BusEvidenceClass",
    "AuxiliaryProofScope",
    "MmuTransportState",
    "MmuTransportSurface",
    "DockIdentity",
    "ToolOffsetAxis",
    "ToolOffsetIdentity",
    "ControllerFaultClass",
    "AuxiliaryParityRowId",
    "AuxiliaryParityContract",
    "AuxiliaryControllerContract",
]

PACKAGE_UPDATE_STRINGS = [
    "DWARF_BINARY_PATH",
    "MODULARBED_BINARY_PATH",
    "XBUDDY_EXTENSION_BINARY_PATH",
    "/puppies/fw-dwarf.bin",
    "/puppies/fw-modularbed.bin",
    "/puppies/fw-xbuddy-extension.bin",
    "/mmu/fw.bin",
    "utils/gen_puppies_descriptor.py",
    "startup-flashing",
    "PUPPY_SKIP_FLASH_FW",
    "mmu-firmware-resource",
    "crash-dump",
]

FORBIDDEN_MARKERS = [
    "firmware_payload",
    "payload_bytes",
    "hex_bytes",
    "credential_value",
    "private_key",
    "SIGNING_KEY_VALUE",
    "raw_crash_dump",
    "crash_dump_payload",
    "BEGIN PRIVATE KEY",
]

OVERCLAIM_STRINGS = [
    "RS485 hardware verified locally",
    "physical toolchanger verified locally",
    "live MMU transport passed",
    "long-run update passed locally",
    "simulator auxiliary flow passed locally",
    "cutover evidence complete",
    "firmware bytes embedded",
    "signing key value recorded",
]


class Phase10VerifierFixture:

    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase10_verify.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel").mkdir(parents=True)
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase10_verify.py")
            shutil.copy2(
                ROOT / "tools/bazel/phase10_contract_policy.py",
                root / "tools/bazel/phase10_contract_policy.py",
            )
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_file(self, root: Path, path: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, full_path)

    def write_source_paths(self, root: Path, source_paths: list[str]) -> None:
        for source_path in source_paths:
            if (root / source_path).exists():
                continue
            if source_path.endswith("/"):
                (root / source_path).mkdir(parents=True, exist_ok=True)
                continue
            self.write_file(root, source_path, "// source-backed fixture")

    def manifest_rows(self, root: Path, path: str) -> list[dict[str, object]]:
        data = json.loads((root / path).read_text(encoding="utf-8"))
        return data[MANIFESTS[path]]

    def write_manifest_rows(
        self,
        root: Path,
        path: str,
        rows: list[dict[str, object]],
    ) -> None:
        data = json.loads((root / path).read_text(encoding="utf-8"))
        data[MANIFESTS[path]] = rows
        self.write_file(root, path, json.dumps(data))

    def copy_phase10_surface(self, root: Path) -> None:
        for manifest_path in MANIFESTS:
            self.copy_file(root, manifest_path)
            rows = self.manifest_rows(root, manifest_path)
            for row in rows:
                reference_sources = row.get("reference_sources")
                if isinstance(reference_sources, list):
                    self.write_source_paths(
                        root, [str(item) for item in reference_sources])

        self.copy_file(root, "rust/crates/domain/src/auxiliary.rs")
        for child_path in sorted(
            (ROOT / "rust/crates/domain/src/auxiliary").glob("*.rs")):
            self.copy_file(
                root,
                child_path.relative_to(ROOT).as_posix(),
            )
        self.copy_file(root, "rust/crates/domain/src/lib.rs")
        self.copy_file(root, f"{PHASE_DIR}/10-VALIDATION.md")

    def write_validation_contract(self,
                                  root: Path,
                                  extra_text: str = "") -> None:
        self.write_file(
            root,
            f"{PHASE_DIR}/10-VALIDATION.md",
            "\n".join([
                "---",
                "phase: 10",
                f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
                "---",
                "Wave 0 Requirements",
                "python3 tools/bazel/phase10_verify.py --quick",
                "python3 tools/bazel/phase10_verify.py --manifests-only",
                "python3 tools/bazel/phase10_verify.py --package-update-only",
                "python3 tools/bazel/phase10_verify.py --evidence-only",
                "just phase10-verify",
                "manual-hardware-required hardware-smoke simulator-flow remain non-local",
                "RS485/Modbus timing manual-only exclusion",
                "Toolchanger dock/tool offset manual-only exclusion",
                "MMU behavior over live transport manual-only exclusion",
                extra_text,
            ]),
        )

    def write_rust_api_surface(
        self,
        root: Path,
        auxiliary_text: str | None = None,
        lib_text: str | None = None,
    ) -> None:
        self.write_file(
            root,
            "rust/crates/domain/src/auxiliary.rs",
            auxiliary_text or "\n".join(f"pub struct {api_string};"
                                        for api_string in RUST_API_STRINGS),
        )
        self.write_file(
            root,
            "rust/crates/domain/src/lib.rs",
            lib_text
            or ("#![forbid(unsafe_code)]\n"
                "pub mod auxiliary;\n"
                "pub use auxiliary::{" + ", ".join(RUST_API_STRINGS) + "};\n"),
        )

    def write_good_wiring_fixture(self, root: Path) -> None:
        self.write_file(
            root,
            "BUILD.bazel",
            "\n".join([
                'alias(name = "phase10_verify", actual = "//tools/bazel:phase10_verify")',
                'alias(name = "phase10_verify_tests", actual = "//tools/bazel:phase10_verify_tests")',
                'filegroup(name = "phase10_auxiliary_controller_docs", srcs = [])',
            ]),
        )
        self.write_file(
            root,
            "tools/bazel/BUILD.bazel",
            "\n".join([
                'sh_binary(name = "phase10_verify", srcs = ["rust_workflow.sh"], data = ["phase10_verify.py", "manifests/phase10_auxiliary_build_update.json"])',
                'sh_binary(name = "phase10_verify_tests", srcs = ["rust_workflow.sh"], data = ["phase10_verify.py", "phase10_verify_test.py"])',
                'filegroup(name = "phase10_auxiliary_build_update_manifest", srcs = ["manifests/phase10_auxiliary_build_update.json"])',
                'filegroup(name = "phase10_auxiliary_controller_docs", srcs = [])',
            ]),
        )
        self.write_file(
            root,
            "tools/bazel/rust_workflow.sh",
            "\n".join([
                'case "$command_name" in',
                "  phase10_verify)",
                "    python3 tools/bazel/phase10_verify.py --all",
                "    ;;",
                "  phase10_verify_tests)",
                "    python3 tools/bazel/phase10_verify_test.py",
                "    ;;",
                "esac",
            ]),
        )
        self.write_file(
            root,
            "justfile",
            "phase10-verify:\n    bazel run //tools/bazel:phase10_verify_tests\n    bazel run //tools/bazel:phase10_verify\n",
        )


class Phase10VerifierTest(Phase10VerifierFixture, unittest.TestCase):

    def test_resolves_auxiliary_api_from_declared_private_children(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase10_surface(root)
            facade_text = (root /
                           "rust/crates/domain/src/auxiliary.rs").read_text(
                               encoding="utf-8")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotIn("impl MmuTransportState", facade_text)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    import phase10_verify_failure_test

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(Phase10VerifierTest)
    suite.addTests(
        loader.loadTestsFromTestCase(
            phase10_verify_failure_test.Phase10VerifierFailureTest))
    result = unittest.TextTestRunner().run(suite)
    raise SystemExit(not result.wasSuccessful())
