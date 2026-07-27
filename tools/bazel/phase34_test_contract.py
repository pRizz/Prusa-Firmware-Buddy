#!/usr/bin/env python3
from __future__ import annotations

import importlib
import importlib.util
import textwrap
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "tools/bazel").as_posix())
VERIFIER = ROOT / "tools/bazel/phase34_final_readiness_demotion_dry_run.py"
CONTRACT = ROOT / "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json"
PHASE31_MANIFEST = "build/ci-evidence/phase31/final-intake-manifest.json"
PHASE32_REGISTER = "build/ci-evidence/phase32/blocker-register.json"
PHASE33_HANDOFF = "build/ci-evidence/phase33/downstream-handoff-manifest.json"
OUTPUT_DIR = "build/ci-evidence/phase34"
REQUIRED_STREAM_SOURCE_REFS = {
    "simulator":
    "build/ci-evidence/phase23/upstream-simulator-result-row.json",
    "hardware-media-safety":
    "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
    "live-service":
    "build/ci-evidence/phase25/upstream-live-service-result-row.json",
    "release-signing":
    "build/ci-evidence/phase26/upstream-result-row-table.json",
}
EXPECTED_GATE_BY_STREAM = {
    "simulator": "final-simulator-evidence",
    "hardware-media-safety": "final-hardware-safety-media-evidence",
    "live-service": "final-live-network-transfer-evidence",
    "release-signing": "final-release-artifact-signing-evidence",
}
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
