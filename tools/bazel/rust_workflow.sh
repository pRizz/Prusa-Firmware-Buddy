#!/usr/bin/env bash
set -euo pipefail

root="${BUILD_WORKSPACE_DIRECTORY:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
command_name="$(basename "$0")"

cd "$root"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$root/target/rust}"

case "$command_name" in
  rust_format_check)
    cargo fmt --all -- --check
    ;;
  rust_lint)
    cargo clippy --all-targets --all-features -- -D warnings
    ;;
  rust_unit_tests)
    cargo test --all-features
    ;;
  rust_docs)
    cargo doc --workspace --all-features --no-deps
    ;;
  rust_build|rust_firmware)
    cargo build --workspace --all-features
    ;;
  phase4_verify)
    python3 tools/bazel/phase4_verify.py --all
    ;;
  *)
    printf 'Unknown Rust workflow target: %s\n' "$command_name" >&2
    exit 2
    ;;
esac

