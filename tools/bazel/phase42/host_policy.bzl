PHASE42_QUALIFICATION_TOOLCHAIN_TYPE = "//tools/bazel/toolchains:phase42_qualification_toolchain_type"

HostPolicyInfo = provider(fields = {
    "detected_os": "linux or darwin",
    "detected_arch": "x86_64 or arm64",
    "qualifies": "true only for linux/x86_64",
    "diagnostic": "detected host plus canonical Linux x86_64 CI/container remedy",
})

_DARWIN_DIAGNOSTICS = {
    "x86_64": "unsupported embedded qualification host: detected Darwin-x86_64; use canonical Linux x86_64 CI/container",
    "arm64": "unsupported embedded qualification host: detected Darwin-arm64; use canonical Linux x86_64 CI/container",
}


def linux_x86_64_host_policy():
    return HostPolicyInfo(
        detected_os = "linux",
        detected_arch = "x86_64",
        qualifies = True,
        diagnostic = "",
    )


def darwin_host_policy(arch):
    if arch not in _DARWIN_DIAGNOSTICS:
        fail("unsupported Darwin host policy architecture: {}".format(arch))

    return HostPolicyInfo(
        detected_os = "darwin",
        detected_arch = arch,
        qualifies = False,
        diagnostic = _DARWIN_DIAGNOSTICS[arch],
    )


def require_embedded_toolchain(ctx):
    toolchain = ctx.toolchains[PHASE42_QUALIFICATION_TOOLCHAIN_TYPE]
    host_policy = toolchain.host_policy
    if not host_policy.qualifies:
        fail(host_policy.diagnostic)

    return toolchain.embedded
