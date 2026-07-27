from __future__ import annotations


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def publication_state_payload(
    attempt_id: str,
    reason_category: str,
) -> dict[str, str]:
    if not re.fullmatch(r"[0-9a-f]{32}", attempt_id):
        raise VerificationError("Phase 34 publication state is blocking")
    if reason_category not in SOURCE_FAILURE_REASON_CODES:
        raise VerificationError("Phase 34 publication state is blocking")
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "attempt_id": attempt_id,
        "authority_state": "blocked",
        "reason_category": reason_category,
        "canonical_output_ref": DEFAULT_OUTPUT_DIR.as_posix(),
    }


def _maybe_lstat(candidate: Path) -> Any | None:
    try:
        return candidate.lstat()
    except FileNotFoundError:
        return None
    except OSError as error:
        raise VerificationError(
            "Phase 34 publication state is blocking") from error


def validate_publication_state_path(
    root: Path,
    marker_ref: Path = PUBLICATION_STATE_SHELL,
) -> Path:
    if (marker_ref.is_absolute() or ".." in marker_ref.parts
            or marker_ref != PUBLICATION_STATE_SHELL):
        raise VerificationError("Phase 34 publication state is blocking")
    root_resolved = root.resolve(strict=False)
    current = root
    for index, part in enumerate(marker_ref.parts):
        current /= part
        maybe_status = _maybe_lstat(current)
        if maybe_status is None:
            continue
        if stat.S_ISLNK(maybe_status.st_mode):
            raise VerificationError("Phase 34 publication state is blocking")
        if (index < len(marker_ref.parts) - 1
                and not stat.S_ISDIR(maybe_status.st_mode)):
            raise VerificationError("Phase 34 publication state is blocking")
    marker = root / marker_ref
    marker_resolved = marker.resolve(strict=False)
    if (marker_resolved != root_resolved
            and root_resolved not in marker_resolved.parents):
        raise VerificationError("Phase 34 publication state is blocking")
    maybe_marker_status = _maybe_lstat(marker)
    if (maybe_marker_status is not None
            and not stat.S_ISDIR(maybe_marker_status.st_mode)):
        raise VerificationError("Phase 34 publication state is blocking")
    return marker


def write_publication_state_payload(
    path: Path,
    payload: dict[str, str],
) -> None:
    write_json(path, payload)


def replace_publication_state_payload(source: Path, target: Path) -> None:
    source.replace(target)


def remove_publication_state_shell(path: Path) -> None:
    shutil.rmtree(path)


def load_publication_state(root: Path) -> dict[str, str] | None:
    shell = validate_publication_state_path(root)
    if _maybe_lstat(shell) is None:
        return None
    payload_path = shell / PUBLICATION_STATE_PAYLOAD_NAME
    maybe_payload_status = _maybe_lstat(payload_path)
    if (maybe_payload_status is None
            or stat.S_ISLNK(maybe_payload_status.st_mode)
            or not stat.S_ISREG(maybe_payload_status.st_mode)):
        raise VerificationError("Phase 34 publication state is blocking")
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as error:
        raise VerificationError(
            "Phase 34 publication state is blocking") from error
    if (not isinstance(payload, dict)
            or set(payload) != set(PUBLICATION_STATE_FIELDS)):
        raise VerificationError("Phase 34 publication state is blocking")
    expected = publication_state_payload(
        str(payload.get("attempt_id") or ""),
        str(payload.get("reason_category") or ""),
    )
    if payload != expected:
        raise VerificationError("Phase 34 publication state is blocking")
    return expected


def ensure_no_publication_state(root: Path) -> None:
    if load_publication_state(root) is not None:
        raise VerificationError("Phase 34 publication state is blocking")


def publish_publication_state(
    root: Path,
    attempt_id: str,
    reason_category: str,
) -> None:
    payload = publication_state_payload(attempt_id, reason_category)
    shell = validate_publication_state_path(root)
    try:
        shell.parent.mkdir(parents=True, exist_ok=True)
        shell.mkdir(exist_ok=True)
        validate_publication_state_path(root)
        temporary_payload = shell / f".{PUBLICATION_STATE_PAYLOAD_NAME}.tmp"
        canonical_payload = shell / PUBLICATION_STATE_PAYLOAD_NAME
        for candidate in (temporary_payload, canonical_payload):
            maybe_status = _maybe_lstat(candidate)
            if maybe_status is not None and (
                    stat.S_ISLNK(maybe_status.st_mode)
                    or not stat.S_ISREG(maybe_status.st_mode)):
                raise VerificationError(
                    "Phase 34 publication state is blocking")
        write_publication_state_payload(temporary_payload, payload)
        replace_publication_state_payload(
            temporary_payload,
            canonical_payload,
        )
        if load_publication_state(root) != payload:
            raise VerificationError("Phase 34 publication state is blocking")
    except (OSError, VerificationError) as error:
        raise VerificationError(
            "Phase 34 publication state is blocking") from error


def clear_publication_state(root: Path, attempt_id: str) -> None:
    payload = load_publication_state(root)
    if payload is None or payload["attempt_id"] != attempt_id:
        raise VerificationError("Phase 34 publication state is blocking")
    shell = validate_publication_state_path(root)
    try:
        remove_publication_state_shell(shell)
    except OSError as error:
        raise VerificationError(
            "Phase 34 publication state is blocking") from error
    if _maybe_lstat(shell) is not None:
        raise VerificationError("Phase 34 publication state is blocking")
