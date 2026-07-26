#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import phase34_final_readiness_demotion_dry_run as phase34
import phase35_cutover_decision_artifact as phase35


ROOT = Path(__file__).resolve().parents[2]
PHASE = "38-fail-closed-cutover-workflow"
PHASE_LIFECYCLE_ID = "38-2026-07-26T16-29-23"
AUTHORITY_GUARD = Path("build/ci-evidence/.phase35-authority-guard.json")
PHASE34_OUTPUT = Path("build/ci-evidence/phase34")
PHASE35_OUTPUT = Path("build/ci-evidence/phase35")
PHASE35_DECISION = PHASE35_OUTPUT / "cutover-decision.json"
PHASE35_ROUTE = PHASE35_OUTPUT / "next-milestone-route.json"
SAFE_REASON_CATEGORIES = {
    "none",
    "phase31-input-invalid",
    "phase33-handoff-invalid",
    "phase33-normalized-decisions-invalid",
    "phase33-readiness-input-invalid",
    "phase33-register-invalid",
    "phase32-blocker-register-invalid",
    "phase33-demotion-input-invalid",
    "phase34-operation-failed",
    "phase34-authority-invalid",
    "phase35-operation-failed",
    "phase35-authority-missing",
    "phase35-authority-invalid",
    "phase35-authority-contradictory",
    "phase35-authority-guard-blocking",
    *phase35.SAFE_SOURCE_FAILURE_REASONS,
}


class WorkflowError(Exception):

    def __init__(self, reason_category: str) -> None:
        safe_reason = (
            reason_category
            if reason_category in SAFE_REASON_CATEGORIES
            else "phase35-authority-invalid"
        )
        super().__init__(safe_reason)
        self.reason_category = safe_reason


@dataclass(frozen=True)
class CommandOutcome:
    status: int
    reason_category: str


@dataclass(frozen=True)
class FinalAuthority:
    available: bool
    verdict: str
    route: str
    readiness_state: str
    requires_fresh_cutover_decision: bool
    demotion_validation_state: str
    demotion_decision_state: str
    demotion_gate_state: str
    reason_category: str

    @classmethod
    def unavailable(cls, reason_category: str) -> FinalAuthority:
        return cls(
            available=False,
            verdict="blocked",
            route="targeted-blocker-repair",
            readiness_state="blocked",
            requires_fresh_cutover_decision=True,
            demotion_validation_state="invalid",
            demotion_decision_state="missing",
            demotion_gate_state="blocked",
            reason_category=reason_category,
        )


@dataclass(frozen=True)
class WorkflowResult:
    status: int
    reason_category: str
    phase34_status: int
    phase35_status: int
    final_authority_available: bool
    verdict: str
    route: str
    readiness_state: str
    production_cutover_planning: bool
    reference_demotion_authorized: bool
    requires_fresh_cutover_decision: bool
    phase_lifecycle_id: str = PHASE_LIFECYCLE_ID
    decision_ref: str = PHASE35_DECISION.as_posix()
    route_ref: str = PHASE35_ROUTE.as_posix()

    def to_safe_dict(self) -> dict[str, Any]:
        return asdict(self)


def authority_guard_payload() -> dict[str, object]:
    return phase35.authority_guard_payload()


def _safe_reason(reason_category: str, fallback: str) -> str:
    return (
        reason_category
        if reason_category in SAFE_REASON_CATEGORIES
        else fallback
    )


def _authority_is_consistent(authority: FinalAuthority) -> bool:
    if not authority.available:
        return False
    if authority.verdict == "approved":
        return (
            authority.route == "production-cutover-planning"
            and authority.readiness_state == "unblocked"
            and not authority.requires_fresh_cutover_decision
        )
    if authority.verdict in {"blocked", "approved-with-exceptions"}:
        return (
            authority.route == "targeted-blocker-repair"
            and authority.requires_fresh_cutover_decision
        )
    return False


