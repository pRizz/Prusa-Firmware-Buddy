load(
    "//tools/bazel/phase42:host_policy.bzl",
    "darwin_host_policy",
    "linux_x86_64_host_policy",
)

EmbeddedToolchainInfo = provider(fields = {
    "rustc": "rules_rust-resolved Rust 1.85.0 compiler",
    "arm_gcc": "Arm GNU 13.2.Rel1 driver",
    "arm_objcopy": "Arm GNU objcopy",
    "arm_objdump": "Arm GNU objdump",
    "arm_readelf": "Arm GNU readelf",
    "arm_nm": "Arm GNU nm",
    "arm_size": "Arm GNU size",
    "arm_toolchain_files": "complete Arm GNU runtime needed by the compiler driver",
    "python": "rules_python-resolved Python 3.12.10 interpreter",
    "mini404": "Mini404 0.9.10 executable",
    "versions": "locked identity dictionary",
    "target_triple": "thumbv7em-none-eabihf",
})

_LOCKED_VERSIONS = {
    "rust": "1.85.0",
    "arm_gnu": "13.2.Rel1",
    "python": "3.12.10",
    "mini404": "0.9.10",
}


def _linux_x86_64_qualification_toolchain_impl(ctx):
    host_policy = linux_x86_64_host_policy()
    embedded = EmbeddedToolchainInfo(
        rustc = ctx.attr.rustc[DefaultInfo].files_to_run,
        arm_gcc = ctx.attr.arm_gcc[DefaultInfo].files_to_run,
        arm_objcopy = ctx.attr.arm_objcopy[DefaultInfo].files_to_run,
        arm_objdump = ctx.attr.arm_objdump[DefaultInfo].files_to_run,
        arm_readelf = ctx.attr.arm_readelf[DefaultInfo].files_to_run,
        arm_nm = ctx.attr.arm_nm[DefaultInfo].files_to_run,
        arm_size = ctx.attr.arm_size[DefaultInfo].files_to_run,
        arm_toolchain_files = ctx.attr.arm_toolchain_files[DefaultInfo].files,
        python = ctx.attr.python[DefaultInfo].files_to_run,
        mini404 = ctx.attr.mini404[DefaultInfo].files_to_run,
        versions = _LOCKED_VERSIONS,
        target_triple = "thumbv7em-none-eabihf",
    )
    return [
        host_policy,
        embedded,
        platform_common.ToolchainInfo(
            host_policy = host_policy,
            embedded = embedded,
        ),
    ]


def _darwin_qualification_toolchain_impl(ctx):
    host_policy = darwin_host_policy(ctx.attr.arch)
    return [
        host_policy,
        platform_common.ToolchainInfo(host_policy = host_policy),
    ]


_EXECUTABLE_ATTRS = {
    "rustc": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "arm_gcc": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "arm_objcopy": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "arm_objdump": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "arm_readelf": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "arm_nm": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "arm_size": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "python": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
    "mini404": attr.label(executable = True, cfg = "exec", mandatory = True, allow_files = True),
}

phase42_linux_x86_64_qualification_toolchain = rule(
    implementation = _linux_x86_64_qualification_toolchain_impl,
    attrs = dict(
        _EXECUTABLE_ATTRS,
        arm_toolchain_files = attr.label(mandatory = True),
    ),
)

phase42_darwin_qualification_toolchain = rule(
    implementation = _darwin_qualification_toolchain_impl,
    attrs = {
        "arch": attr.string(mandatory = True, values = ["x86_64", "arm64"]),
    },
)
