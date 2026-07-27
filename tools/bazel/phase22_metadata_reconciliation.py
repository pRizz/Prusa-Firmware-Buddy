#!/usr/bin/env python3
from __future__ import annotations

from phase22_metadata_policy import *


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    for path in [
            CONTRACT_MANIFEST,
            Path("tools/bazel/phase22_metadata_reconciliation.py"),
            Path("tools/bazel/phase22_metadata_reconciliation_test.py")
    ]:
        if not (root / path).exists():
            errors.append(f"missing wiring file: {path}")

    root_build = read_text(root / "BUILD.bazel")
    tools_build = read_text(root / "tools/bazel/BUILD.bazel")
    rust_workflow = read_text(root / "tools/bazel/rust_workflow.sh")
    justfile = read_text(root / "justfile")

    root_markers = [
        'name = "phase22_metadata_reconciliation_docs"',
        'name = "phase22_verify"',
        'actual = "//tools/bazel:phase22_verify"',
        'name = "phase22_verify_tests"',
        'actual = "//tools/bazel:phase22_verify_tests"',
    ]
    for marker in root_markers:
        if marker not in root_build:
            errors.append(f"BUILD.bazel missing Phase 22 marker: {marker}")
    for path in REQUIRED_PHASE22_VALIDATION_DOCS:
        if path not in root_build:
            errors.append(
                f"phase22_metadata_reconciliation_docs missing validation file: {path}"
            )

    tools_markers = [
        'name = "phase22_source_ref_manifests"',
        'name = "phase22_verify"',
        'name = "phase22_verify_tests"',
        "//:phase22_metadata_reconciliation_docs",
    ]
    for marker in tools_markers:
        if marker not in tools_build:
            errors.append(
                f"tools/bazel/BUILD.bazel missing Phase 22 marker: {marker}")
    for path in REQUIRED_PHASE22_SOURCE_REF_MANIFESTS:
        if path not in tools_build:
            errors.append(
                f"phase22_source_ref_manifests missing manifest: {path}")

    workflow_markers = [
        "phase22_verify)",
        "python3 tools/bazel/phase22_metadata_reconciliation.py --wiring-only",
        "python3 tools/bazel/phase22_metadata_reconciliation.py --quick --output-dir build/ci-evidence/phase22",
        "phase22_verify_tests)",
        "python3 tools/bazel/phase22_metadata_reconciliation_test.py",
    ]
    for marker in workflow_markers:
        if marker not in rust_workflow:
            errors.append(
                f"rust_workflow.sh missing Phase 22 marker: {marker}")

    just_markers = [
        "phase22-verify:",
        "bazel run //tools/bazel:phase22_verify_tests",
        "bazel run //tools/bazel:phase22_verify",
    ]
    for marker in just_markers:
        if marker not in justfile:
            errors.append(f"justfile missing Phase 22 marker: {marker}")

    if errors:
        raise VerificationError("\n".join(errors))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def prepare_output_dir(root: Path, output_dir: Path) -> Path:
    full_output_dir = validate_output_dir(root, output_dir)
    maybe_symlink = has_symlink_descendant(full_output_dir)
    if maybe_symlink is not None:
        raise VerificationError(
            f"output directory contains symlink descendant: {maybe_symlink.relative_to(root)}"
        )
    if full_output_dir.exists():
        if not full_output_dir.is_dir():
            raise VerificationError(
                f"output path exists but is not a directory: {full_output_dir.relative_to(root)}"
            )
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=False)
    return full_output_dir


def correction_report_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_row in require_list(contract.get("metadata_corrections"),
                                "metadata_corrections"):
        if not isinstance(raw_row, dict):
            continue
        rows.append({
            "id":
            raw_row.get("id"),
            "target_file":
            raw_row.get("target_file"),
            "status":
            "corrected",
            "correction_type":
            raw_row.get("correction_type"),
            "source_refs":
            raw_row.get("source_refs", []),
            "required_new_markers":
            raw_row.get("required_new_markers", []),
        })
    return rows


def copy_sanitized_source_snapshots(root: Path, contract: dict[str, Any],
                                    output_dir: Path) -> None:
    snapshot_root = output_dir / "sanitized-source-snapshots"
    errors: list[str] = []
    for snapshot in require_list(contract.get("sanitized_source_snapshots"),
                                 "sanitized_source_snapshots"):
        if not isinstance(snapshot,
                          str) or not is_safe_relative_path(snapshot):
            errors.append(
                f"sanitized_source_snapshots unsafe path: {snapshot}")
            continue
        source_path = root / snapshot
        if not source_path.exists():
            errors.append(
                f"sanitized_source_snapshots missing source: {snapshot}")
            continue
        text = read_text(source_path)
        errors.extend(
            check_file_security_text(Path(snapshot), text,
                                     broad_markers=False))
        destination = snapshot_root / snapshot
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)

    if errors:
        raise VerificationError("\n".join(errors))


def write_quick_artifacts(root: Path, contract: dict[str, Any],
                          output_dir: Path, readiness: dict[str, Any]) -> None:
    full_output_dir = prepare_output_dir(root, output_dir)
    generated_at_utc = utc_now()
    corrections = correction_report_rows(contract)

    metadata_report = {
        "artifact_name": "phase22-metadata-reconciliation",
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": generated_at_utc,
        "requirements": contract.get("requirements", []),
        "correction_count": len(corrections),
        "corrections": corrections,
    }
    readiness_report = dict(readiness)
    readiness_report["generated_at_utc"] = generated_at_utc

    redacted_summary = "\n".join([
        "# Phase 22 Metadata Reconciliation",
        "",
        "Phase 22 reconciles source-backed planning metadata and writes an audit-rerun readiness report.",
        "",
        ("Phase 22 reconciles metadata only; hardware, live-service, release signing, upstream-result pass evidence, "
         "maintainer decisions, final demotion, and milestone archival remain governed by their validated inputs."
         ),
        "",
    ])

    write_json(full_output_dir / "metadata-reconciliation-report.json",
               metadata_report)
    write_json(full_output_dir / "audit-rerun-readiness.json",
               readiness_report)
    (full_output_dir / "redacted-summary.md").write_text(redacted_summary,
                                                         encoding="utf-8")
    copy_sanitized_source_snapshots(root, contract, full_output_dir)


def run_quick(root: Path, output_dir: Path) -> None:
    contract = check_contract(root)
    check_requirements(root)
    check_validation(root)
    check_roadmap_state(root)
    check_security(root, output_dir)
    check_wiring(root)
    readiness = check_audit_readiness(root, metadata_corrected=True)
    write_quick_artifacts(root, contract, output_dir, readiness)
    check_security(root, output_dir)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify Phase 22 metadata reconciliation evidence.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--requirements-only", action="store_true")
    parser.add_argument("--validation-only", action="store_true")
    parser.add_argument("--roadmap-state-only", action="store_true")
    parser.add_argument("--audit-readiness-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path.cwd()
    output_dir = Path(args.output_dir)

    try:
        if args.contract_only:
            check_contract(root)
        elif args.requirements_only:
            check_requirements(root)
        elif args.validation_only:
            check_validation(root)
        elif args.roadmap_state_only:
            check_roadmap_state(root)
        elif args.audit_readiness_only:
            check_audit_readiness(root)
        elif args.security_only:
            check_security(root, output_dir)
        elif args.wiring_only:
            check_wiring(root)
        elif args.quick:
            run_quick(root, output_dir)
        else:
            check_contract(root)
    except VerificationError as error:
        print(error)
        return 1

    print("phase22 metadata reconciliation verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
