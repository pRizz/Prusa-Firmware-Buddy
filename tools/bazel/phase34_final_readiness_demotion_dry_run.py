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
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phase34_decision_reconciliation import reconcile_decision_rows

ROOT = Path(__file__).resolve().parents[2]
PHASE = "34-final-readiness-and-demotion-dry-run"
PHASE_LIFECYCLE_ID = "34-2026-07-25T18-18-48"
PHASE31_LIFECYCLE_ID = "31-2026-07-03T02-04-07"
PHASE32_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
PHASE33_LIFECYCLE_ID = "33-2026-07-04T01-36-41"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json"
)
PHASE31_CONTRACT = Path(
    "tools/bazel/manifests/phase31_final_evidence_intake_contract.json")
PHASE32_CONTRACT = Path(
    "tools/bazel/manifests/phase32_blocker_register_triage_contract.json")
PHASE33_CONTRACT = Path(
    "tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json")
PHASE28_CONTRACT = Path(
    "tools/bazel/manifests/phase28_final_readiness_packet_contract.json")
DEFAULT_PHASE31_OUTPUT_DIR = Path("build/ci-evidence/phase31")
DEFAULT_PHASE31_MANIFEST = DEFAULT_PHASE31_OUTPUT_DIR / "final-intake-manifest.json"
DEFAULT_PHASE33_HANDOFF = Path(
    "build/ci-evidence/phase33/downstream-handoff-manifest.json")
