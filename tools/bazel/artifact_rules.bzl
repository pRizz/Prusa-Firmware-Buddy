def phase3_release_artifacts(
        name,
        product,
        printer,
        board,
        mcu,
        bootloader_mode,
        payload,
        resource_seed = None,
        evidence_class = "local-smoke",
        signing_mode = "unsigned-local"):
    """Declare deterministic Phase 3 package-surface outputs.

    `.bbf` generation is routed through `utils/pack_fw.py --no-sign` by
    `artifact_packager.py` when prerequisites exist. `.dfu` generation is
    routed through `utils/dfu.py`. If bootstrap prerequisites are absent, the
    emitted status output is `BOOTSTRAP_REQUIRED` / `bootstrap-required` or
    `ci-only`; non-reference local BBF/DFU encoders must not satisfy BAZL-03.

    Structural compatibility checks are named `BBF structural check` and
    `DFU structural check`.
    """

    resource_arg = ""
    srcs = [payload]
    if resource_seed:
        srcs.append(resource_seed)
        resource_arg = " --resource-seed $(location %s)" % resource_seed

    native.genrule(
        name = name,
        srcs = srcs,
        tools = [
            "//tools/bazel:artifact_manifest.py",
            "//tools/bazel:artifact_packager.py",
        ],
        outs = [
            "%s.bin" % name,
            "%s.map" % name,
            "%s.provenance.json" % name,
            "%s.bbf" % name,
            "%s.bbf.status.json" % name,
            "%s.dfu" % name,
            "%s.dfu.status.json" % name,
            "%s.resource.img" % name,
            "%s.resource.pkg" % name,
            "%s.manifest.json" % name,
        ],
        cmd = "\n".join([
            "set -euo pipefail",
            "out_dir=\"$(@D)\"",
            "python3 $(location //tools/bazel:artifact_packager.py) \\",
            "  --output-dir \"$$out_dir\" \\",
            "  --name \"%s\" \\" % name,
            "  --product \"%s\" \\" % product,
            "  --printer \"%s\" \\" % printer,
            "  --board \"%s\" \\" % board,
            "  --mcu \"%s\" \\" % mcu,
            "  --bootloader-mode \"%s\" \\" % bootloader_mode,
            "  --payload $(location %s) \\" % payload,
            "  --evidence-class \"%s\" \\" % evidence_class,
            "  --signing-mode \"%s\"%s" % (signing_mode, resource_arg),
            "python3 $(location //tools/bazel:artifact_manifest.py) \\",
            "  --output \"$$out_dir/%s.manifest.json\" \\" % name,
            "  --product \"%s\" \\" % product,
            "  --printer \"%s\" \\" % printer,
            "  --board \"%s\" \\" % board,
            "  --mcu \"%s\" \\" % mcu,
            "  --bootloader-mode \"%s\" \\" % bootloader_mode,
            "  --artifact-kind bin \\",
            "  --artifact \"$$out_dir/%s.bin\" \\" % name,
            "  --resource \"$$out_dir/%s.resource.pkg\" \\" % name,
            "  --package-member \"$$out_dir/%s.bin\" \\" % name,
            "  --package-member \"$$out_dir/%s.map\" \\" % name,
            "  --package-member \"$$out_dir/%s.provenance.json\" \\" % name,
            "  --package-member \"$$out_dir/%s.bbf\" \\" % name,
            "  --package-member \"$$out_dir/%s.dfu\" \\" % name,
            "  --package-member \"$$out_dir/%s.resource.img\" \\" % name,
            "  --package-member \"$$out_dir/%s.resource.pkg\" \\" % name,
            "  --provenance \"$$out_dir/%s.provenance.json\" \\" % name,
            "  --evidence-class \"%s\" \\" % evidence_class,
            "  --signing-mode \"%s\"" % signing_mode,
        ]),
    )
