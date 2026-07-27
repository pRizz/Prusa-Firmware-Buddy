#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import stat
import sys
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
PHASE = "35-cutover-decision-artifact"
PHASE_LIFECYCLE_ID = "35-2026-07-25T21-06-10"
PHASE33_LIFECYCLE_ID = "33-2026-07-04T01-36-41"
PHASE34_LIFECYCLE_ID = "34-2026-07-25T18-18-48"
CONTRACT_PATH = Path(
    "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json")
PHASE34_CONTRACT_PATH = Path(
    "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json"
)
DEFAULT_PHASE34_OUTPUT = Path("build/ci-evidence/phase34")
DEFAULT_OUTPUT = Path("build/ci-evidence/phase35")
AUTHORITY_GUARD = Path("build/ci-evidence/.phase35-authority-guard.json")
PREVIOUS_OUTPUT = Path("build/ci-evidence/.phase35-previous")
WORKFLOW_ATTEMPT_SHELL = Path("build/ci-evidence/.phase38-workflow-attempt")
AUTHORITY_GUARD_FIELDS = [
    "phase",
    "phase_lifecycle_id",
    "authority_state",
    "reason_code",
    "attempted_output_root",
]
AUTHORITY_GUARD_REASON = "publication-in-progress"
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
PHASE34_LEDGER_REF = "build/ci-evidence/phase34/readiness-coverage-ledger.json"
PHASE33_NORMALIZED_REGISTER = "build/ci-evidence/phase33/normalized-decision-records.json"
PHASE33_EXCEPTION_REGISTER = "build/ci-evidence/phase33/exception-decision-register.json"
PHASE33_RESIDUAL_REGISTER = "build/ci-evidence/phase33/residual-risk-decision-register.json"
REQUIREMENTS = ["CUTOVER-01", "CUTOVER-02", "CUTOVER-03"]
AUDIT_KINDS = [
    "evidence-packet",
    "blocker",
    "exception",
    "residual-risk",
    "retained-code-decision",
    "readiness-decision",
    "readiness-result",
    "demotion-decision",
    "demotion-dry-run",
]
AUDIT_FIELDS = [
    "link_id",
    "kind",
    "target_id",
    "target_ref",
    "source_phase_lifecycle_id",
    "verdict_effect",
]
GENERATED_ARTIFACTS = [
    "cutover-decision-run-manifest.json",
    "cutover-audit-link-index.json",
    "cutover-decision.json",
    "next-milestone-route.json",
    "redacted-cutover-decision-report.md",
    "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
    "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
    "contract-snapshots/phase34-final-readiness-run-manifest.json",
]
SOURCE_FAILURE_ARTIFACTS = [
    "cutover-decision-run-manifest.json",
    "cutover-decision.json",
    "next-milestone-route.json",
]
SOURCE_FAILURE_MANIFEST_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "generation_state",
    "output_root",
    "generated_artifacts",
    "source_manifest_ref",
    "source_failure_reason_codes",
    "raw_evidence_consumed",
]
SOURCE_FAILURE_REASON_CODES = [
    "source-artifact-missing",
    "source-artifact-malformed",
    "source-artifact-stale",
    "source-artifact-lifecycle-mismatched",
    "secret-tainted",
    "unsafe-ref",
    "source-ref-failed",
]
SAFE_SOURCE_FAILURE_REASONS = set(SOURCE_FAILURE_REASON_CODES)
DECISION_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "requirement_ids",
    "cutover_verdict",
    "reason_codes",
    "readiness_state",
    "readiness_result_ref",
    "active_exception_ids",
    "blocker_ids",
    "audit_link_index_ref",
    "audit_link_counts_by_kind",
    "demotion_decision_validation_state",
    "demotion_decision_state",
    "demotion_decision_source_refs",
    "demotion_gate_state",
    "demotion_gate_reason_codes",
    "route_ref",
    "raw_evidence_consumed",
]
ROUTE_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "route",
    "source_verdict",
    "follow_up_scope",
    "requires_fresh_cutover_decision",
    "planning_only",
    "production_actions_authorized",
]
PHASE34_ARTIFACTS = [
    "final-readiness-run-manifest.json",
    "readiness-coverage-ledger.json",
    "final-readiness-packet.json",
    "readiness-blocker-summary.json",
    "demotion-dry-run.json",
    "redacted-readiness-report.md",
    "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase33-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
    "contract-snapshots/phase31-final-intake-manifest.json",
    "contract-snapshots/phase31-accepted-receipts.json",
]
PHASE35_CONTRACT_FIELDS = {
    "artifact_name",
    "audit_link_failure_modes",
    "audit_link_schema",
    "authority_boundaries",
    "authority_guard",
    "blocked_reason_codes",
    "cutover_decision_fields",
    "default_behavior",
    "demotion_projection",
    "generated_artifacts",
    "id",
    "output_root",
    "phase",
    "phase_lifecycle_id",
    "repair_scope_fields",
    "repair_scope_ref_policy",
    "requirement_ids",
    "route_enum",
    "route_fields",
    "route_semantics",
    "route_truth_table",
    "schema_version",
    "security",
    "source_contract",
    "source_failure_behavior",
    "source_lifecycle_ids",
    "verdict_enum",
    "verdict_truth_table",
    "verification_commands",
}
PHASE34_CONTRACT_FIELDS = {
    "artifact_name",
    "blocked_reason_codes",
    "decision_domain_policy",
    "default_behavior",
    "demotion_dry_run_schema",
    "generated_artifacts",
    "hard_blocker_problem_kinds",
    "id",
    "io_validation_responsibilities",
    "ledger_schema",
    "output_root",
    "phase",
    "phase_lifecycle_id",
    "prohibited_output_markers",
    "prohibited_semantics",
    "pure_evaluator_outputs",
    "requirement_ids",
    "schema_version",
    "source_contracts",
    "source_inputs",
    "source_failure_policy",
    "sparse_blocker_overlay_policy",
    "test_command",
    "verification_commands",
}
PHASE34_MANIFEST_FIELDS = {
    "accepted_receipt_snapshot_ref",
    "artifact_name",
    "generated_artifacts",
    "generated_at_utc",
    "output_root",
    "phase",
    "phase_lifecycle_id",
    "phase33_register_digests",
    "raw_evidence_consumed",
    "snapshot_refs",
    "source_refs",
}
PHASE33_REGISTER_NAMES = {
    "decision_validation_report",
    "demotion_decision_handoff",
    "exception_decision_register",
    "normalized_decision_records",
    "readiness_decision_handoff",
    "residual_risk_decision_register",
    "retained_code_decision_register",
}
ALLOWED_REF_PREFIXES = (
    "build/ci-evidence/phase23/",
    "build/ci-evidence/phase24/",
    "build/ci-evidence/phase25/",
    "build/ci-evidence/phase26/",
    "build/ci-evidence/phase27/",
    "build/ci-evidence/phase28/",
    "build/ci-evidence/phase29/",
    "build/ci-evidence/phase30/",
    "build/ci-evidence/phase31/",
    "build/ci-evidence/phase32/",
    "build/ci-evidence/phase33/",
    "build/ci-evidence/phase34/",
    "build/ci-evidence/phase35/",
    "external://phase23/",
    "external://phase24/",
    "external://phase25/",
    "external://phase26/",
    "external://phase27/",
    "external://phase28/",
    "external://phase29/",
    "external://phase30/",
    "external://phase31/",
    "external://phase32/",
    "external://phase33/",
    "external://phase34/",
    "maintainer://",
    "owner://",
)
FORBIDDEN_FIELDS = {
    "access_token",
    "api_key",
    "authorization_header",
    "certificate_pem",
    "client_secret",
    "credential_value",
    "password",
    "private_key",
    "raw_crash_dump",
    "raw_payload",
    "raw_release_log",
    "secret",
    "secret_value",
    "service_payload",
    "signing_key_value",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE),
    re.compile(r"\bproduction demotion complete\b", re.IGNORECASE),
    re.compile(r"\breference demotion authorized by cutover\b", re.IGNORECASE),
    re.compile(r"\bproduction rollout authorized\b", re.IGNORECASE),
    re.compile(r"\braw evidence payload\b", re.IGNORECASE),
)
CONTRACT_VOCABULARY = {
    "production demotion complete",
    "reference demotion authorized by cutover",
    "production rollout authorized",
    "raw evidence payload",
}
STALE_BEFORE = datetime(2026, 4, 26, tzinfo=timezone.utc)
PHASE35_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
    "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27",
    "python3 tools/bazel/phase28_final_readiness_packet.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json --output-dir build/ci-evidence/phase28",
    "python3 tools/bazel/phase32_blocker_register_triage.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase27-output-dir build/ci-evidence/phase27 --phase28-output-dir build/ci-evidence/phase28 --output-dir build/ci-evidence/phase32",
    "python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick --phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase33",
    "python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only",
    "python3 tools/bazel/phase35_cutover_decision_artifact.py --wiring-only",
    "run_phase38_coordinator",
]
PHASE35_TEST_COMMANDS = [
    "python3 tools/bazel/phase35_cutover_decision_artifact_test.py",
]


def _install_phase35_modules() -> None:
    module_dir = Path(__file__).resolve().parent
    for module_name in (
            "phase35_contract_security.py",
            "phase35_cutover_policy.py",
            "phase35_source_bundle.py",
            "phase35_authority_guard.py",
            "phase35_bundle_wiring.py",
    ):
        source = (module_dir / module_name).read_text(encoding="utf-8")
        exec(compile(source, module_name, "exec"), globals())


_install_phase35_modules()
