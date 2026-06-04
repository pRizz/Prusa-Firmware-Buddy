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
VERIFIER = ROOT / "tools/bazel/phase6_verify.py"

REQUIRED_PRINTING_ROW_IDS = [
    "print-gcode-routing",
    "print-serial-start-pause-resume-cancel",
    "print-file-start-preview-stream-recovery",
    "print-planner-visible-flow",
    "print-buddy-gmcode-handlers",
]

REQUIRED_PRINTING_SOURCE_PATHS = [
    "lib/Marlin/",
    "lib/AddMarlin.cmake",
    "src/common/marlin_server.cpp",
    "src/common/marlin_client.cpp",
    "src/common/marlin_server_request.hpp",
    "src/common/marlin_client_queue.hpp",
    "src/common/marlin_vars.cpp",
    "src/common/serial_printing.cpp",
    "src/common/gcode/",
    "src/marlin_stubs/gcode.cpp",
]

REQUIRED_SAFETY_ROW_IDS = [
    "thermal-safety-transitions",
    "motion-safe-output-and-emergency-stop",
    "selftest-calibration-crash-recovery",
    "power-panic-recovery",
    "fatal-redscreen-bsod-assert",
    "watchdog-and-crash-dump-boundary",
    "probe-loadcell-classification",
]

REQUIRED_SAFETY_SOURCE_PATHS = [
    "src/common/safe_state.cpp",
    "src/common/feature/safety_timer/",
    "src/common/power_panic.cpp",
    "src/common/crash_dump/",
    "src/common/feature/emergency_stop/",
    "src/common/selftest/",
    "src/common/probe_analysis.cpp",
    "src/common/Pin.cpp",
    "src/common/random_hw.cpp",
    "src/common/wdt.cpp",
    "rust/crates/runtime-adapter/src/panic_boundary.rs",
]

REQUIRED_FEATURE_ROW_IDS = [
    "filament-sensor-gates",
    "tmc-motion-driver-gates",
    "precise-homing-gates",
    "input-shaper-gates",
    "phase-burst-stepping-gates",
    "loadcell-hx717-gates",
    "bed-chamber-door-gates",
    "mmu2-gates",
    "nfc-leds-gates",
    "toolchanger-xbuddy-extension-gates",
]

REQUIRED_FEATURE_GATE_STRINGS = [
    "PRINTERS_WITH_FILAMENT_SENSOR_BINARY",
    "PRINTERS_WITH_FILAMENT_SENSOR_ADC",
    "HAS_SIDE_FSENSOR",
    "HAS_TRINAMIC",
    "HAS_ADC_SIDE_FSENSOR",
    "HAS_TMC_UART",
    "HAS_PRECISE_HOMING",
    "HAS_PRECISE_HOMING_COREXY",
    "HAS_INPUT_SHAPER_CALIBRATION",
    "HAS_PHASE_STEPPING",
    "HAS_PHASE_STEPPING_CALIBRATION",
    "HAS_BURST_STEPPING",
    "HAS_LOADCELL",
    "HAS_LOADCELL_HX717",
    "HAS_LOCAL_BED",
    "HAS_MODULAR_BED",
    "HAS_REMOTE_BED",
    "HAS_CHAMBER_API",
    "HAS_CHAMBER_FILTRATION_API",
    "HAS_DOOR_SENSOR",
    "HAS_MMU2",
    "HAS_MMU2_OVER_UART",
    "HAS_NFC",
    "HAS_LEDS",
    "HAS_SIDE_LEDS",
    "HAS_TOOLCHANGER",
    "HAS_XBUDDY_EXTENSION",
]

REQUIRED_CONCERN_ROW_IDS = [
    "concern-cl-007-probe-analysis",
    "concern-cl-008-home-screen-flash-start",
    "concern-cl-011-crash-dump-handling",
    "concern-cl-014-rng-fallback",
    "concern-cl-024-stm32g0-irq",
    "concern-cl-002-mmu-reporting",
    "concern-tmc-motion-driver-retention",
]

REQUIRED_CONCERN_IDS = [
    "CL-007",
    "CL-008",
    "CL-011",
    "CL-014",
    "CL-024",
    "CL-002",
    "phase6-tmc-motion-driver-retention",
]

PHASE_DIR = ".planning/phases/06-printing-core-safety-and-feature-gates"


