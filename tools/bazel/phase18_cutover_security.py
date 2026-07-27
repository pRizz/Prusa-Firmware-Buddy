from __future__ import annotations

from phase18_cutover_artifacts import normalize_final_results, normalize_retained_reviews
from phase18_cutover_contract import *
from phase18_cutover_policy import *
from phase18_cutover_upstream_policy import *
from phase18_cutover_validation import *


def generated_artifacts_to_scan(root: Path,
                                output_dir: Path | None = None) -> list[Path]:
    scan_dir = output_dir or root / DEFAULT_OUTPUT_DIR
    paths: list[Path] = []
    for artifact in sorted(REQUIRED_GENERATED_ARTIFACTS):
        full_path = scan_dir / artifact
        if full_path.exists():
            paths.append(full_path)
    return paths


def run_security_scan(
    root: Path,
    maybe_decision_input_path: str | None,
    maybe_upstream_results_path: str | None,
    output_dir: Path | None = None,
    decision_input_validated: bool = False,
    upstream_results_validated: bool = False,
    expected_demotion_allowed: bool | None = None,
    expected_final_statuses: dict[str, str] | None = None,
    expected_final_allows: dict[str, bool] | None = None,
    expected_retained_statuses: dict[str, str] | None = None,
    expected_upstream_statuses: dict[str, str] | None = None,
    contract: dict[str, Any] | None = None,
) -> None:
    errors: list[str] = []
    for path in [CONTRACT_MANIFEST]:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_json_fields(load_json(root, path),
                                         path.as_posix())
        except VerificationError as error:
            errors.append(str(error))
    if maybe_decision_input_path:
        try:
            decision_input = load_decision_input(root,
                                                 maybe_decision_input_path)
            decision_input_validated = True
        except VerificationError as error:
            errors.append(str(error))
    upstream_results = None
    if maybe_upstream_results_path:
        try:
            upstream_results = load_upstream_results(
                root, maybe_upstream_results_path)
            upstream_results_validated = True
        except VerificationError as error:
            errors.append(str(error))
    if contract is not None and not errors:
        try:
            decision_input = load_decision_input(
                root, maybe_decision_input_path
            ) if maybe_decision_input_path else None
            packets = contract_packets(contract)
            criteria = contract_final_criteria(contract)
            upstream_requirements = requirements_by_criterion(contract)
            retained_reviews, final_decisions = validated_decision_maps(
                decision_input, packets, criteria)
            validate_retained_acceptance_consistency(packets, retained_reviews,
                                                     final_decisions)
            expected_upstream = normalize_upstream_consumption(
                criteria, upstream_results, upstream_requirements,
                final_decisions)
            expected_results = normalize_final_results(criteria,
                                                       final_decisions,
                                                       expected_upstream)
            expected_retained_rows = normalize_retained_reviews(
                packets, retained_reviews)
            expected_demotion_allowed = demotion_allowed(
                decision_input is not None,
                upstream_results is not None,
                expected_results,
            )
            expected_final_statuses = {
                row["id"]: row["status"]
                for row in expected_results
            }
            expected_final_allows = {
                row["id"]: bool(row["demotion_status_allows_cutover"])
                for row in expected_results
            }
            expected_retained_statuses = {
                row["id"]: row["status"]
                for row in expected_retained_rows
            }
            expected_upstream_statuses = {
                row["criterion_id"]: row["upstream_result_status"]
                for row in expected_upstream.values()
            }
        except VerificationError as error:
            errors.append(str(error))
    for full_path in generated_artifacts_to_scan(root, output_dir):
        relative_path = full_path.relative_to(root)
        try:
            text = full_path.read_text(encoding="utf-8")
            reject_forbidden_text(relative_path, text)
            if full_path.suffix == ".json":
                reject_forbidden_json_fields(json.loads(text),
                                             relative_path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    validate_generated_overclaim_guards(
        root,
        errors,
        output_dir,
        decision_input_validated,
        upstream_results_validated,
        expected_demotion_allowed,
        expected_final_statuses,
        expected_final_allows,
        expected_retained_statuses,
        expected_upstream_statuses,
    )
    if errors:
        raise VerificationError("\n".join(errors))


def validate_generated_overclaim_guards(
    root: Path,
    errors: list[str],
    output_dir: Path | None = None,
    decision_input_validated: bool = False,
    upstream_results_validated: bool = False,
    expected_demotion_allowed: bool | None = None,
    expected_final_statuses: dict[str, str] | None = None,
    expected_final_allows: dict[str, bool] | None = None,
    expected_retained_statuses: dict[str, str] | None = None,
    expected_upstream_statuses: dict[str, str] | None = None,
) -> None:
    output_dir = output_dir or root / DEFAULT_OUTPUT_DIR
    run_manifest_path = output_dir / "run-manifest.json"
    if not run_manifest_path.exists():
        return
    try:
        run_manifest = json.loads(
            run_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(
            f"{run_manifest_path.relative_to(root).as_posix()} is not valid JSON: {error}"
        )
        return
    if not isinstance(run_manifest, dict):
        errors.append(
            "build/ci-evidence/phase18/run-manifest.json must contain an object"
        )
        return
    decision_inputs_supplied = run_manifest.get("decision_inputs_supplied")
    if not isinstance(decision_inputs_supplied, bool):
        errors.append(
            "generated run-manifest.json decision_inputs_supplied must be boolean"
        )
        return
    upstream_results_supplied = run_manifest.get("upstream_results_supplied")
    if not isinstance(upstream_results_supplied, bool):
        errors.append(
            "generated run-manifest.json upstream_results_supplied must be boolean"
        )
        return
    if decision_inputs_supplied and not decision_input_validated:
        errors.append(
            "generated run-manifest.json claims decision input without validated --decision-input"
        )
        return
    if upstream_results_supplied and not upstream_results_validated:
        errors.append(
            "generated run-manifest.json claims upstream results without validated --upstream-results"
        )
        return
    if decision_inputs_supplied or upstream_results_supplied:
        if expected_demotion_allowed is not True and run_manifest.get(
                "demotion_allowed") is True:
            errors.append(
                "generated run-manifest.json demotion_allowed true requires complete decision input and upstream results"
            )
        normalized_path = output_dir / "normalized-final-demotion-results.json"
        if normalized_path.exists():
            try:
                normalized = json.loads(
                    normalized_path.read_text(encoding="utf-8"))
                if isinstance(
                        normalized, dict
                ) and expected_demotion_allowed is not True and normalized.get(
                        "demotion_allowed") is True:
                    errors.append(
                        "generated normalized-final-demotion-results.json demotion_allowed true requires complete decision input and upstream results"
                    )
                results = normalized.get("results") if isinstance(
                    normalized, dict) else None
                if expected_final_statuses is not None and isinstance(
                        results, list):
                    for row in results:
                        if not isinstance(row, dict):
                            continue
                        row_id = str(row.get("id", "unknown"))
                        expected_status = expected_final_statuses.get(row_id)
                        if expected_status is not None and row.get(
                                "status") != expected_status:
                            errors.append(
                                f"generated final criterion status mismatch: {row_id}"
                            )
                        expected_allows = expected_final_allows.get(
                            row_id
                        ) if expected_final_allows is not None else None
                        if expected_allows is not None and row.get(
                                "demotion_status_allows_cutover"
                        ) != expected_allows:
                            errors.append(
                                f"generated final criterion demotion flag mismatch: {row_id}"
                            )
            except json.JSONDecodeError as error:
                errors.append(
                    f"{normalized_path.relative_to(root).as_posix()} is not valid JSON: {error}"
                )
        upstream_path = output_dir / "upstream-result-consumption.json"
        if upstream_path.exists():
            try:
                upstream = json.loads(
                    upstream_path.read_text(encoding="utf-8"))
                results = upstream.get("results") if isinstance(
                    upstream, dict) else None
                if expected_upstream_statuses is not None and isinstance(
                        results, list):
                    for row in results:
                        if not isinstance(row, dict):
                            continue
                        row_id = str(row.get("criterion_id", "unknown"))
                        expected_status = expected_upstream_statuses.get(
                            row_id)
                        if expected_status is not None and row.get(
                                "upstream_result_status") != expected_status:
                            errors.append(
                                f"generated upstream result status mismatch: {row_id}"
                            )
            except json.JSONDecodeError as error:
                errors.append(
                    f"{upstream_path.relative_to(root).as_posix()} is not valid JSON: {error}"
                )
        retained_path = output_dir / "retained-code-acceptance-summary.json"
        if retained_path.exists():
            try:
                retained = json.loads(
                    retained_path.read_text(encoding="utf-8"))
                packets = retained.get("packets") if isinstance(
                    retained, dict) else None
                if expected_retained_statuses is not None and isinstance(
                        packets, list):
                    for row in packets:
                        if not isinstance(row, dict):
                            continue
                        row_id = str(row.get("id", "unknown"))
                        expected_status = expected_retained_statuses.get(
                            row_id)
                        if expected_status is not None and row.get(
                                "status") != expected_status:
                            errors.append(
                                f"generated retained-code packet status mismatch: {row_id}"
                            )
            except json.JSONDecodeError as error:
                errors.append(
                    f"{retained_path.relative_to(root).as_posix()} is not valid JSON: {error}"
                )
        return
    if run_manifest.get("demotion_allowed") is True:
        errors.append(
            "generated no-decision run-manifest.json cannot set demotion_allowed true"
        )
    normalized_path = output_dir / "normalized-final-demotion-results.json"
    if normalized_path.exists():
        try:
            normalized = json.loads(
                normalized_path.read_text(encoding="utf-8"))
            if isinstance(normalized,
                          dict) and normalized.get("demotion_allowed") is True:
                errors.append(
                    "generated no-decision normalized-final-demotion-results.json cannot set demotion_allowed true"
                )
            results = normalized.get("results") if isinstance(
                normalized, dict) else None
            if isinstance(results, list):
                for row in results:
                    if not isinstance(row, dict):
                        continue
                    if row.get("status") in ALLOWED_DEMOTION_STATUSES:
                        errors.append(
                            "generated no-decision normalized-final-demotion-results.json cannot set "
                            f"{row.get('id', 'unknown')} to {row.get('status')}"
                        )
                    if row.get("demotion_status_allows_cutover") is True:
                        errors.append(
                            "generated no-decision normalized-final-demotion-results.json cannot set "
                            f"{row.get('id', 'unknown')} demotion_status_allows_cutover true"
                        )
        except json.JSONDecodeError as error:
            errors.append(
                f"{normalized_path.relative_to(root).as_posix()} is not valid JSON: {error}"
            )
    retained_path = output_dir / "retained-code-acceptance-summary.json"
    if retained_path.exists():
        try:
            retained = json.loads(retained_path.read_text(encoding="utf-8"))
            packets = retained.get("packets") if isinstance(retained,
                                                            dict) else None
            if isinstance(packets, list):
                for row in packets:
                    if isinstance(row, dict) and row.get("status") in {
                            "accepted", "deferred-approved-exception"
                    }:
                        errors.append(
                            "generated no-decision retained-code-acceptance-summary.json cannot set "
                            f"{row.get('id', 'unknown')} to {row.get('status')}"
                        )
        except json.JSONDecodeError as error:
            errors.append(
                f"{retained_path.relative_to(root).as_posix()} is not valid JSON: {error}"
            )
