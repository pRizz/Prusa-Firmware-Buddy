set shell := ["bash", "-euo", "pipefail", "-c"]

phase2-verify:
    python3 tools/bazel/phase2_verify.py

phase3-verify:
    bazel run //tools/bazel:phase3_verify

phase4-verify:
    bazel run //tools/bazel:phase4_verify

phase5-verify:
    bazel run //tools/bazel:phase5_verify

phase6-verify:
    bazel run //tools/bazel:phase6_verify_tests
    bazel run //tools/bazel:phase6_verify

phase7-verify:
    bazel run //tools/bazel:phase7_verify_tests
    bazel run //tools/bazel:phase7_verify

phase8-verify:
    bazel run //tools/bazel:phase8_verify_tests
    bazel run //tools/bazel:phase8_verify

phase9-verify:
    bazel run //tools/bazel:phase9_verify_tests
    bazel run //tools/bazel:phase9_verify

phase10-verify:
    bazel run //tools/bazel:phase10_verify_tests
    bazel run //tools/bazel:phase10_verify

phase11-verify:
    bazel run //tools/bazel:phase11_verify_tests
    bazel run //tools/bazel:phase11_verify
    bazel run //tools/bazel:rust_format_check
    bazel run //tools/bazel:rust_lint
    bazel run //tools/bazel:rust_build
    bazel run //tools/bazel:rust_unit_tests

phase13-verify:
    bazel run //tools/bazel:phase13_verify_tests
    bazel run //tools/bazel:phase13_verify

phase14-verify:
    bazel run //tools/bazel:phase14_verify_tests
    bazel run //tools/bazel:phase14_verify

phase15-verify:
    bazel run //tools/bazel:phase15_verify_tests
    bazel run //tools/bazel:phase15_verify

phase16-verify:
    bazel run //tools/bazel:phase16_verify_tests
    bazel run //tools/bazel:phase16_verify

phase17-verify:
    bazel run //tools/bazel:phase17_verify_tests
    bazel run //tools/bazel:phase17_verify

phase17-release-artifacts-smoke:
    bazel build //tools/bazel:phase17_representative_release_smoke

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
