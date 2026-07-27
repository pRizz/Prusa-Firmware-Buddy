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

phase18-verify:
    bazel run //tools/bazel:phase18_verify_tests
    bazel run //tools/bazel:phase18_verify

phase19-verify:
    bazel run //tools/bazel:phase19_verify_tests
    bazel run //tools/bazel:phase19_verify

phase20-verify:
    bazel run //tools/bazel:phase20_verify_tests
    bazel run //tools/bazel:phase20_verify

phase22-verify:
    bazel run //tools/bazel:phase22_verify_tests
    bazel run //tools/bazel:phase22_verify

phase23-verify:
    bazel run //tools/bazel:phase23_verify_tests
    bazel run //tools/bazel:phase23_verify

phase24-verify:
    bazel run //tools/bazel:phase24_verify_tests
    bazel run //tools/bazel:phase24_verify

phase25-verify:
    bazel run //tools/bazel:phase25_verify_tests
    bazel run //tools/bazel:phase25_verify

phase26-verify:
    bazel run //tools/bazel:phase26_verify_tests
    bazel run //tools/bazel:phase26_verify

phase27-verify:
    bazel run //tools/bazel:phase27_verify_tests
    bazel run //tools/bazel:phase27_verify

phase28-verify:
    bazel run //tools/bazel:phase28_verify_tests
    bazel run //tools/bazel:phase28_verify

phase31-verify:
    bazel run //tools/bazel:phase31_verify_tests
    bazel run //tools/bazel:phase31_verify

phase32-verify:
    bazel run //tools/bazel:phase32_verify_tests
    bazel run //tools/bazel:phase32_verify

phase33-verify:
    bazel run //tools/bazel:phase33_verify_tests
    bazel run //tools/bazel:phase33_verify

phase34-verify:
    bazel run //tools/bazel:phase34_verify_tests
    bazel run //tools/bazel:phase34_verify

phase35-verify:
    bazel run //tools/bazel:phase35_verify_tests
    bazel run //tools/bazel:phase35_verify

phase38-verify:
    bazel run //tools/bazel:phase38_verify_tests
    bazel run //tools/bazel:phase38_verify

phase40-verify *args:
    bazel run //:phase40_file_length_policy_test
    bazel run //:phase40_file_length_policy -- {{args}}
    bun scripts/bright-builds-check.ts all

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
