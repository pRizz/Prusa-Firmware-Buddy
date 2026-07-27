#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import sys
import uuid
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
WORKFLOW_ATTEMPT_SHELL = Path(
    "build/ci-evidence/.phase38-workflow-attempt"
)
WORKFLOW_ATTEMPT_PAYLOAD_NAME = "attempt.json"
WORKFLOW_ATTEMPT_FIELDS = [
    "phase",
    "phase_lifecycle_id",
    "attempt_id",
    "authority_state",
    "reason_category",
    "canonical_output_ref",
]
WORKFLOW_ATTEMPT_REASON = "workflow-in-progress"
EXPECTED_PHASE35_READER_BLOCK = "Phase 38 workflow attempt is blocking"
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
    "workflow-attempt-blocking",
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


def workflow_attempt_payload(attempt_id: str) -> dict[str, str]:
    if not re.fullmatch(r"[0-9a-f]{32}", attempt_id):
        raise WorkflowError("workflow-attempt-blocking")
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "attempt_id": attempt_id,
        "authority_state": "blocked",
        "reason_category": WORKFLOW_ATTEMPT_REASON,
        "canonical_output_ref": PHASE35_OUTPUT.as_posix(),
    }


def _maybe_lstat(candidate: Path) -> Any | None:
    try:
        return candidate.lstat()
    except FileNotFoundError:
        return None
    except OSError as error:
        raise WorkflowError("workflow-attempt-blocking") from error


def validate_workflow_attempt_path(
    root: Path,
    marker_ref: Path = WORKFLOW_ATTEMPT_SHELL,
) -> Path:
    if (
        marker_ref.is_absolute()
        or ".." in marker_ref.parts
        or marker_ref != WORKFLOW_ATTEMPT_SHELL
    ):
        raise WorkflowError("workflow-attempt-blocking")
    root_resolved = root.resolve(strict=False)
    current = root
    for index, part in enumerate(marker_ref.parts):
        current /= part
        maybe_status = _maybe_lstat(current)
        if maybe_status is None:
            continue
        if stat.S_ISLNK(maybe_status.st_mode):
            raise WorkflowError("workflow-attempt-blocking")
        if (
            index < len(marker_ref.parts) - 1
            and not stat.S_ISDIR(maybe_status.st_mode)
        ):
            raise WorkflowError("workflow-attempt-blocking")
    shell = root / marker_ref
    shell_resolved = shell.resolve(strict=False)
    if (
        shell_resolved != root_resolved
        and root_resolved not in shell_resolved.parents
    ):
        raise WorkflowError("workflow-attempt-blocking")
    maybe_shell_status = _maybe_lstat(shell)
    if (
        maybe_shell_status is not None
        and not stat.S_ISDIR(maybe_shell_status.st_mode)
    ):
        raise WorkflowError("workflow-attempt-blocking")
    return shell


def write_workflow_attempt_payload(
    path: Path,
    payload: dict[str, str],
) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def replace_workflow_attempt_payload(source: Path, target: Path) -> None:
    source.replace(target)


def remove_workflow_attempt_shell(path: Path) -> None:
    shutil.rmtree(path)


def load_workflow_attempt_marker(root: Path) -> dict[str, str] | None:
    shell = validate_workflow_attempt_path(root)
    if _maybe_lstat(shell) is None:
        return None
    payload_path = shell / WORKFLOW_ATTEMPT_PAYLOAD_NAME
    maybe_payload_status = _maybe_lstat(payload_path)
    if (
        maybe_payload_status is None
        or stat.S_ISLNK(maybe_payload_status.st_mode)
        or not stat.S_ISREG(maybe_payload_status.st_mode)
    ):
        raise WorkflowError("workflow-attempt-blocking")
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as error:
        raise WorkflowError("workflow-attempt-blocking") from error
    if (
        not isinstance(payload, dict)
        or set(payload) != set(WORKFLOW_ATTEMPT_FIELDS)
    ):
        raise WorkflowError("workflow-attempt-blocking")
    expected = workflow_attempt_payload(
        str(payload.get("attempt_id") or "")
    )
    if payload != expected:
        raise WorkflowError("workflow-attempt-blocking")
    return expected


