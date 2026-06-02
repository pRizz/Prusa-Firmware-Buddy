set shell := ["bash", "-euo", "pipefail", "-c"]

phase2-verify:
    python3 tools/bazel/phase2_verify.py

bazel-query:
    bazel query "//tools/bazel/... + //platforms/..."

bootstrap:
    bazel run //tools/bazel:bootstrap

build:
    bazel run //tools/bazel:build_firmware

test:
    bazel run //tools/bazel:test_host

format:
    bazel run //tools/bazel:format

lint:
    bazel run //tools/bazel:lint

generated-check:
    bazel run //tools/bazel:generated_check

simulator-parity:
    bazel run //tools/bazel:simulator_parity

release-package:
    bazel run //tools/bazel:release_package