def evaluate_final_status(
    phase34_outcome: CommandOutcome,
    phase35_outcome: CommandOutcome,
    authority: FinalAuthority,
) -> WorkflowResult:
    authority_consistent = _authority_is_consistent(authority)
    operations_succeeded = (
        phase34_outcome.status == 0
        and phase35_outcome.status == 0
    )
    production_cutover_planning = (
        operations_succeeded
        and authority_consistent
        and authority.verdict == "approved"
        and authority.route == "production-cutover-planning"
    )
    reference_demotion_authorized = (
        operations_succeeded
        and authority_consistent
        and authority.readiness_state == "unblocked"
        and authority.demotion_validation_state == "valid"
        and authority.demotion_decision_state == "approve"
        and authority.demotion_gate_state == "open"
    )

    if phase34_outcome.status != 0:
        status = phase34_outcome.status
        reason_category = _safe_reason(
            phase34_outcome.reason_category,
            "phase34-operation-failed",
        )
    elif phase35_outcome.status != 0:
        status = phase35_outcome.status
        reason_category = _safe_reason(
            phase35_outcome.reason_category,
            "phase35-operation-failed",
        )
    elif not authority.available:
        status = 1
        reason_category = _safe_reason(
            authority.reason_category,
            "phase35-authority-invalid",
        )
    elif not authority_consistent:
        status = 1
        reason_category = "phase35-authority-contradictory"
    else:
        status = 0
        reason_category = "none"

    return WorkflowResult(
        status=status,
        reason_category=reason_category,
        phase34_status=phase34_outcome.status,
        phase35_status=phase35_outcome.status,
        final_authority_available=(
            operations_succeeded
            and authority.available
            and authority_consistent
        ),
        verdict=authority.verdict,
        route=authority.route,
        readiness_state=authority.readiness_state,
        production_cutover_planning=production_cutover_planning,
        reference_demotion_authorized=reference_demotion_authorized,
        requires_fresh_cutover_decision=(
            authority.requires_fresh_cutover_decision
        ),
    )