def require_clear_workflow_attempt_marker(root: Path) -> None:
    if load_workflow_attempt_marker(root) is not None:
        raise WorkflowError("workflow-attempt-blocking")


def publish_workflow_attempt_marker(root: Path, attempt_id: str) -> None:
    payload = workflow_attempt_payload(attempt_id)
    shell = validate_workflow_attempt_path(root)
    try:
        shell.parent.mkdir(parents=True, exist_ok=True)
        shell.mkdir(exist_ok=True)
        validate_workflow_attempt_path(root)
        temporary_payload = shell / f".{WORKFLOW_ATTEMPT_PAYLOAD_NAME}.tmp"
        canonical_payload = shell / WORKFLOW_ATTEMPT_PAYLOAD_NAME
        for candidate in (temporary_payload, canonical_payload):
            maybe_status = _maybe_lstat(candidate)
            if maybe_status is not None and (
                stat.S_ISLNK(maybe_status.st_mode)
                or not stat.S_ISREG(maybe_status.st_mode)
            ):
                raise WorkflowError("workflow-attempt-blocking")
        write_workflow_attempt_payload(temporary_payload, payload)
        replace_workflow_attempt_payload(
            temporary_payload,
            canonical_payload,
        )
        if load_workflow_attempt_marker(root) != payload:
            raise WorkflowError("workflow-attempt-blocking")
    except (OSError, WorkflowError) as error:
        raise WorkflowError("workflow-attempt-blocking") from error


def clear_workflow_attempt_marker(root: Path, attempt_id: str) -> None:
    payload = load_workflow_attempt_marker(root)
    if payload is None or payload["attempt_id"] != attempt_id:
        raise WorkflowError("workflow-attempt-blocking")
    shell = validate_workflow_attempt_path(root)
    try:
        remove_workflow_attempt_shell(shell)
    except OSError as error:
        raise WorkflowError("workflow-attempt-blocking") from error
    if _maybe_lstat(shell) is not None:
        raise WorkflowError("workflow-attempt-blocking")


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


def _load_candidate_final_authority(root: Path) -> FinalAuthority:
    try:
        require_clear_authority_guard(root)
    except WorkflowError:
        return FinalAuthority.unavailable(
            "phase35-authority-guard-blocking"
        )
    output = root / PHASE35_OUTPUT
    if not output.exists():
        return FinalAuthority.unavailable("phase35-authority-missing")
    if output.is_symlink() or not output.is_dir():
        return FinalAuthority.unavailable("phase35-authority-invalid")
    try:
        phase35.validate_mutation_target(
            root,
            PHASE35_OUTPUT,
            PHASE35_OUTPUT,
            "canonical output",
            expect_directory=True,
            allow_missing=False,
        )
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


def load_final_authority(root: Path) -> FinalAuthority:
    try:
        require_clear_workflow_attempt_marker(root)
    except WorkflowError:
        return FinalAuthority.unavailable("workflow-attempt-blocking")
    return _load_candidate_final_authority(root)


def _run_phase34(root: Path, attempt_id: str) -> CommandOutcome:
    try:
        maybe_reason = phase34.run_quick(
            root,
            phase34.DEFAULT_PHASE31_OUTPUT_DIR.as_posix(),
            phase34.DEFAULT_PHASE33_HANDOFF.as_posix(),
            PHASE34_OUTPUT.as_posix(),
            attempt_id,
        )
    except phase34.VerificationError:
        try:
            maybe_state = phase34.load_publication_state(root)
        except phase34.VerificationError:
            maybe_state = None
        if (
            maybe_state is not None
            and maybe_state.get("attempt_id") == attempt_id
        ):
            return CommandOutcome(
                1,
                _safe_reason(
                    maybe_state["reason_category"],
                    "phase34-operation-failed",
                ),
            )
        return CommandOutcome(1, "phase34-operation-failed")
    if maybe_reason is None:
        return CommandOutcome(0, "none")
    return CommandOutcome(1, _safe_reason(maybe_reason, "phase34-operation-failed"))


