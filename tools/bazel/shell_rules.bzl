def _shell_binary_impl(ctx):
    output = ctx.actions.declare_file(ctx.label.name)
    source = ctx.file.src

    ctx.actions.run_shell(
        inputs = [source],
        outputs = [output],
        command = "cp \"$1\" \"$2\" && chmod +x \"$2\"",
        arguments = [source.path, output.path],
    )

    return [DefaultInfo(
        executable = output,
        files = depset([output]),
        runfiles = ctx.runfiles(files = [source] + ctx.files.data),
    )]

shell_binary = rule(
    implementation = _shell_binary_impl,
    attrs = {
        "data": attr.label_list(allow_files = True),
        "src": attr.label(allow_single_file = True, mandatory = True),
    },
    executable = True,
)
