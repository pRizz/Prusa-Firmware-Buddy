def _reference_toolchain_impl(ctx):
    return [
        platform_common.ToolchainInfo(
            language = ctx.attr.language,
            reference_command = ctx.attr.reference_command,
            source_paths = ctx.attr.source_paths,
            toolchain_name = ctx.attr.toolchain_name,
        ),
    ]


reference_toolchain = rule(
    implementation = _reference_toolchain_impl,
    attrs = {
        "language": attr.string(mandatory = True),
        "reference_command": attr.string(mandatory = True),
        "source_paths": attr.string_list(mandatory = True),
        "toolchain_name": attr.string(mandatory = True),
    },
)
