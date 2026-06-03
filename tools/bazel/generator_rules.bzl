load(":shell_rules.bzl", "shell_binary")

PHASE3_GENERATED_SURFACES = {
    "product_profiles": struct(evidence_class = "local-smoke", writes_source_tree = True),
    "option_data": struct(evidence_class = "local-smoke", writes_source_tree = True),
    "resources": struct(evidence_class = "ci-only", writes_source_tree = True),
    "translations": struct(evidence_class = "ci-only", writes_source_tree = True),
    "fonts": struct(evidence_class = "ci-only", writes_source_tree = True),
    "wui_assets": struct(evidence_class = "ci-only", writes_source_tree = True),
    "esp_blobs": struct(evidence_class = "reference-only", writes_source_tree = True),
    "puppy_descriptors": struct(evidence_class = "reference-only", writes_source_tree = True),
    "mmu_descriptors": struct(evidence_class = "reference-only", writes_source_tree = True),
    "package_metadata": struct(evidence_class = "local-smoke", writes_source_tree = True),
    "tracked_generated_outputs": struct(evidence_class = "local-smoke", writes_source_tree = True),
}


def phase3_generated_check(name, surface):
    shell_binary(
        name = name,
        src = "phase3_workflow.sh",
        data = [
            "generated_drift.py",
            "manifests/representative_products.json",
            "//:phase1_reference_baseline",
        ],
    )


def phase3_generated_update(name, surface):
    shell_binary(
        name = name,
        src = "phase3_workflow.sh",
        data = [
            "generated_drift.py",
            "manifests/representative_products.json",
            "//:phase1_reference_baseline",
        ],
    )


def phase3_generated_surface(surface):
    metadata = PHASE3_GENERATED_SURFACES[surface]
    check_name = "tracked_generated_outputs_check" if surface == "tracked_generated_outputs" else "generated_%s_check" % surface
    update_name = "tracked_generated_outputs_update" if surface == "tracked_generated_outputs" else "generated_%s_update" % surface

    # Metadata is intentionally retained in the macro surface so queryable
    # labels carry source-writing and evidence-class semantics.
    _evidence_class = metadata.evidence_class
    _writes_source_tree = metadata.writes_source_tree
    phase3_generated_check(name = check_name, surface = surface)
    phase3_generated_update(name = update_name, surface = surface)
