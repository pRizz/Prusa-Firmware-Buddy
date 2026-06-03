set shell := ["bash", "-euo", "pipefail", "-c"]

phase2-verify:
    python3 tools/bazel/phase2_verify.py

phase3-verify:
    bazel run //tools/bazel:phase3_verify

phase4-verify:
    bazel run //tools/bazel:phase4_verify

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

rust-format:
    bazel run //tools/bazel:rust_format_check

rust-lint:
    bazel run //tools/bazel:rust_lint

rust-test:
    bazel run //tools/bazel:rust_unit_tests

rust-doc:
    bazel run //tools/bazel:rust_docs

rust-build:
    bazel run //tools/bazel:rust_build

generated-check:
    bazel run //tools/bazel:generated_check

generated-update:
    bazel run //tools/bazel:generated_update

simulator-parity:
    bazel run //tools/bazel:simulator_parity

release-package:
    bazel build //tools/bazel:representative_release_artifacts
