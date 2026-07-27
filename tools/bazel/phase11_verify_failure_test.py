#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase11_verify_test import *  # noqa: F403


class Phase11VerifierFailureTest(Phase11VerifierFixture, unittest.TestCase):

    def test_pyramid_only_rejects_local_hardware_overclaim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [
                self.pyramid_row(row_id) for row_id in REQUIRED_PYRAMID_ROW_IDS
                if row_id != "pyramid-hardware-smoke-manual-gates"
            ]
            rows.append(
                self.pyramid_row(
                    "pyramid-hardware-smoke-manual-gates",
                    proof_scope="hardware-smoke",
                    evidence_class="manual-hardware-required",
                    local_status="passed-local",
                ))
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pyramid-hardware-smoke-manual-gates", result.stdout)
        self.assertIn("passed-local", result.stdout)

    def test_pyramid_only_rejects_source_path_escape(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [
                self.pyramid_row(row_id) for row_id in REQUIRED_PYRAMID_ROW_IDS
            ]
            rows[0]["source_artifacts"] = ["../outside"]
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("../outside", result.stdout)
        self.assertIn("repo-relative", result.stdout)

    def test_pyramid_only_rejects_path_confusing_row_ids(self) -> None:
        # Arrange
        invalid_row_ids = {
            "pyramid rust unit tests": "id must be printable ASCII",
            "pyramid-rust..unit-tests": "id must be path-free",
        }

        for invalid_row_id, expected_message in invalid_row_ids.items():
            with self.subTest(invalid_row_id=invalid_row_id):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = [
                        self.pyramid_row(row_id)
                        for row_id in REQUIRED_PYRAMID_ROW_IDS
                    ]
                    rows[0]["id"] = invalid_row_id
                    self.write_complete_pyramid_manifest(root, rows=rows)

                    # Act
                    result = self.run_verifier(["--pyramid-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(invalid_row_id, result.stdout)
                self.assertIn(expected_message, result.stdout)

    def test_pyramid_only_rejects_secret_marker(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [
                self.pyramid_row(row_id) for row_id in REQUIRED_PYRAMID_ROW_IDS
            ]
            rows[0]["secret_handling"] = "token_value"
            rows[1]["cutover_status"] = "byte-identical firmware"
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token_value", result.stdout)
        self.assertIn("byte-identical firmware", result.stdout)

    def test_pyramid_only_rejects_missing_required_row(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [
                self.pyramid_row(row_id) for row_id in REQUIRED_PYRAMID_ROW_IDS
                if row_id != "pyramid-retained-code-justifications"
            ]
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pyramid-retained-code-justifications", result.stdout)

    def test_pyramid_only_rejects_empty_non_local_evidence_list(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_complete_pyramid_manifest(root)
            rows = self.manifest_rows(root, PYRAMID_MANIFEST)
            for row in rows:
                if row["id"] == "pyramid-simulator-flows":
                    row["required_non_local_evidence"] = []
            self.write_manifest_rows(root, PYRAMID_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pyramid-simulator-flows", result.stdout)
        self.assertIn("required_non_local_evidence", result.stdout)

    def test_pyramid_only_rejects_stale_requires_plan_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, PYRAMID_MANIFEST)
            for row in rows:
                if row["id"] == "pyramid-reference-fixture-comparisons":
                    row["cutover_status"] = "requires-plan-11-03-reference-comparison-rows"
                if row["id"] == "pyramid-retained-code-justifications":
                    row["cutover_status"] = "requires-plan-11-04-retained-code-review"
            self.write_manifest_rows(root, PYRAMID_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires-plan-11-03-reference-comparison-rows",
                      result.stdout)
        self.assertIn("requires-plan-11-04-retained-code-review",
                      result.stdout)

    def test_scoped_checks_report_missing_contracts(self) -> None:
        cases = [
            ("--requirements-only", ".planning/REQUIREMENTS.md",
             "# Requirements\n", ["phase11_requirement_evidence.json"]),
            ("--comparison-only", None, None,
             ["phase11_reference_comparisons.json"]),
            ("--cutover-only", None, None, [
                "phase11_cutover_readiness.json",
                "phase11_retained_code_justifications.json"
            ]),
            ("--rust-only", "rust/crates/domain/src/lib.rs",
             "#![forbid(unsafe_code)]\n",
             ["rust/crates/domain/src/cutover.rs"]),
        ]
        for flag, maybe_path, maybe_text, expected in cases:
            with self.subTest(flag=flag):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    if maybe_path is not None and maybe_text is not None:
                        self.write_file(root, maybe_path, maybe_text)

                    # Act
                    result = self.run_verifier([flag], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                for needle in expected:
                    self.assertIn(needle, result.stdout)

    def test_requirements_only_rejects_missing_v1_requirement(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = [
                row for row in self.manifest_rows(root, REQUIREMENT_MANIFEST)
                if row["id"] != "req-verf-05"
            ]
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("req-verf-05", result.stdout)

    def test_requirements_only_rejects_roadmap_only_proof(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            self.write_file(root, ".planning/ROADMAP.md", "roadmap fixture\n")
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-verf-04":
                    row["source_artifacts"] = [".planning/ROADMAP.md"]
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("roadmap-only", result.stdout)

    def test_requirements_only_rejects_empty_non_local_evidence_list(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-base-02":
                    row["required_non_local_evidence"] = []
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("req-base-02", result.stdout)
        self.assertIn("required_non_local_evidence", result.stdout)

    def test_requirements_only_rejects_stale_not_created_yet_blocker(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-rust-03":
                    row["cutover_blocker"] = (
                        "Plan 11-04 retained-code acceptance rows are not created yet."
                    )
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not created yet", result.stdout)

    def test_comparison_only_rejects_byte_identity_without_fixture(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "byte-identity-with-fixture"
                    row["byte_identity_claim"] = True
                    row.pop("reference_fixture", None)
                    row["normalization_rule"] = "normalize release metadata"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn("byte_identity_claim", result.stdout)

    def test_comparison_only_rejects_unknown_comparison_kind(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "normalized-semantics"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn("comparison_kind is not allowed", result.stdout)

    def test_comparison_only_rejects_normalized_byte_identity_claim(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "normalized-semantic"
                    row["byte_identity_claim"] = True
                    row["reference_fixture"] = "release-candidate-metadata"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn("normalized comparisons must not claim byte identity",
                      result.stdout)

    def test_comparison_only_rejects_byte_identity_kind_without_claim(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "byte-identity-with-fixture"
                    row["byte_identity_claim"] = False
                    row["reference_fixture"] = "release-candidate-metadata"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn(
            "byte identity comparisons must set byte_identity_claim true",
            result.stdout)

    def test_comparison_only_rejects_empty_non_local_evidence_list(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-product-artifacts":
                    row["required_non_local_evidence"] = []
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-product-artifacts", result.stdout)
        self.assertIn("required_non_local_evidence", result.stdout)

    def test_cutover_only_rejects_non_string_cutover_lists(self) -> None:
        # Arrange
        invalid_fields = ["required_evidence", "verifier_commands"]

        for invalid_field in invalid_fields:
            with self.subTest(invalid_field=invalid_field):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_phase11_surface(root)
                    rows = self.manifest_rows(root, CUTOVER_MANIFEST)
                    for row in rows:
                        if row["id"] == "criteria-all-v1-requirements-mapped":
                            row[invalid_field] = [123]
                    self.write_manifest_rows(root, CUTOVER_MANIFEST, rows)

                    # Act
                    result = self.run_verifier(["--cutover-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("criteria-all-v1-requirements-mapped",
                              result.stdout)
                self.assertIn(invalid_field, result.stdout)
                self.assertIn("list of strings", result.stdout)

    def test_cutover_only_rejects_non_string_retained_required_evidence(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, RETAINED_MANIFEST)
            for row in rows:
                if row["id"] == "retained-hal-cmsis-vendor":
                    row["required_evidence"] = [123]
            self.write_manifest_rows(root, RETAINED_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("retained-hal-cmsis-vendor", result.stdout)
        self.assertIn("required_evidence", result.stdout)
        self.assertIn("list of strings", result.stdout)

    def test_cutover_only_rejects_demote_reference_true(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, CUTOVER_MANIFEST)
            for row in rows:
                if row["id"] == "criteria-local-verifier-passed":
                    row["status"] = "pending-aggregate-verifier"
                    row["demotion_allowed"] = True
            self.write_manifest_rows(root, CUTOVER_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("criteria-local-verifier-passed", result.stdout)
        self.assertIn("demotion_allowed", result.stdout)

    def test_cutover_only_rejects_ready_reference_demotion_status(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, CUTOVER_MANIFEST)
            for row in rows:
                if row["id"] == "criteria-reference-demotion-blocked":
                    row["status"] = "passed-local"
            self.write_manifest_rows(root, CUTOVER_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("criteria-reference-demotion-blocked", result.stdout)
        self.assertIn("status must remain not-cutover-ready", result.stdout)

    def test_cutover_only_rejects_known_concern_source_path_escape(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            data = json.loads(
                (root / CUTOVER_MANIFEST).read_text(encoding="utf-8"))
            rows = data["known_concern_dispositions"]
            self.assertIsInstance(rows, list)
            rows[0]["source_artifacts"] = ["../outside"]
            self.write_file(root, CUTOVER_MANIFEST, json.dumps(data, indent=2))

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("known concern", result.stdout)
        self.assertIn("../outside", result.stdout)
        self.assertIn("repo-relative", result.stdout)

    def test_security_only_rejects_secret_markers_in_phase_docs(self) -> None:
        cases = [
            (f"{PHASE_DIR}/11-VALIDATION.md", True),
            (f"{ARCHIVED_PHASE_DIR}/11-VALIDATION.md", False),
            (f"{ARCHIVED_PHASE_DIR}/11-VERIFICATION.md", False),
            (f"{PHASE_DIR}/11-CONTEXT.md", True),
            (f"{PHASE_DIR}/11-RESEARCH.md", True),
        ]
        for phase_doc_path, copy_surface in cases:
            with self.subTest(phase_doc_path=phase_doc_path):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    if copy_surface:
                        self.copy_phase11_surface(root)
                    self.write_file(root, phase_doc_path, "token_value\n")

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("token_value", result.stdout)

    def test_security_only_rejects_private_key_header_variants(self) -> None:
        # Arrange
        private_key_headers = [
            "-----BEGIN RSA PRIVATE KEY-----",
            "-----BEGIN EC PRIVATE KEY-----",
            "-----BEGIN OPENSSH PRIVATE KEY-----",
        ]

        for private_key_header in private_key_headers:
            with self.subTest(private_key_header=private_key_header):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_phase11_surface(root)
                    self.write_file(root, f"{PHASE_DIR}/11-VALIDATION.md",
                                    private_key_header)

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(private_key_header, result.stdout)

    def test_security_only_rejects_mixed_case_secret_field_names(self) -> None:
        # Arrange
        secret_field_names = [
            "Certificate-Pem",
            "Password_Value",
            "Token-Value",
            "Private_Key",
        ]

        for secret_field_name in secret_field_names:
            with self.subTest(secret_field_name=secret_field_name):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_phase11_surface(root)
                    self.write_file(root, f"{PHASE_DIR}/11-VALIDATION.md",
                                    secret_field_name)

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(secret_field_name, result.stdout)

    def test_security_only_rejects_cutover_overclaim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            self.write_file(root, f"{PHASE_DIR}/11-01-SUMMARY.md",
                            "hardware verified locally\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware verified locally", result.stdout)

    def test_rust_only_rejects_unsafe_cutover_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            cutover_path = root / "rust/crates/domain/src/cutover.rs"
            cutover_path.write_text(
                cutover_path.read_text(encoding="utf-8") +
                "\nunsafe fn unsound() {}\n",
                encoding="utf-8",
            )

            # Act
            result = self.run_verifier(["--rust-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe function", result.stdout)

    def test_requirements_only_rejects_stale_pending_plan_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root, reconcile_requirements=False)
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-verf-03":
                    row["current_status"] = "pending-plan-11-03"
                if row["id"] == "req-verf-05":
                    row["current_status"] = "pending-plan-11-04"
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pending-plan-11-03", result.stdout)
        self.assertIn("pending-plan-11-04", result.stdout)
