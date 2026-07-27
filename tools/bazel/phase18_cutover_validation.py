from __future__ import annotations

from phase18_cutover_contract import *
from phase18_cutover_source_refs import *


def contract_packets(contract: dict[str, Any]) -> list[dict[str, Any]]:
    raw_packets = contract.get("retained_code_acceptance_packets")
    if not isinstance(raw_packets, list):
        raise VerificationError(
            "contract retained_code_acceptance_packets must be a list")
    packets: list[dict[str, Any]] = []
    for index, packet in enumerate(raw_packets):
        if not isinstance(packet, dict):
            raise VerificationError(
                f"retained_code_acceptance_packets[{index}] must be an object")
        packets.append(packet)
    return packets


def contract_final_criteria(contract: dict[str, Any]) -> list[dict[str, Any]]:
    raw_criteria = contract.get("final_demotion_criteria")
    if not isinstance(raw_criteria, list):
        raise VerificationError(
            "contract final_demotion_criteria must be a list")
    criteria: list[dict[str, Any]] = []
    for index, criterion in enumerate(raw_criteria):
        if not isinstance(criterion, dict):
            raise VerificationError(
                f"final_demotion_criteria[{index}] must be an object")
        criteria.append(criterion)
    return criteria


def validate_schema(contract: dict[str, Any], errors: list[str]) -> None:
    top_level_fields = set(contract)
    for missing in sorted(EXPECTED_TOP_LEVEL_FIELDS - top_level_fields):
        errors.append(
            f"{CONTRACT_MANIFEST.as_posix()} missing top-level field: {missing}"
        )
    for extra in sorted(top_level_fields - EXPECTED_TOP_LEVEL_FIELDS):
        errors.append(
            f"{CONTRACT_MANIFEST.as_posix()} unexpected top-level field: {extra}"
        )
    expected_values = {
        "schema_version": "1",
        "id": "phase18_cutover_review_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase18-cutover-review",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected in expected_values.items():
        if contract.get(field) != expected:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected!r}")
    try:
        if require_list_of_strings(
                contract, "retained_packet_status_vocabulary",
                "contract") != RETAINED_PACKET_STATUS_VOCABULARY:
            errors.append(
                "retained_packet_status_vocabulary does not match the Phase 18 vocabulary"
            )
        if require_list_of_strings(
                contract, "final_criterion_status_vocabulary",
                "contract") != FINAL_CRITERION_STATUS_VOCABULARY:
            errors.append(
                "final_criterion_status_vocabulary does not match the Phase 18 vocabulary"
            )
        if require_list_of_strings(
                contract, "upstream_result_status_vocabulary",
                "contract") != UPSTREAM_RESULT_STATUS_VOCABULARY:
            errors.append(
                "upstream_result_status_vocabulary does not match the Phase 21 vocabulary"
            )
        if require_list_of_strings(contract, "review_decision_vocabulary",
                                   "contract") != REVIEW_DECISION_VOCABULARY:
            errors.append(
                "review_decision_vocabulary does not match the Phase 18 vocabulary"
            )
        if require_list_of_strings(contract, "allowed_demotion_statuses",
                                   "contract") != ALLOWED_DEMOTION_STATUSES:
            errors.append(
                "allowed_demotion_statuses does not match the Phase 18 demotion policy"
            )
        if (require_list_of_strings(contract,
                                    "acceptable_upstream_result_statuses",
                                    "contract")
                != ACCEPTABLE_UPSTREAM_RESULT_STATUSES):
            errors.append(
                "acceptable_upstream_result_statuses does not match the Phase 21 upstream policy"
            )
        validate_source_collection_map(contract, errors)
        validate_packet_schema(contract, errors)
        validate_decision_schema(contract, errors)
        validate_generated_artifacts(contract, errors)
    except VerificationError as error:
        errors.append(str(error))