def _phase34_effective_authority_is_valid(
    root: Path,
    attempt_id: str,
    outcome: CommandOutcome,
) -> bool:
    try:
        maybe_state = phase34.load_publication_state(root)
    except phase34.VerificationError:
        return False
    if outcome.status != 0 and maybe_state is not None:
        return (
            maybe_state.get("attempt_id") == attempt_id
            and maybe_state.get("authority_state") == "blocked"
            and maybe_state.get("reason_category")
            == outcome.reason_category
        )
    if maybe_state is not None:
        return False

    output = root / PHASE34_OUTPUT
    if output.is_symlink() or not output.is_dir():
        return False
    try:
        phase34.validate_generated_outputs(output)
        phase34.validate_output_security(output, PHASE34_OUTPUT.as_posix())
        packet = _load_json_object(
            output / "final-readiness-packet.json"
        )
        manifest = _load_json_object(
            output / "final-readiness-run-manifest.json"
        )
    except (phase34.VerificationError, WorkflowError):
        return False
    normal_authority_valid = (
        packet.get("phase_lifecycle_id") == phase34.PHASE_LIFECYCLE_ID
        and packet.get("readiness_state") in {"blocked", "unblocked"}
    )
    if outcome.status == 0:
        return normal_authority_valid
    return (
        normal_authority_valid
        and packet.get("readiness_state") == "blocked"
        and manifest.get("run_state") == "blocked-source-failure"
        and manifest.get("attempt_id") == attempt_id
        and manifest.get("source_failure_reason_code")
        == outcome.reason_category
    )


def _run_phase35(
    root: Path,
    phase34_outcome: CommandOutcome,
) -> CommandOutcome:
    try:
        if phase34_outcome.status != 0:
            phase35.publish_failed_phase34_bundle(root)
        else:
            phase35.run_quick(
                root,
                PHASE34_OUTPUT.as_posix(),
                PHASE35_OUTPUT.as_posix(),
            )
    except phase35.VerificationError as error:
        if (
            error.reason_code == "unsafe-ref"
            and str(error) == EXPECTED_PHASE35_READER_BLOCK
        ):
            return CommandOutcome(0, "none")
        return CommandOutcome(
            1,
            _safe_reason(error.reason_code, "phase35-operation-failed"),
        )
    return CommandOutcome(0, "none")


def coordinate_workflow(root: Path = ROOT) -> WorkflowResult:
    attempt_id = uuid.uuid4().hex
    try:
        publish_workflow_attempt_marker(root, attempt_id)
        phase35.publish_authority_guard(root)
    except (phase35.VerificationError, WorkflowError):
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

    phase34_outcome = _run_phase34(root, attempt_id)
    if not _phase34_effective_authority_is_valid(
        root,
        attempt_id,
        phase34_outcome,
    ):
        invalid_phase34 = CommandOutcome(
            phase34_outcome.status or 1,
            "phase34-authority-invalid",
        )
        return evaluate_final_status(
            invalid_phase34,
            CommandOutcome(0, "none"),
            FinalAuthority.unavailable("phase34-authority-invalid"),
        )

    phase35_outcome = _run_phase35(root, phase34_outcome)
    candidate = _load_candidate_final_authority(root)
    if phase35_outcome.status == 0 and candidate.available:
        try:
            clear_workflow_attempt_marker(root, attempt_id)
        except WorkflowError:
            phase35_outcome = CommandOutcome(
                1,
                "workflow-attempt-blocking",
            )
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
