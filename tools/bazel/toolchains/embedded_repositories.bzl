load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")


_ARM_GNU_BUILD_FILE = """
package(default_visibility = ["//visibility:public"])

exports_files([
    "bin/arm-none-eabi-ar",
    "bin/arm-none-eabi-as",
    "bin/arm-none-eabi-g++",
    "bin/arm-none-eabi-gcc",
    "bin/arm-none-eabi-ld",
    "bin/arm-none-eabi-nm",
    "bin/arm-none-eabi-objcopy",
    "bin/arm-none-eabi-objdump",
    "bin/arm-none-eabi-readelf",
    "bin/arm-none-eabi-size",
])

filegroup(
    name = "all_files",
    srcs = glob(["**"], exclude_directories = 0),
)
"""

_MINI404_BUILD_FILE = """
package(default_visibility = ["//visibility:public"])

exports_files(["qemu-system-buddy"])

filegroup(
    name = "runtime_files",
    srcs = glob(["**"], exclude_directories = 0),
)
"""


def _embedded_repositories_impl(_module_ctx):
    http_archive(
        name = "arm_gnu_linux_x86_64",
        build_file_content = _ARM_GNU_BUILD_FILE,
        sha256 = "6cd1bbc1d9ae57312bcd169ae283153a9572bd6a8e4eeae2fedfbc33b115fdbb",
        strip_prefix = "arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi",
        url = "https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz",
    )

    http_archive(
        name = "mini404_linux_x86_64",
        build_file_content = _MINI404_BUILD_FILE,
        sha256 = "2709a43dbb6e64ea4597399d2f0e05be13e70a7b659a18ac61512498d320a5ba",
        strip_prefix = "Mini404-v0.9.10-linux",
        url = "https://github.com/vintagepc/MINI404/releases/download/v0.9.10/Mini404-v0.9.10-linux.tar.bz2",
    )


embedded_repositories = module_extension(
    implementation = _embedded_repositories_impl,
)