def validate_source_collection_map(contract: dict[str, Any],
                                   errors: list[str]) -> None:
    source_collections = require_dict(contract, "retained_source_collections",
                                      "contract")
    for path, (collection_name,
               key_name) in SOURCE_REF_ROW_COLLECTIONS.items():
        entry = source_collections.get(path)
        if not isinstance(entry, dict):
            errors.append(
                f"retained_source_collections missing source manifest: {path}")
            continue
        if entry.get("collection") != collection_name:
            errors.append(
                f"{path} retained_source_collections collection must be {collection_name}"
            )
        if entry.get("key") != key_name:
            errors.append(
                f"{path} retained_source_collections key must be {key_name}")


def validate_packet_schema(contract: dict[str, Any],
                           errors: list[str]) -> None:
    schema = require_dict(contract, "retained_code_acceptance_packet_schema",
                          "contract")
    required_fields = require_list_of_strings(
        schema, "required_fields", "retained_code_acceptance_packet_schema")
    if required_fields != REQUIRED_PACKET_FIELDS:
        errors.append(
            "retained_code_acceptance_packet_schema required_fields do not match Phase 18 packet requirements"
        )
    if schema.get("secret_handling_policy") != "name-only-or-redacted":
        errors.append(
            "retained_code_acceptance_packet_schema secret_handling_policy must be name-only-or-redacted"
        )


def validate_decision_schema(contract: dict[str, Any],
                             errors: list[str]) -> None:
    schema = require_dict(contract, "final_decision_schema", "contract")
    required_fields = require_list_of_strings(schema, "required_fields",
                                              "final_decision_schema")
    if required_fields != FINAL_DECISION_REQUIRED_FIELDS:
        errors.append(
            "final_decision_schema required_fields do not match Phase 18 decision input requirements"
        )
    decisions = require_list_of_strings(schema, "decision_vocabulary",
                                        "final_decision_schema")
    if decisions != REVIEW_DECISION_VOCABULARY:
        errors.append(
            "final_decision_schema decision_vocabulary does not match review_decision_vocabulary"
        )
    exception = require_dict(schema, "exception", "final_decision_schema")
    exception_fields = require_list_of_strings(
        exception, "required_fields", "final_decision_schema.exception")
    if exception_fields != EXCEPTION_REQUIRED_FIELDS:
        errors.append(
            "final_decision_schema exception.required_fields do not match Phase 18 exception requirements"
        )


def contract_upstream_requirements(
        contract: dict[str, Any]) -> list[dict[str, Any]]:
    raw_requirements = contract.get("upstream_result_requirements")
    if not isinstance(raw_requirements, list):
        raise VerificationError(
            "contract upstream_result_requirements must be a list")
    requirements: list[dict[str, Any]] = []
    for index, requirement in enumerate(raw_requirements):
        if not isinstance(requirement, dict):
            raise VerificationError(
                f"upstream_result_requirements[{index}] must be an object")
        requirements.append(requirement)
    return requirements


def validate_upstream_result_requirements(
    requirements: list[dict[str, Any]],
    criteria: list[dict[str, Any]],
    errors: list[str],
) -> None:
    criteria_by_id = {
        str(criterion["id"]): criterion
        for criterion in criteria
    }
    requirement_ids = [
        str(requirement.get("criterion_id")) for requirement in requirements
    ]
    for missing in sorted(set(criteria_by_id) - set(requirement_ids)):
        errors.append(
            "missing upstream result requirement for final criterion: " +
            missing)
    for extra in sorted(set(requirement_ids) - set(criteria_by_id)):
        errors.append(
            "upstream result requirement criterion_id does not resolve: " +
            extra)
    if len(requirement_ids) != len(set(requirement_ids)):
        errors.append(
            "duplicate upstream result requirement criterion IDs are not allowed"
        )
    for requirement in requirements:
        criterion_id = str(
            requirement.get("criterion_id", "unknown-upstream-requirement"))
        criterion = criteria_by_id.get(criterion_id)
        try:
            validate_upstream_result_requirement(requirement, criterion,
                                                 criterion_id)
        except VerificationError as error:
            errors.append(str(error))