class Phase6VerifierTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
        maybe_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase6_verify.py"
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
        shutil.copy2(VERIFIER, root / "tools/bazel/phase6_verify.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def write_source_paths(self, root: Path, paths: list[str]) -> None:
        for source_path in paths:
            if source_path.endswith("/"):
                (root / source_path).mkdir(parents=True, exist_ok=True)
            else:
                self.write_file(root, source_path, "// reference source")

    def write_printing_manifest(
        self,
        root: Path,
        evidence_class: str = "source-audit",
        intentional_delta: str | None = "none",
    ) -> None:
        self.write_source_paths(root, REQUIRED_PRINTING_SOURCE_PATHS)

        rows = [
            {
                "id": row_id,
                "requirement": "CORE-03",
                "source_paths": REQUIRED_PRINTING_SOURCE_PATHS,
                "reference_behavior": f"reference behavior for {row_id}",
                "print_surface": f"print surface for {row_id}",
                "evidence_class": evidence_class,
                "rust_surface": f"buddy-domain::{row_id}",
                "intentional_delta": intentional_delta,
            }
            for row_id in REQUIRED_PRINTING_ROW_IDS
        ]
        manifest = {
            "schema_version": 1,
            "phase": "06-printing-core-safety-and-feature-gates",
            "phase_lifecycle_id": "6-2026-06-04T09-48-48",
            "printing_contracts": rows,
        }
        self.write_file(
            root,
            "tools/bazel/manifests/phase6_printing_core.json",
            json.dumps(manifest),
        )

    def write_safety_manifest(self, root: Path) -> None:
        self.write_source_paths(root, REQUIRED_SAFETY_SOURCE_PATHS)

        rows = [
            {
                "id": row_id,
                "requirement": "CORE-04",
                "source_paths": REQUIRED_SAFETY_SOURCE_PATHS,
                "safety_flow": f"safety flow for {row_id}",
                "preserved_behavior": f"preserved behavior for {row_id}",
                "evidence_class": "manual-hardware-required" if index == 1 else "source-audit",
                "rust_surface": f"rust/crates/domain/src/safety.rs::{row_id}",
                "non_local_evidence": "manual-hardware-required evidence remains required",
            }
            for index, row_id in enumerate(REQUIRED_SAFETY_ROW_IDS)
        ]
        manifest = {
            "schema_version": 1,
            "phase": "06-printing-core-safety-and-feature-gates",
            "phase_lifecycle_id": "6-2026-06-04T09-48-48",
            "safety_gates": rows,
        }
        self.write_file(
            root,
            "tools/bazel/manifests/phase6_safety_gates.json",
            json.dumps(manifest),
        )

    def write_feature_manifest(self, root: Path) -> None:
        source_paths = [
            "ProjectOptions.cmake",
            "utils/presets/presets.json",
            "lib/AddMarlin.cmake",
            "lib/TMCStepper/",
            "lib/AddTMCStepper.cmake",
            "lib/AddMMU2.cmake",
            "src/mmu2/mmu2_reporting.cpp",
            "lib/Prusa-Firmware-MMU/",
            "src/common/probe_analysis.cpp",
            "src/common/selftest/",
            "src/common/safe_state.cpp",
            "src/common/feature/emergency_stop/",
            "src/puppies/",
            "include/puppies/",
            ".planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md",
            ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md",
            "tools/bazel/manifests/phase6_concern_dispositions.json",
        ]
        self.write_source_paths(root, source_paths)

        rows = [
            {
                "id": row_id,
                "requirement": "CORE-05",
                "source_paths": source_paths,
                "gate": f"gate for {row_id}",
                "profile_keys": REQUIRED_FEATURE_GATE_STRINGS,
                "expected_state": f"expected state for {row_id}",
                "evidence_class": "manifest-check",
                "rust_surface": f"rust/crates/domain/src/feature.rs::{row_id}",
            }
            for row_id in REQUIRED_FEATURE_ROW_IDS
        ]
        manifest = {
            "schema_version": 1,
            "phase": "06-printing-core-safety-and-feature-gates",
            "phase_lifecycle_id": "6-2026-06-04T09-48-48",
            "feature_gates": rows,
        }
        self.write_file(
            root,
            "tools/bazel/manifests/phase6_feature_gates.json",
            json.dumps(manifest),
        )

    def write_concern_manifest(self, root: Path) -> None:
        source_paths = [
            "src/common/probe_analysis.cpp",
            "src/common/crash_dump/dump.cpp",
            "src/common/crash_dump/crash_dump_distribute.cpp",
            "src/common/random_hw.cpp",
            "src/connect/tls/hardware_rng.cpp",
            "src/mmu2/mmu2_reporting.cpp",
            "lib/TMCStepper/",
            "lib/AddTMCStepper.cmake",
        ]
        self.write_source_paths(root, source_paths)

        if len(REQUIRED_CONCERN_ROW_IDS) != len(REQUIRED_CONCERN_IDS):
            raise AssertionError("concern row IDs and concern IDs must stay aligned")

        rows = []
        for row_id, concern_id in zip(REQUIRED_CONCERN_ROW_IDS, REQUIRED_CONCERN_IDS):
            rows.append(
                {
                    "id": row_id,
                    "concern_id": concern_id,
                    "requirement": "CORE-04"
                    if concern_id not in {"CL-002", "phase6-tmc-motion-driver-retention"} else "CORE-05",
                    "source_paths": source_paths,
                    "disposition": "preserve-temporarily",
                    "phase6_handling": "preserve-temporarily source handling",
                    "evidence_class": "source-audit",
                    "intentional_delta": "none",
                }
            )
        manifest = {
            "schema_version": 1,
            "phase": "06-printing-core-safety-and-feature-gates",
            "phase_lifecycle_id": "6-2026-06-04T09-48-48",
            "concerns": rows,
        }
        self.write_file(
            root,
            "tools/bazel/manifests/phase6_concern_dispositions.json",
            json.dumps(manifest),
        )

    def write_facade_files(self, root: Path) -> None:
        self.write_file(
            root,
            "BUILD.bazel",
            "phase6_verify\nphase6_verify_tests\nphase6_printing_safety_docs\n",
        )
        self.write_file(
            root,
            "tools/bazel/BUILD.bazel",
            "\n".join(
                [
                    "phase6_verify",
                    "phase6_verify_tests",
                    "phase6_verify.py",
                    "phase6_verify_test.py",
                    "phase6_printing_core.json",
                    "phase6_safety_gates.json",
                    "phase6_feature_gates.json",
                    "phase6_concern_dispositions.json",
                    "//:phase6_printing_safety_docs",
                ]
            ),
        )
        self.write_file(
            root,
            "tools/bazel/rust_workflow.sh",
            "\n".join(
                [
                    'case "$command_name" in',
                    "  phase6_verify)",
                    "    python3 tools/bazel/phase6_verify.py --all",
                    "    ;;",
                    "  phase6_verify_tests)",
                    "    python3 tools/bazel/phase6_verify_test.py",
                    "    ;;",
                    "esac",
                    "",
                ]
            ),
        )
        self.write_file(
            root,
            "justfile",
            "phase6-verify:\n    bazel run //tools/bazel:phase6_verify_tests\n    bazel run //tools/bazel:phase6_verify\n",
        )

    def write_validation_contract(self, root: Path, include_full_suite: bool = True) -> None:
        lines = [
            "Quick run command",
            "python3 tools/bazel/phase6_verify.py --quick",
        ]
        if include_full_suite:
            lines.extend(["Full suite command", "just phase6-verify"])
        self.write_file(root, f"{PHASE_DIR}/06-VALIDATION.md", "\n".join(lines))

    def write_rust_api_surface(
        self,
        root: Path,
        print_text: str | None = None,
        safety_text: str | None = None,
        feature_text: str | None = None,
    ) -> None:
        self.write_file(root, "rust/crates/domain/src/lib.rs", "#![forbid(unsafe_code)]\n")
        self.write_file(
            root,
            "rust/crates/domain/src/print.rs",
            print_text
            or "\n".join(
                [
                    "pub struct FixtureId;",
                    "pub enum PrintJobState {}",
                    "pub enum PrintSource {}",
                    "pub enum PrintCommand {}",
                    "pub enum PlannerFlowState {}",
                    "pub enum CommandRoute {}",
                    "pub fn route_gcode_mnemonic() {}",
                    "pub fn transition_print_state() {}",
                    'const COMMENT_ONLY: &str = "unsafe { unsafe fn";',
                    "// unsafe extern should be ignored in comments",
                ]
            ),
        )
        self.write_file(
            root,
            "rust/crates/domain/src/safety.rs",
            safety_text
            or "\n".join(
                [
                    "pub enum SafetyFlow {}",
                    "pub enum SafetyAction {}",
                    "pub enum EvidenceClass {}",
                    "pub struct FatalPathPolicy;",
                    "pub struct SafetyPolicySurface;",
                    "pub fn classify_safety_flow() {}",
                ]
            ),
        )
        self.write_file(
            root,
            "rust/crates/domain/src/feature.rs",
            feature_text
            or "\n".join(
                [
                    "pub enum Phase6FeatureGate {}",
                    "pub struct Phase6FeatureGates;",
                    "pub enum BurstSteppingMode {}",
                    "pub enum GateState { OutOfScopePhase10 }",
                    "pub fn HasAdcSideFilamentSensor() {}",
                    "pub fn HasChamberFiltrationApi() {}",
                    "pub fn HasLoadcellHx717() {}",
                    "pub fn HasMmu2OverUart() {}",
                ]
            ),
        )

    def write_phase6_quick_surface(self, root: Path) -> None:
        self.write_printing_manifest(root, intentional_delta=None)
        self.write_safety_manifest(root)
        self.write_feature_manifest(root)
        self.write_concern_manifest(root)
        self.write_facade_files(root)
        self.write_validation_contract(root)
        self.write_rust_api_surface(root)

    def test_help_lists_phase6_modes(self) -> None:
        result = self.run_verifier(["--help"])

        self.assertEqual(result.returncode, 0, msg=result.stdout)
        for flag in [
            "--quick",
            "--all",
            "--manifests-only",
            "--printing-only",
            "--safety-only",
            "--features-only",
            "--concerns-only",
        ]:
            self.assertIn(flag, result.stdout)

    def test_manifests_only_reports_missing_manifest(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file: tools/bazel/manifests/phase6_printing_core.json", result.stdout)

    def test_printing_only_rejects_invalid_evidence_class(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_printing_manifest(root, evidence_class="hardware passed")

            result = self.run_verifier(["--printing-only"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_class", result.stdout)

    def test_printing_only_accepts_null_intentional_delta(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_printing_manifest(root, intentional_delta=None)

            result = self.run_verifier(["--printing-only"], maybe_root=root)

        self.assertEqual(result.returncode, 0, msg=result.stdout)

    def test_quick_rejects_missing_print_rust_api_surface(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase6_quick_surface(root)
            self.write_rust_api_surface(root, print_text="pub enum PrintJobState {}\n")

            result = self.run_verifier(["--quick"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rust/crates/domain/src/print.rs", result.stdout)
        self.assertIn("FixtureId", result.stdout)

    def test_quick_rejects_missing_safety_rust_api_surface(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase6_quick_surface(root)
            self.write_rust_api_surface(root, safety_text="pub enum SafetyFlow {}\n")

            result = self.run_verifier(["--quick"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rust/crates/domain/src/safety.rs", result.stdout)
        self.assertIn("SafetyPolicySurface", result.stdout)

    def test_quick_rejects_missing_feature_rust_api_surface(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase6_quick_surface(root)
            self.write_rust_api_surface(root, feature_text="pub struct Phase6FeatureGates;\n")

            result = self.run_verifier(["--quick"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rust/crates/domain/src/feature.rs", result.stdout)
        self.assertIn("OutOfScopePhase10", result.stdout)

    def test_quick_rejects_unsafe_in_phase6_domain_modules(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase6_quick_surface(root)
            self.write_rust_api_surface(
                root,
                print_text="\n".join(
                    [
                        "pub struct FixtureId;",
                        "pub enum PrintJobState {}",
                        "pub enum PrintSource {}",
                        "pub enum PrintCommand {}",
                        "pub enum PlannerFlowState {}",
                        "pub enum CommandRoute {}",
                        "pub fn route_gcode_mnemonic() {}",
                        "pub fn transition_print_state() { unsafe { core::arch::asm!(\"nop\"); } }",
                    ]
                ),
            )

            result = self.run_verifier(["--quick"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe block", result.stdout)

    def test_quick_rejects_scope_overclaim_in_phase6_summary(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase6_quick_surface(root)
            self.write_file(root, f"{PHASE_DIR}/06-04-SUMMARY.md", "auth implemented\n")

            result = self.run_verifier(["--quick"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("auth implemented", result.stdout)

    def test_quick_rejects_missing_validation_contract(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase6_quick_surface(root)
            self.write_validation_contract(root, include_full_suite=False)

            result = self.run_verifier(["--quick"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("06-VALIDATION.md", result.stdout)
        self.assertIn("Full suite command", result.stdout)

    def test_all_runs_quick_checks_and_cargo_verification(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase6_quick_surface(root)
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

            result = self.run_verifier(["--all"], maybe_root=root, maybe_env=env)

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