PHASE33_OUTPUT_ROOT = Path("build/ci-evidence/phase33")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase34")
PUBLICATION_STATE_SHELL = Path("build/ci-evidence/.phase34-publication-state")
PUBLICATION_STATE_PAYLOAD_NAME = "state.json"
PUBLICATION_STATE_FIELDS = [
    "phase",
    "phase_lifecycle_id",
    "attempt_id",
    "authority_state",
    "reason_category",
    "canonical_output_ref",
]
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
REQUIRED_REQUIREMENT_IDS = ["READY-01", "READY-02", "READY-03"]
REQUIRED_PHASE31_STREAMS = (
    "simulator",
    "hardware-media-safety",
    "live-service",
    "release-signing",
)
LEDGER_FIELDS = [
    "row_id",
    "ledger_row_kind",
    "source_domain",
    "producer_phase",
    "producer_artifact_kind",
    "source_row_kind",
    "source_subject_id",
    "decision_axis",
    "decision_subject_id",
    "phase_lifecycle_id",
    "source_stream",
    "source_ref",
    "requirement_ids",
    "affected_gates",
    "proof_eligibility",
    "evidence_status",
    "row_problem_kind",
    "blocker_kind",
    "severity",
    "evidence_refs",
    "artifact_refs",
    "classification_ref",
    "retained_code_decision_refs",
    "residual_risk_decision_refs",
    "exception_decision_refs",
    "readiness_decision_refs",
    "demotion_decision_refs",
    "coverage_state",
    "readiness_effect",
    "reason_codes",
]
GENERATED_ARTIFACTS = [
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
HARD_BLOCKER_PROBLEM_KINDS = {
    "redaction_failed",
    "source_ref_failed",
    "secret_tainted",
    "lifecycle_mismatch",
    "unsafe_ref",
}
PROBLEM_REASON_CODES = {
    "missing": "required-row-missing",
    "failed": "evidence-failed",
    "stale": "evidence-stale",
    "malformed": "evidence-malformed",
    "redaction_failed": "redaction-failed",
    "source_ref_failed": "source-ref-failed",
    "secret_tainted": "secret-tainted",
    "lifecycle_mismatch": "lifecycle-mismatched",
    "unsafe_ref": "unsafe-ref",
    "non_final_placeholder": "non-final-evidence",
    "smoke_fixture": "non-final-evidence",
    "local_dry_run": "non-final-evidence",
    "prose_attestation": "non-final-evidence",
    "row_only_submission": "non-final-evidence",
    "unknown_unclassified": "unknown-classification",
}
PHASE33_REQUIRED_DECISION_FIELDS = [
    "decision_id",
    "decision_type",
    "decision_value",
    "source_row_refs",
    "decision_targets",
    "maintainer_identity_ref",
    "maintainer_role",
    "owner_signoff_ref",
    "decision_timestamp",
    "rationale",
    "evidence_refs",
    "artifact_refs",
]
PHASE33_DECISION_VALUE_ENUMS = {
    "retained_code": {"accept", "reject", "exception_approve"},
    "residual_risk": {"accept", "reject"},
    "exception": {"approve", "reject"},
    "readiness": {"approve", "block"},
    "reference_demotion": {"approve", "reject"},
}
PHASE33_DECISION_AXES = {
    "retained_code": "retained_code",
    "residual_risk": "residual_risk",
    "exception": "exception",
    "readiness": "readiness",
    "reference_demotion": "demotion",
}
DECISION_DOMAIN_PRODUCER_PHASES = {"phase27", "phase28"}
EXPECTED_GATE_BY_STREAM = {
    "simulator": "final-simulator-evidence",
    "hardware-media-safety": "final-hardware-safety-media-evidence",
    "live-service": "final-live-network-transfer-evidence",
    "release-signing": "final-release-artifact-signing-evidence",
    "upstream-result": "final-upstream-result-evidence",
    "retained-code": "final-retained-code-acceptance",
    "readiness": "final-readiness",
    "unknown": "cutover-decision",
}
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api_key",
    "authorization_header",
    "certificate_private_material",
    "client_secret",
    "connect_token",
    "credential_value",
    "demotion_allowed",
    "password",
    "private_key",
    "raw_crash_dump",
    "raw_release_log",
    "secret",
    "secret_value",
    "service_payload",
    "signing_key_value",
    "signing_payload_bytes",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("bearer-token",
     re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)),
    ("service-payload", re.compile(r"\bservice[_ -]?payload\b",
                                   re.IGNORECASE)),
    ("raw-crash-dump",
     re.compile(r"\braw[_ -]?crash[_ -]?dump\b", re.IGNORECASE)),
    ("demotion-allowed", re.compile(r'"?demotion_allowed"?\s*:',
                                    re.IGNORECASE)),
    ("evidence-demotion-overclaim",
     re.compile(r"\breference demotion approved by evidence\b",
                re.IGNORECASE)),
    ("production-demotion",
     re.compile(r"\bproduction demotion complete\b", re.IGNORECASE)),
    ("cutover-verdict",
     re.compile(r"\bcutover verdict approved\b", re.IGNORECASE)),
    ("evidence-alone",
     re.compile(r"\baccepted by evidence alone\b", re.IGNORECASE)),
)
NON_SNAPSHOT_OUTPUTS = [
    artifact for artifact in GENERATED_ARTIFACTS
    if not artifact.startswith("contract-snapshots/")
]
PHASE34_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
    ("python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick "
     "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
     "--output-dir build/ci-evidence/phase27"),
    ("python3 tools/bazel/phase28_final_readiness_packet.py --quick "
     "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
     "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
     "--output-dir build/ci-evidence/phase28"),
    ("python3 tools/bazel/phase32_blocker_register_triage.py --quick "
     "--phase31-output-dir build/ci-evidence/phase31 "
     "--phase27-output-dir build/ci-evidence/phase27 "
     "--phase28-output-dir build/ci-evidence/phase28 "
     "--output-dir build/ci-evidence/phase32"),
    ("python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick "
     "--phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json "
     "--output-dir build/ci-evidence/phase33"),
    "python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only",
    ("python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --quick "
     "--phase31-output-dir build/ci-evidence/phase31 "
     "--phase33-handoff build/ci-evidence/phase33/downstream-handoff-manifest.json "
     "--output-dir build/ci-evidence/phase34"),
]
SOURCE_FAILURE_REASON_CODES = [
    "phase31-input-invalid",
    "phase33-handoff-invalid",
    "phase33-normalized-decisions-invalid",
    "phase33-readiness-input-invalid",
    "phase33-register-invalid",
    "phase32-blocker-register-invalid",
    "phase33-demotion-input-invalid",
]
SOURCE_FAILURE_AUTHORITY_FIELDS = {
    "readiness_state": "blocked",
    "cutover_verdict_state": "blocked",
    "production_cutover_route_state": "blocked",
    "demotion_gate_state": "blocked",
}


def _install_phase34_modules() -> None:
    module_dir = Path(__file__).resolve().parent
    for module_name in (
            "phase34_publication_state.py",
            "phase34_source_validation.py",
            "phase34_decision_validation.py",
            "phase34_readiness_policy.py",
            "phase34_coverage_diagnostics.py",
            "phase34_bundle_publication.py",
            "phase34_readiness_wiring.py",
    ):
        source = (module_dir / module_name).read_text(encoding="utf-8")
        exec(compile(source, module_name, "exec"), globals())


_install_phase34_modules()