def validate_upstream_result_requirement(
    requirement: dict[str, Any],
    criterion: dict[str, Any] | None,
    requirement_name: str,
) -> None:
    errors: list[str] = []
    try:
        require_fields(requirement, UPSTREAM_RESULT_REQUIREMENT_FIELDS,
                       requirement_name)
        evidence_family = require_string(requirement, "evidence_family",
                                         requirement_name)
        result_required = require_bool(requirement, "result_required",
                                       requirement_name)
        source_phase = require_string(requirement, "source_phase",
                                      requirement_name)
        source_lifecycle_id = require_string(requirement,
                                             "source_lifecycle_id",
                                             requirement_name)
        manifest_refs = require_list_of_strings(requirement,
                                                "required_manifest_refs",
                                                requirement_name)
        approved_roots = require_list_of_strings(requirement,
                                                 "approved_ref_roots",
                                                 requirement_name)
        acceptable_statuses = set(
            require_list_of_strings(requirement, "acceptable_statuses",
                                    requirement_name))
        hard_blocking_statuses = set(
            require_list_of_strings(requirement, "hard_blocking_statuses",
                                    requirement_name))
        exception_coverable_statuses = set(
            require_list_of_strings(requirement,
                                    "exception_coverable_statuses",
                                    requirement_name))
        required_row_fields = require_list_of_strings(requirement,
                                                      "required_row_fields",
                                                      requirement_name)
        require_list_of_strings(requirement, "hard_blocker_reasons",
                                requirement_name)
        require_list_of_strings(requirement, "requirement_ids",
                                requirement_name)
        redaction_field = require_string(requirement, "redaction_status_field",
                                         requirement_name)
        source_ref_field = require_string(requirement,
                                          "source_ref_status_field",
                                          requirement_name)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if criterion is not None and evidence_family != criterion[
            "evidence_family"]:
        errors.append(
            f"{requirement_name} evidence_family must match final criterion")
    expected_lifecycle = UPSTREAM_SOURCE_LIFECYCLES.get(source_phase)
    if expected_lifecycle is None:
        errors.append(
            f"{requirement_name} source_phase is not approved: {source_phase}")
    elif source_lifecycle_id != expected_lifecycle:
        errors.append(
            f"{requirement_name} source_lifecycle_id must be {expected_lifecycle}"
        )
    if not set(acceptable_statuses) <= set(UPSTREAM_RESULT_STATUS_VOCABULARY):
        errors.append(
            f"{requirement_name} acceptable_statuses contains unknown upstream statuses"
        )
    if not set(hard_blocking_statuses) <= set(
            UPSTREAM_RESULT_STATUS_VOCABULARY):
        errors.append(
            f"{requirement_name} hard_blocking_statuses contains unknown upstream statuses"
        )
    if not set(exception_coverable_statuses) <= set(
            UPSTREAM_RESULT_STATUS_VOCABULARY):
        errors.append(
            f"{requirement_name} exception_coverable_statuses contains unknown upstream statuses"
        )
    if hard_blocking_statuses & exception_coverable_statuses:
        errors.append(
            f"{requirement_name} hard_blocking_statuses cannot be exception coverable"
        )
    if result_required and "passed" not in acceptable_statuses:
        errors.append(
            f"{requirement_name} result_required requirements must accept passed"
        )
    if not result_required and "not-required" not in acceptable_statuses:
        errors.append(
            f"{requirement_name} decision-owned requirements must accept not-required"
        )
    if "rejected-redaction" not in hard_blocking_statuses or "rejected-overclaim" not in hard_blocking_statuses:
        errors.append(
            f"{requirement_name} must hard-block redaction and overclaim failures"
        )
    if required_row_fields != UPSTREAM_RESULT_ROW_REQUIRED_FIELDS:
        errors.append(
            f"{requirement_name} required_row_fields do not match Phase 21 upstream row requirements"
        )
    if redaction_field != "redaction_status":
        errors.append(
            f"{requirement_name} redaction_status_field must be redaction_status"
        )
    if source_ref_field != "source_ref_status":
        errors.append(
            f"{requirement_name} source_ref_status_field must be source_ref_status"
        )
    for root in approved_roots:
        if root.startswith("external://"):
            continue
        try:
            require_repo_relative(root,
                                  f"{requirement_name} approved_ref_roots")
        except VerificationError as error:
            errors.append(str(error))
    for manifest_ref in manifest_refs:
        try:
            require_upstream_artifact_ref(
                manifest_ref, approved_roots,
                f"{requirement_name} required_manifest_refs")
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def validate_generated_artifacts(contract: dict[str, Any],
                                 errors: list[str]) -> None:
    artifacts = require_list_of_strings(contract, "generated_artifacts",
                                        "contract")
    seen = set(artifacts)
    for missing in sorted(REQUIRED_GENERATED_ARTIFACTS - seen):
        errors.append(f"missing required generated artifact: {missing}")
    for extra in sorted(seen - REQUIRED_GENERATED_ARTIFACTS):
        errors.append(f"unexpected generated artifact: {extra}")
    if len(artifacts) != len(seen):
        errors.append("generated_artifacts must not contain duplicates")
    for artifact in artifacts:
        try:
            require_repo_relative(artifact, "generated_artifacts")
        except VerificationError as error:
            errors.append(str(error))