def require_clear_authority_guard(
    root: Path,
    guard_ref: Path = AUTHORITY_GUARD,
) -> None:
    if (
        guard_ref.is_absolute()
        or ".." in guard_ref.parts
        or guard_ref != AUTHORITY_GUARD
    ):
        raise WorkflowError("phase35-authority-guard-blocking")

    current = root
    for index, part in enumerate(guard_ref.parts):
        current /= part
        if current.is_symlink():
            raise WorkflowError("phase35-authority-guard-blocking")
        if (
            index < len(guard_ref.parts) - 1
            and current.exists()
            and not current.is_dir()
        ):
            raise WorkflowError("phase35-authority-guard-blocking")

    guard = root / guard_ref
    if not guard.exists():
        return
    if not guard.is_file():
        raise WorkflowError("phase35-authority-guard-blocking")
    try:
        payload = json.loads(guard.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as error:
        raise WorkflowError(
            "phase35-authority-guard-blocking"
        ) from error
    if payload != authority_guard_payload():
        raise WorkflowError("phase35-authority-guard-blocking")
    raise WorkflowError("phase35-authority-guard-blocking")


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as error:
        raise WorkflowError("phase35-authority-invalid") from error
    if not isinstance(value, dict):
        raise WorkflowError("phase35-authority-invalid")
    return value


def load_final_authority(root: Path) -> FinalAuthority:
    require_clear_authority_guard(root)
    output = root / PHASE35_OUTPUT
    if not output.exists():
        return FinalAuthority.unavailable("phase35-authority-missing")
    if output.is_symlink() or not output.is_dir():
        return FinalAuthority.unavailable("phase35-authority-invalid")
    try:
        phase35.ensure_canonical_authority(root, PHASE35_OUTPUT)
        manifest = _load_json_object(
            output / "cutover-decision-run-manifest.json"
        )
        if manifest.get("generation_state") == "blocked-source-error":
            phase35.validate_source_failure_bundle(output)
        else:
            phase35.validate_installed_full_bundle(output)
        decision = _load_json_object(root / PHASE35_DECISION)
        route = _load_json_object(root / PHASE35_ROUTE)
    except (phase35.VerificationError, WorkflowError):
        return FinalAuthority.unavailable("phase35-authority-invalid")

    if (
        decision.get("phase_lifecycle_id") != phase35.PHASE_LIFECYCLE_ID
        or route.get("phase_lifecycle_id") != phase35.PHASE_LIFECYCLE_ID
        or route.get("source_verdict") != decision.get("cutover_verdict")
    ):
        return FinalAuthority.unavailable("phase35-authority-invalid")

    return FinalAuthority(
        available=True,
        verdict=str(decision.get("cutover_verdict") or "blocked"),
        route=str(route.get("route") or "targeted-blocker-repair"),
        readiness_state=str(
            decision.get("readiness_state") or "blocked"
        ),
        requires_fresh_cutover_decision=(
            route.get("requires_fresh_cutover_decision") is True
        ),
        demotion_validation_state=str(
            decision.get("demotion_decision_validation_state") or "invalid"
        ),
        demotion_decision_state=str(
            decision.get("demotion_decision_state") or "missing"
        ),
        demotion_gate_state=str(
            decision.get("demotion_gate_state") or "blocked"
        ),
        reason_category="none",
    )


def _run_phase34(root: Path) -> CommandOutcome:
    try:
        maybe_reason = phase34.run_quick(
            root,
            phase34.DEFAULT_PHASE31_OUTPUT_DIR.as_posix(),
            phase34.DEFAULT_PHASE33_HANDOFF.as_posix(),
            PHASE34_OUTPUT.as_posix(),
        )
    except phase34.VerificationError:
        return CommandOutcome(1, "phase34-operation-failed")
    if maybe_reason is None:
        return CommandOutcome(0, "none")
    return CommandOutcome(1, _safe_reason(maybe_reason, "phase34-operation-failed"))


def _phase34_authority_is_valid(root: Path) -> bool:
    output = root / PHASE34_OUTPUT
    if output.is_symlink() or not output.is_dir():
        return False
    try:
        phase34.validate_generated_outputs(output)
        phase34.validate_output_security(output, PHASE34_OUTPUT.as_posix())
        packet = _load_json_object(
            output / "final-readiness-packet.json"
        )
    except (phase34.VerificationError, WorkflowError):
        return False
    return (
        packet.get("phase_lifecycle_id") == phase34.PHASE_LIFECYCLE_ID
        and packet.get("readiness_state") in {"blocked", "unblocked"}
    )


def _run_phase35(root: Path) -> CommandOutcome:
    try:
        phase35.run_quick(
            root,
            PHASE34_OUTPUT.as_posix(),
            PHASE35_OUTPUT.as_posix(),
        )
    except phase35.VerificationError as error:
        return CommandOutcome(
            1,
            _safe_reason(error.reason_code, "phase35-operation-failed"),
        )
    return CommandOutcome(0, "none")


def coordinate_workflow(root: Path = ROOT) -> WorkflowResult:
    try:
        phase35.publish_authority_guard(root)
    except phase35.VerificationError:
        guard_failure = CommandOutcome(
            1,
            "phase35-authority-guard-blocking",
        )
        return evaluate_final_status(
            CommandOutcome(0, "none"),
            guard_failure,
            FinalAuthority.unavailable(
                "phase35-authority-guard-blocking"
            ),
        )

    phase34_outcome = _run_phase34(root)
    if not _phase34_authority_is_valid(root):
        invalid_phase34 = CommandOutcome(
            phase34_outcome.status or 1,
            "phase34-authority-invalid",
        )
        return evaluate_final_status(
            invalid_phase34,
            CommandOutcome(0, "none"),
            FinalAuthority.unavailable("phase34-authority-invalid"),
        )

    phase35_outcome = _run_phase35(root)
    try:
        authority = load_final_authority(root)
    except WorkflowError as error:
        authority = FinalAuthority.unavailable(error.reason_category)
    return evaluate_final_status(
        phase34_outcome,
        phase35_outcome,
        authority,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize fail-closed Phase 34 and Phase 35 cutover authority."
        )
    )
    parser.add_argument("--quick", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv or sys.argv[1:])
    if not args.quick:
        print("no mode selected", file=sys.stderr)
        return 2
    result = coordinate_workflow(ROOT)
    print(json.dumps(result.to_safe_dict(), sort_keys=True))
    return result.status


if __name__ == "__main__":
    raise SystemExit(main())
