load(
    "//tools/bazel/phase42:host_policy.bzl",
    "PHASE42_QUALIFICATION_TOOLCHAIN_TYPE",
    "require_embedded_toolchain",
)

_EXPECTED_VERSIONS = {
    "arm_gnu": "13.2.Rel1",
    "rust": "1.85.0",
}
_TARGET_TRIPLE = "thumbv7em-none-eabihf"
_CANONICAL_PLATFORM = "//platforms:mini_buddy_stm32f407vg"


def _require_locked_identity(embedded):
    if embedded.target_triple != _TARGET_TRIPLE:
        fail("Phase 42 link smoke requires target {}".format(_TARGET_TRIPLE))
    for tool, expected in _EXPECTED_VERSIONS.items():
        actual = embedded.versions.get(tool)
        if actual != expected:
            fail("Phase 42 link smoke requires {} {}, got {}".format(tool, expected, actual))


def _capture_inspection(ctx, *, mnemonic, tool, arguments, input_file, output, checks):
    output_index = len(arguments) + 2
    command = [
        "set -euo pipefail",
        '"$1" "${@:2:%d}" > "${%d}"' % (len(arguments), output_index),
    ]
    for index in range(len(checks)):
        command.append('grep -Eq "${%d}" "${%d}"' % (output_index + index + 1, output_index))

    action_arguments = [tool.executable.path]
    action_arguments.extend(arguments)
    action_arguments.append(output.path)
    action_arguments.extend(checks)
    ctx.actions.run_shell(
        arguments = action_arguments,
        command = "\n".join(command),
        inputs = [input_file],
        mnemonic = mnemonic,
        outputs = [output],
        tools = [tool],
    )


def _arm_link_smoke_impl(ctx):
    embedded = require_embedded_toolchain(ctx)
    _require_locked_identity(embedded)

    object_file = ctx.actions.declare_file(ctx.label.name + ".o")
    elf_file = ctx.actions.declare_file(ctx.label.name + ".elf")
    map_file = ctx.actions.declare_file(ctx.label.name + ".map")
    report_file = ctx.actions.declare_file(ctx.label.name + ".report.json")
    readelf_file = ctx.actions.declare_file(ctx.label.name + ".readelf.txt")
    objdump_file = ctx.actions.declare_file(ctx.label.name + ".objdump.txt")
    nm_file = ctx.actions.declare_file(ctx.label.name + ".nm.txt")
    size_file = ctx.actions.declare_file(ctx.label.name + ".size.txt")

    ctx.actions.run(
        arguments = [
            ctx.file.src.path,
            "--crate-name=phase42_arm_link_smoke",
            "--crate-type=bin",
            "--edition=2024",
            "--target=thumbv7em-none-eabihf",
            "--emit=obj=" + object_file.path,
            "-Cpanic=abort",
            "-Copt-level=s",
        ],
        executable = embedded.rustc,
        inputs = [ctx.file.src],
        mnemonic = "Phase42RustCompile",
        outputs = [object_file],
    )

    ctx.actions.run(
        arguments = [
            object_file.path,
            "-o",
            elf_file.path,
            "-nostdlib",
            "-mthumb",
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",
            "-Wl,--gc-sections",
            "-Wl,-Map," + map_file.path,
            "-T",
            ctx.file.linker_script.path,
        ],
        executable = embedded.arm_gcc,
        inputs = depset(
            direct = [object_file, ctx.file.linker_script],
            transitive = [embedded.arm_toolchain_files],
        ),
        mnemonic = "Phase42ArmLink",
        outputs = [elf_file, map_file],
    )

    inspection_specs = (
        (
            "Phase42ArmReadelf",
            embedded.arm_readelf,
            ["-h", "-A", elf_file.path],
            readelf_file,
            ["Machine:[[:space:]]+ARM", "hard-float ABI", "Tag_CPU_arch: v7E-M", "Tag_FP_arch: VFPv4-D16", "Tag_ABI_VFP_args: VFP registers"],
        ),
        (
            "Phase42ArmObjdump",
            embedded.arm_objdump,
            ["-f", "-d", elf_file.path],
            objdump_file,
            ["file format elf32-littlearm", "architecture: arm", "<_phase42_smoke_entry>"],
        ),
        (
            "Phase42ArmNm",
            embedded.arm_nm,
            ["-g", "--defined-only", elf_file.path],
            nm_file,
            ["[[:space:]]T[[:space:]]+_phase42_smoke_entry$"],
        ),
        (
            "Phase42ArmSize",
            embedded.arm_size,
            ["-A", elf_file.path],
            size_file,
            ["^\\.text[[:space:]]+[1-9][0-9]*"],
        ),
    )
    for mnemonic, tool, arguments, output, checks in inspection_specs:
        _capture_inspection(
            ctx,
            mnemonic = mnemonic,
            tool = tool,
            arguments = arguments,
            input_file = elf_file,
            output = output,
            checks = checks,
        )

    inspection_files = [readelf_file, objdump_file, nm_file, size_file]
    report = json.encode({
        "artifact_class": "phase42-arm-link-smoke",
        "arm_gnu": "Arm GNU 13.2.Rel1",
        "elf": elf_file.path,
        "inspections": [output.path for output in inspection_files],
        "map": map_file.path,
        "platform": _CANONICAL_PLATFORM,
        "report": report_file.path,
        "rust": "Rust 1.85.0",
        "schema": "phase42-arm-link-smoke/v1",
        "target": str(ctx.label),
        "target_triple": _TARGET_TRIPLE,
    })
    ctx.actions.run_shell(
        arguments = [report_file.path, report] + [output.path for output in [elf_file, map_file] + inspection_files],
        command = "set -euo pipefail\nfor input in \"${@:3}\"; do test -s \"$input\"; done\nprintf '%s\\n' \"$2\" > \"$1\"",
        inputs = [elf_file, map_file] + inspection_files,
        mnemonic = "Phase42SmokeReport",
        outputs = [report_file],
    )

    return [
        DefaultInfo(files = depset([elf_file, map_file, report_file])),
        OutputGroupInfo(inspections = depset(inspection_files)),
    ]


arm_link_smoke = rule(
    implementation = _arm_link_smoke_impl,
    attrs = {
        "linker_script": attr.label(allow_single_file = True, mandatory = True),
        "src": attr.label(allow_single_file = [".rs"], mandatory = True),
    },
    toolchains = [PHASE42_QUALIFICATION_TOOLCHAIN_TYPE],
)