def validate_packets(root: Path, packets: list[dict[str, Any]],
                     errors: list[str]) -> set[str]:
    packet_ids = [str(packet.get("id")) for packet in packets]
    for missing in sorted(REQUIRED_RETAINED_PACKET_IDS - set(packet_ids)):
        errors.append("missing required retained packet: " + missing)
    if len(packet_ids) != len(set(packet_ids)):
        errors.append("duplicate retained packet IDs are not allowed")
    covered_source_refs: set[str] = set()
    for packet in packets:
        packet_name = str(packet.get("id", "unknown retained packet"))
        try:
            validate_packet(root, packet, packet_name)
            covered_source_refs.update(packet["retained_source_refs"])
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(
            retained_surface_source_refs(root) - covered_source_refs):
        errors.append("missing retained source coverage: " + missing)
    return set(packet_ids)


def validate_packet(root: Path, packet: dict[str, Any],
                    packet_name: str) -> None:
    errors: list[str] = []
    try:
        require_fields(packet, REQUIRED_PACKET_FIELDS, packet_name)
        requirement_ids = set(
            require_list_of_strings(packet, "requirement_ids", packet_name))
        require_list_of_strings(packet, "taxonomy_tags", packet_name)
        status = require_string(packet, "status", packet_name)
        source_refs = require_list_of_strings(packet, "retained_source_refs",
                                              packet_name)
        require_list_of_strings(packet, "prior_phase_refs", packet_name)
        require_list_of_strings(packet, "required_evidence_refs", packet_name)
        require_list_of_strings(packet, "supplied_evidence_result_refs",
                                packet_name)
        require_string(packet, "approver_role", packet_name)
        require_dict(packet, "approval_metadata", packet_name)
        require_string(packet, "rationale", packet_name)
        require_string(packet, "residual_risk", packet_name)
        require_string(packet, "blocker_or_deferred_action", packet_name)
        require_string(packet, "exception_ref", packet_name)
        require_list_of_strings(packet, "unsupported_claims", packet_name)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
    if "REV-01" not in requirement_ids:
        errors.append(f"{packet_name} must cover REV-01")
    if unknown_requirements:
        errors.append(
            f"{packet_name} uses unknown REV requirement IDs: {', '.join(unknown_requirements)}"
        )
    if status not in RETAINED_PACKET_STATUS_VOCABULARY:
        errors.append(f"{packet_name} status is invalid: {status}")
    if packet.get("secret_handling_policy") != "name-only-or-redacted":
        errors.append(
            f"{packet_name} secret_handling_policy must be name-only-or-redacted"
        )
    unsupported_claims = set(packet.get("unsupported_claims", []))
    for missing in sorted(REQUIRED_UNSUPPORTED_CLAIMS - unsupported_claims):
        errors.append(
            f"{packet_name} missing unsupported claim guard: {missing}")
    for source_ref in source_refs:
        try:
            resolve_source_ref(root, source_ref, packet_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def validate_final_criteria(root: Path, criteria: list[dict[str, Any]],
                            packet_ids: set[str], errors: list[str]) -> None:
    criterion_ids = [str(criterion.get("id")) for criterion in criteria]
    for missing in sorted(REQUIRED_FINAL_CRITERION_IDS - set(criterion_ids)):
        errors.append("missing required final demotion criterion: " + missing)
    if len(criterion_ids) != len(set(criterion_ids)):
        errors.append("duplicate final demotion criterion IDs are not allowed")
    covered_families: set[str] = set()
    for criterion in criteria:
        criterion_name = str(criterion.get("id", "unknown final criterion"))
        try:
            validate_final_criterion(root, criterion, criterion_name,
                                     packet_ids)
            covered_families.add(criterion["evidence_family"])
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(REQUIRED_FINAL_EVIDENCE_FAMILIES - covered_families):
        errors.append("missing required final evidence family coverage: " +
                      missing)


def validate_final_criterion(root: Path, criterion: dict[str, Any],
                             criterion_name: str,
                             packet_ids: set[str]) -> None:
    errors: list[str] = []
    try:
        require_fields(criterion, REQUIRED_FINAL_CRITERION_FIELDS,
                       criterion_name)
        requirement_ids = set(
            require_list_of_strings(criterion, "requirement_ids",
                                    criterion_name))
        evidence_family = require_string(criterion, "evidence_family",
                                         criterion_name)
        required_decision = require_string(criterion, "required_decision",
                                           criterion_name)
        default_status = require_string(criterion, "default_status",
                                        criterion_name)
        allowed_statuses = set(
            require_list_of_strings(criterion, "allowed_statuses",
                                    criterion_name))
        source_refs = require_list_of_strings(criterion, "source_refs",
                                              criterion_name)
        require_bool(criterion, "maintainer_decision_required", criterion_name)
        require_bool(criterion, "exception_allowed", criterion_name)
        require_bool(criterion, "blocks_demotion", criterion_name)
        require_string(criterion, "residual_risk_ref", criterion_name)
        require_string(criterion, "local_proof_boundary", criterion_name)
        require_string(criterion, "non_local_evidence_boundary",
                       criterion_name)
        require_list_of_strings(criterion, "unsupported_claims",
                                criterion_name)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
    if not requirement_ids:
        errors.append(
            f"{criterion_name} must cover at least one REV- requirement")
    if unknown_requirements:
        errors.append(
            f"{criterion_name} uses unknown REV requirement IDs: {', '.join(unknown_requirements)}"
        )
    if evidence_family not in REQUIRED_FINAL_EVIDENCE_FAMILIES:
        errors.append(
            f"{criterion_name} evidence_family is invalid: {evidence_family}")
    if required_decision not in REVIEW_DECISION_VOCABULARY:
        errors.append(
            f"{criterion_name} required_decision is invalid: {required_decision}"
        )
    if default_status not in FINAL_CRITERION_STATUS_VOCABULARY:
        errors.append(
            f"{criterion_name} default_status is invalid: {default_status}")
    if not allowed_statuses <= set(FINAL_CRITERION_STATUS_VOCABULARY):
        errors.append(
            f"{criterion_name} allowed_statuses contains unknown statuses")
    if default_status in FINAL_CRITERION_STATUS_VOCABULARY and default_status not in allowed_statuses:
        errors.append(
            f"{criterion_name} default_status {default_status} is not allowed by allowed_statuses"
        )
    if criterion.get("blocks_demotion") is not True:
        errors.append(f"{criterion_name} blocks_demotion must be true")
    if criterion_name in {
            "final-retained-code-acceptance",
            "final-residual-risk-review",
            "final-maintainer-decision",
            "final-reference-demotion-allowed",
    } and criterion.get("maintainer_decision_required") is not True:
        errors.append(
            f"{criterion_name} maintainer_decision_required must be true")
    unsupported_claims = set(criterion.get("unsupported_claims", []))
    if "claim-reference-demotion-without-decision-input" not in unsupported_claims:
        errors.append(
            f"{criterion_name} must guard against reference demotion without decision input"
        )
    for source_ref in source_refs:
        try:
            resolve_source_ref(root, source_ref, criterion_name)
        except VerificationError as error:
            errors.append(str(error))
    for packet_id in criterion.get("packet_refs", []):
        if packet_id not in packet_ids:
            errors.append(
                f"{criterion_name} packet ref does not resolve: {packet_id}")
    if errors:
        raise VerificationError("\n".join(errors))
