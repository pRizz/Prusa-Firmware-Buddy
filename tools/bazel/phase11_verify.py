#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from phase11_contract_policy import *  # noqa: F403


def check_requirements(root: Path) -> None:
    manifest_text = read_text(root, REQUIREMENT_EVIDENCE_MANIFEST)
    rows = require_top_level(root, REQUIREMENT_EVIDENCE_MANIFEST,
                             "requirement_evidence")
    required_requirement_ids = extract_v1_requirement_ids(root)
    require_exact_row_ids(rows, set(REQUIRED_REQUIREMENT_ROWS),
                          REQUIREMENT_EVIDENCE_MANIFEST)
    actual_requirement_ids: set[str] = set()
    errors: list[str] = []
    fields = [
        "id",
        "requirement_id",
        "owning_phase",
        "source_artifacts",
        "verifier_command_or_evidence_class",
        "current_status",
        "cutover_status",
        "intentional_delta_status",
        "retained_code_justification",
        "required_non_local_evidence",
        "cutover_blocker",
        "proof_scope",
        "phase_lifecycle_id",
    ]
    later_artifacts_exist = later_phase_artifacts_exist(root)
    try:
        require_no_stale_plan_markers_after_later_artifacts(
            root,
            REQUIREMENT_EVIDENCE_MANIFEST,
            manifest_text,
        )
    except VerificationError as error:
        errors.append(str(error))
    for row in rows:
        row_name = f"{REQUIREMENT_EVIDENCE_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, fields, row_name,
                           {"required_non_local_evidence", "cutover_blocker"})
            row_id = require_string(row, "id", row_name)
            expected_requirement_id = REQUIRED_REQUIREMENT_ROWS[row_id]
            requirement_id = require_string(row, "requirement_id", row_name)
            if requirement_id != expected_requirement_id:
                raise VerificationError(
                    f"{row_name} requirement_id must be {expected_requirement_id}"
                )
            actual_requirement_ids.add(requirement_id)
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(
                    f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
                )
            proof_scope = require_string(row, "proof_scope", row_name)
            if proof_scope not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(
                    f"{row_name} proof_scope is not allowed: {proof_scope}")
            require_required_non_local_evidence(row, row_name, proof_scope)
            source_artifacts = require_non_empty_list_of_strings(
                row, "source_artifacts", row_name)
            if source_artifacts == [".planning/ROADMAP.md"]:
                raise VerificationError(
                    f"{row_name} must not use roadmap-only evidence")
            if row.get("verifier_command_or_evidence_class") == "roadmap-only":
                raise VerificationError(
                    f"{row_name} must not use roadmap-only evidence")
            require_source_artifacts(root, row, row_name)
            if requirement_id in PENDING_REQUIREMENT_IDS:
                current_status = require_string(row, "current_status",
                                                row_name)
                has_named_blocker = not is_missing(row.get("cutover_blocker"))
                has_non_local_evidence = not is_missing(
                    row.get("required_non_local_evidence"))
                if current_status != "source-backed-local-passed" and not has_named_blocker and not has_non_local_evidence:
                    raise VerificationError(
                        f"{row_name} missing pending-requirement handling for {requirement_id}"
                    )
            if later_artifacts_exist and requirement_id == "VERF-03":
                require_final_verf03_row(row, row_name)
            if later_artifacts_exist and requirement_id == "VERF-05":
                require_final_verf05_row(row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    missing_requirements = sorted(required_requirement_ids -
                                  actual_requirement_ids)
    extra_requirements = sorted(actual_requirement_ids -
                                required_requirement_ids)
    if missing_requirements:
        errors.append("missing v1 requirement IDs: " +
                      ", ".join(missing_requirements))
    if extra_requirements:
        errors.append("unexpected requirement IDs: " +
                      ", ".join(extra_requirements))
    if errors:
        raise VerificationError("\n".join(errors))


def check_comparisons(root: Path) -> None:
    rows = require_top_level(root, REFERENCE_COMPARISONS_MANIFEST,
                             "reference_comparisons")
    require_exact_row_ids(rows, REQUIRED_COMPARISON_ROW_IDS,
                          REFERENCE_COMPARISONS_MANIFEST)
    fields = [
        "id",
        "requirement_id",
        "comparison_kind",
        "normalization_rule",
        "byte_identity_claim",
        "reference_command_policy",
        "guard_environment",
        "source_artifacts",
        "required_non_local_evidence",
        "secret_handling",
        "proof_scope",
        "phase_lifecycle_id",
    ]
    errors: list[str] = []
    for row in rows:
        row_name = f"{REFERENCE_COMPARISONS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, fields, row_name,
                           {"required_non_local_evidence"})
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(
                    f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
                )
            if row.get("secret_handling") != "name-only-or-redacted":
                raise VerificationError(
                    f"{row_name} secret_handling must be name-only-or-redacted"
                )
            proof_scope = require_string(row, "proof_scope", row_name)
            if proof_scope not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(
                    f"{row_name} proof_scope is not allowed: {proof_scope}")
            require_required_non_local_evidence(row, row_name, proof_scope)
            comparison_kind = require_string(row, "comparison_kind", row_name)
            if comparison_kind not in ALLOWED_REFERENCE_COMPARISON_KINDS:
                raise VerificationError(
                    f"{row_name} comparison_kind is not allowed: {comparison_kind}"
                )
            byte_identity_claim = row.get("byte_identity_claim")
            if not isinstance(byte_identity_claim, bool):
                raise VerificationError(
                    f"{row_name} byte_identity_claim must be a boolean")
            if comparison_kind == "normalized-semantic" and byte_identity_claim:
                raise VerificationError(
                    f"{row_name} normalized comparisons must not claim byte identity"
                )
            if comparison_kind == "byte-identity-with-fixture" and not byte_identity_claim:
                raise VerificationError(
                    f"{row_name} byte identity comparisons must set byte_identity_claim true"
                )
            if byte_identity_claim:
                if is_missing(row.get("reference_fixture")) or is_missing(
                        row.get("normalization_rule")):
                    raise VerificationError(
                        f"{row_name} byte_identity_claim true requires reference_fixture and normalization_rule"
                    )
            policy = require_string(row, "reference_command_policy", row_name)
            if "reference-only" in policy and row.get(
                    "guard_environment") != "BUDDY_BAZEL_EXECUTE_REFERENCE=1":
                raise VerificationError(
                    f"{row_name} reference-only commands must be guarded")
            require_source_artifacts(root, row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_cutover(root: Path) -> None:
    errors: list[str] = []
    cutover_rows: list[dict[str, object]] = []
    known_concern_rows: list[dict[str, object]] = []
    retained_rows: list[dict[str, object]] = []
    try:
        cutover_rows = require_top_level(root, CUTOVER_READINESS_MANIFEST,
                                         "cutover_criteria")
        require_exact_row_ids(
            cutover_rows,
            REQUIRED_CUTOVER_CRITERION_ROW_IDS,
            CUTOVER_READINESS_MANIFEST,
        )
    except VerificationError as error:
        errors.append(str(error))
    try:
        known_concern_rows = require_top_level(
            root,
            CUTOVER_READINESS_MANIFEST,
            "known_concern_dispositions",
        )
        require_exact_row_ids(
            known_concern_rows,
            REQUIRED_KNOWN_CONCERN_ROW_IDS,
            CUTOVER_READINESS_MANIFEST,
        )
    except VerificationError as error:
        errors.append(str(error))
    try:
        retained_rows = require_top_level(
            root,
            RETAINED_CODE_JUSTIFICATIONS_MANIFEST,
            "retained_code_justifications",
        )
        require_exact_row_ids(
            retained_rows,
            REQUIRED_RETAINED_CODE_ROW_IDS,
            RETAINED_CODE_JUSTIFICATIONS_MANIFEST,
        )
    except VerificationError as error:
        errors.append(str(error))
    cutover_fields = [
        "id",
        "requirement_id",
        "criterion",
        "status",
        "blocking_reason",
        "source_artifacts",
        "verifier_commands",
        "required_evidence",
        "demotion_allowed",
        "proof_scope",
        "phase_lifecycle_id",
    ]
    known_concern_fields = [
        "id",
        "source_artifacts",
        "disposition",
        "phase11_handling",
        "regression_guard",
        "proof_scope",
        "secret_handling",
        "phase_lifecycle_id",
    ]
    retained_fields = [
        "id",
        "requirement_id",
        "retained_surface",
        "owner",
        "disposition",
        "justification",
        "boundary",
        "safe_facade_or_contract",
        "source_artifacts",
        "required_evidence",
        "proof_scope",
        "secret_handling",
        "phase_lifecycle_id",
    ]
    for row in cutover_rows:
        row_name = f"{CUTOVER_READINESS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, cutover_fields, row_name)
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(
                    f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
                )
            if row.get("proof_scope") not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(
                    f"{row_name} proof_scope is not allowed: {row.get('proof_scope')}"
                )
            require_non_empty_list_of_strings(row, "verifier_commands",
                                              row_name)
            require_non_empty_list_of_strings(row, "required_evidence",
                                              row_name)
            if row.get("id") == "criteria-reference-demotion-blocked":
                if row.get("status") != "not-cutover-ready":
                    raise VerificationError(
                        f"{row_name} status must remain not-cutover-ready")
                if row.get("demotion_allowed") is not False:
                    raise VerificationError(
                        f"{row_name} must keep demotion_allowed false")
            if row.get("demotion_allowed") is True and row.get(
                    "status") != "passed-local":
                raise VerificationError(
                    f"{row_name} demotion_allowed must stay false until status is passed-local"
                )
            require_source_artifacts(root, row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    for row in known_concern_rows:
        row_name = f"{CUTOVER_READINESS_MANIFEST.as_posix()} known concern {row.get('id', '<unknown>')}"
        try:
            require_fields(row, known_concern_fields, row_name)
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(
                    f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
                )
            proof_scope = require_string(row, "proof_scope", row_name)
            if proof_scope not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(
                    f"{row_name} proof_scope is not allowed: {proof_scope}")
            if row.get("secret_handling") != "name-only-or-redacted":
                raise VerificationError(
                    f"{row_name} secret_handling must be name-only-or-redacted"
                )
            disposition = require_string(row, "disposition", row_name)
            if disposition not in ALLOWED_KNOWN_CONCERN_DISPOSITIONS:
                raise VerificationError(
                    f"{row_name} disposition is not allowed: {disposition}")
            require_source_artifacts(root, row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    for row in retained_rows:
        row_name = (
            f"{RETAINED_CODE_JUSTIFICATIONS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        )
        try:
            require_fields(row, retained_fields, row_name)
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(
                    f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
                )
            if row.get("proof_scope") != "retained-code-justification":
                raise VerificationError(
                    f"{row_name} proof_scope must be retained-code-justification"
                )
            require_non_empty_list_of_strings(row, "required_evidence",
                                              row_name)
            if row.get("secret_handling") != "name-only-or-redacted":
                raise VerificationError(
                    f"{row_name} secret_handling must be name-only-or-redacted"
                )
            if row.get("disposition") not in {
                    "accepted", "blocked", "deferred"
            }:
                raise VerificationError(
                    f"{row_name} disposition must be accepted, blocked, or deferred"
                )
            require_source_artifacts(root, row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def existing_security_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    manifest_dir = root / "tools/bazel/manifests"
    if manifest_dir.exists():
        paths.extend(
            path.relative_to(root)
            for path in sorted(manifest_dir.glob("phase11_*.json")))
    phase_dirs = [PHASE11_DOC_DIR]
    maybe_archived_phase_dir = maybe_archived_phase_path(PHASE11_DOC_DIR)
    if maybe_archived_phase_dir is not None:
        phase_dirs.append(maybe_archived_phase_dir)
    for phase_dir in phase_dirs:
        if not (root / phase_dir).exists():
            continue
        phase_doc_patterns = [
            "11-CONTEXT.md",
            "11-RESEARCH.md",
            "11-VALIDATION.md",
            "11-VERIFICATION.md",
            "11-*-SUMMARY.md",
        ]
        for pattern in phase_doc_patterns:
            paths.extend(
                path.relative_to(root)
                for path in sorted((root / phase_dir).glob(pattern)))
    return paths


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in existing_security_paths(root):
        try:
            reject_forbidden_text(path, read_text(root, path))
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_rust(root: Path) -> None:
    cutover_text = read_text(root, CUTOVER_RUST)
    lib_text = read_text(root, RUST_DOMAIN_LIB)
    errors: list[str] = []
    if "pub mod cutover;" not in lib_text:
        errors.append(
            f"{RUST_DOMAIN_LIB.as_posix()} must export pub mod cutover;")
    for api_string in sorted(REQUIRED_RUST_API_STRINGS):
        if api_string not in cutover_text:
            errors.append(
                f"{CUTOVER_RUST.as_posix()} missing Rust API surface: {api_string}"
            )
    for label, pattern in UNSAFE_RUST_PATTERNS.items():
        if pattern in cutover_text:
            errors.append(
                f"{CUTOVER_RUST.as_posix()} contains {label}: {pattern}")
    if errors:
        raise VerificationError("\n".join(errors))


def require_file_contains(root: Path, path: Path,
                          needles: list[str]) -> list[str]:
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    return [
        f"{path.as_posix()} missing required wiring text: {needle}"
        for needle in needles if needle not in text
    ]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase11_verify"',
                'name = "phase11_verify_tests"',
                "phase11_parity_pyramid.json",
                "phase11_requirement_evidence.json",
                "phase11_reference_comparisons.json",
                "phase11_cutover_readiness.json",
                "phase11_retained_code_justifications.json",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase11_verify)",
                "python3 tools/bazel/phase11_verify.py --wiring-only",
                "python3 tools/bazel/phase11_verify.py --quick",
                "phase11_verify_tests)",
                "python3 tools/bazel/phase11_verify_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase11_cutover_evidence_docs"',
                'name = "phase11_verify"',
                'name = "phase11_verify_tests"',
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase11-verify:",
                "bazel run //tools/bazel:phase11_verify_tests",
                "bazel run //tools/bazel:phase11_verify",
                "bazel run //tools/bazel:rust_format_check",
                "bazel run //tools/bazel:rust_lint",
                "bazel run //tools/bazel:rust_build",
                "bazel run //tools/bazel:rust_unit_tests",
            ],
        ))
    if errors:
        raise VerificationError("\n".join(errors))


def check_quick(root: Path) -> None:
    collect_errors([
        lambda: check_pyramid(root),
        lambda: check_requirements(root),
        lambda: check_comparisons(root),
        lambda: check_cutover(root),
        lambda: check_security(root),
        lambda: check_rust(root),
    ])


def run_command(root: Path, command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise VerificationError(
            f"{' '.join(command)} failed with exit code {result.returncode}\n{result.stdout}"
        )


def check_all(root: Path) -> None:
    collect_errors([
        lambda: check_quick(root),
        lambda: check_wiring(root),
    ])
    run_command(root, ["cargo", "fmt", "--all", "--", "--check"])
    run_command(root, [
        "cargo", "clippy", "--all-targets", "--all-features", "--", "-D",
        "warnings"
    ])
    run_command(root, ["cargo", "build", "--all-targets", "--all-features"])
    run_command(root, ["cargo", "test", "--all-features"])


def collect_errors(checks: list[object]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify Phase 11 parity pyramid and cutover evidence.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to inspect; useful for wiring fixtures.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="run local deterministic Phase 11 aggregate checks",
    )
    parser.add_argument("--all",
                        action="store_true",
                        help="run all Phase 11 verification modes")
    parser.add_argument("--pyramid-only",
                        action="store_true",
                        help="verify only the parity pyramid")
    parser.add_argument("--requirements-only",
                        action="store_true",
                        help="verify only requirement evidence")
    parser.add_argument("--comparison-only",
                        action="store_true",
                        help="verify only reference comparisons")
    parser.add_argument("--cutover-only",
                        action="store_true",
                        help="verify only cutover readiness")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="verify only secret and overclaim scans")
    parser.add_argument("--rust-only",
                        action="store_true",
                        help="verify only Rust cutover contracts")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="verify only Bazel/just wiring")
    return parser.parse_args()


def selected_checks(root: Path, args: argparse.Namespace) -> list[object]:
    checks: list[object] = []
    if args.all:
        checks.append(lambda: check_all(root))
    if args.quick:
        checks.append(lambda: check_quick(root))
    if args.pyramid_only:
        checks.append(lambda: check_pyramid(root))
    if args.requirements_only:
        checks.append(lambda: check_requirements(root))
    if args.comparison_only:
        checks.append(lambda: check_comparisons(root))
    if args.cutover_only:
        checks.append(lambda: check_cutover(root))
    if args.security_only:
        checks.append(lambda: check_security(root))
    if args.rust_only:
        checks.append(lambda: check_rust(root))
    if args.wiring_only:
        checks.append(lambda: check_wiring(root))
    if not checks:
        checks.append(lambda: check_quick(root))
    return checks


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else ROOT
    try:
        collect_errors(selected_checks(root, args))
    except VerificationError as error:
        print(f"Phase 11 parity/cutover verification failed:\n{error}")
        return 1
    print("Phase 11 parity/cutover verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
