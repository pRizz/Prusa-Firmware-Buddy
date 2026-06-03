#!/usr/bin/env bash
set -euo pipefail

root="${BUILD_WORKSPACE_DIRECTORY:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$root"

printf 'representative_release_artifacts\n'
printf 'evidence_class=local-smoke\n'
printf 'reference_format_status=bootstrap-required-or-ci-only-when-prerequisites-are-missing\n'
printf 'BBF structural check delegated to artifact_packager.py; utils/pack_fw.py --no-sign is the reference path.\n'
printf 'DFU structural check delegated to artifact_packager.py; utils/dfu.py is the reference path.\n'

python3 tools/bazel/phase3_verify.py --require-artifacts --require-manifests
