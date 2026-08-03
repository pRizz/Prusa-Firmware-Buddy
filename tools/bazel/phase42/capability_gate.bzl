load(
    ":host_policy.bzl",
    "PHASE42_QUALIFICATION_TOOLCHAIN_TYPE",
)


def _unavailable_capability_impl(ctx):
    toolchain = ctx.toolchains[PHASE42_QUALIFICATION_TOOLCHAIN_TYPE]
    host_policy = toolchain.host_policy
    capability = ctx.label.name
    owner_and_remedy = "owning phase: {}; available now: {}".format(
        ctx.attr.owning_phase,
        ctx.attr.available_command,
    )
    if not host_policy.qualifies:
        fail("{}; capability: {}; {}".format(
            host_policy.diagnostic,
            capability,
            owner_and_remedy,
        ))

    fail("capability unavailable: {}; {}".format(capability, owner_and_remedy))


_unavailable_capability = rule(
    implementation = _unavailable_capability_impl,
    attrs = {
        "available_command": attr.string(mandatory = True),
        "owning_phase": attr.string(mandatory = True),
    },
    executable = True,
    toolchains = [PHASE42_QUALIFICATION_TOOLCHAIN_TYPE],
)


def unavailable_capability(name, owning_phase, available_command):
    """Declares a capability that must fail during analysis until its owner lands."""
    _unavailable_capability(
        name = name,
        available_command = available_command,
        owning_phase = owning_phase,
    )
