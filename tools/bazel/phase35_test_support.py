#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from collections.abc import Callable
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "tools/bazel").as_posix())

import phase35_cutover_decision_artifact as phase35
import phase38_cutover_workflow as workflow

CONTRACT = ROOT / "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json"
PHASE32_REGISTER = "build/ci-evidence/phase32/blocker-register.json"
PHASE33_NORMALIZED_REGISTER = "build/ci-evidence/phase33/normalized-decision-records.json"
PHASE33_EXCEPTION_REGISTER = "build/ci-evidence/phase33/exception-decision-register.json"
PHASE33_RESIDUAL_REGISTER = "build/ci-evidence/phase33/residual-risk-decision-register.json"
PHASE34_LEDGER = "build/ci-evidence/phase34/readiness-coverage-ledger.json"

VERDICTS = ["approved", "blocked", "approved-with-exceptions"]
ROUTES = ["production-cutover-planning", "targeted-blocker-repair"]
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
AUDIT_REQUIRED_FIELDS = [
    "link_id",
    "kind",
    "target_id",
    "target_ref",
    "source_phase_lifecycle_id",
    "verdict_effect",
]
BLOCKED_REASONS = [
    "source-artifact-missing",
    "source-artifact-malformed",
    "source-artifact-stale",
    "source-artifact-duplicate",
    "source-artifact-lifecycle-mismatched",
    "redaction-failed",
    "source-ref-failed",
    "secret-tainted",
    "unsafe-ref",
    "unknown-input",
    "underclassified",
    "coverage-incomplete",
    "readiness-blocked",
    "exception-invalid",
    "audit-link-missing",
    "audit-link-extra",
    "audit-link-duplicate",
    "audit-link-dangling",
    "audit-link-lifecycle-mismatched",
    "audit-link-category-mismatched",
    "audit-link-digest-mismatched",
    "route-scope-incomplete",
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
