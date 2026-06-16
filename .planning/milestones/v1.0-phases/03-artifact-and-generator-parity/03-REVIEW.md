---
phase: 03-artifact-and-generator-parity
reviewed: 2026-06-03T01:52:13Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/artifact_manifest.py
  - tools/bazel/artifact_metadata_compare.py
  - tools/bazel/artifact_packager.py
  - tools/bazel/artifact_rules.bzl
  - tools/bazel/generated_drift.py
  - tools/bazel/generator_rules.bzl
  - tools/bazel/manifests/representative_products.json
  - tools/bazel/phase3_artifacts.sh
  - tools/bazel/phase3_verify.py
  - tools/bazel/phase3_verify.sh
  - tools/bazel/phase3_workflow.sh
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 3: Code Review Report

**Reviewed:** 2026-06-03T01:52:13Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** clean after remediation

## Summary

Reviewed the listed Phase 3 Bazel, Python, shell, JSON, and facade files for correctness, security, and maintainability. The review applied repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the pinned Bright Builds architecture, code-shape, verification, and testing standards.

No critical security or data-loss issues were found. The initial review found verification false-positive risks in generated drift/update behavior, reference release metadata comparison, successful BBF packaging on bootstrapped machines, DFU suffix validation, auxiliary manifest wiring, and root `BUILD.bazel` staging. All actionable findings below were remediated, and the full Phase 3 local gate passed after fixes.

Scope note: `git check-ignore -v BUILD.bazel` reports the root `BUILD.bazel` as ignored by `.gitignore:2:/build*` on this checkout. It was still included here because the workflow explicitly listed it.

## Resolved Warnings

### WR-01: Successful BBF Reference Generation Copies Onto Itself

**File:** `tools/bazel/artifact_packager.py:147-151`
**Issue:** When `utils/pack_fw.py` succeeds, it writes the BBF beside the input firmware as `bin_path.with_suffix(".bbf")`. For these Phase 3 outputs that is the same path as `bbf_path`, so `shutil.copyfile(produced, bbf_path)` raises `SameFileError`. The path only appears healthy on machines missing prerequisites, because they take the bootstrap-required fallback instead.
**Fix:**
```python
produced = bin_path.with_suffix(".bbf")
if result.returncode == 0 and produced.exists():
    if produced.resolve() != bbf_path.resolve():
        shutil.copyfile(produced, bbf_path)
    return True
return False
```

### WR-02: DFU Structural Check Has A Tautological Suffix Test

**File:** `tools/bazel/artifact_packager.py:247`
**Issue:** `data.endswith(data[-4:])` is always true for non-empty data, so a file with a `DfuSe` prefix and `Target` text can pass even when the DFU suffix or CRC is corrupt.
**Fix:**
```python
import zlib

expected_crc = int.from_bytes(data[-4:], "little")
actual_crc = 0xFFFFFFFF & -zlib.crc32(data[:-4]) - 1
if len(data) < 16 or data[-8:-5] != b"UFD" or data[-5] != 16 or expected_crc != actual_crc:
    raise AssertionError("DFU structural check failed: invalid suffix/CRC surface")
```

### WR-03: Generated Drift Check And Update Targets Are No-Ops

**File:** `tools/bazel/generated_drift.py:85-104`
**Issue:** Check mode copies each tracked output to `output_dir` and then compares the tracked file to that fresh copy, so it cannot detect drift. Update mode only prints the declared update command and returns success without running it, so `generated_update` targets do not update source-tree outputs.
**Fix:**
```python
if update:
    subprocess.run(check.update_command, cwd=workspace, check=True)
    return []

# In check mode, run the generator into output_dir, then compare without copying
# tracked_path over generated_path first.
```

### WR-04: Resources Update Command Points To A Missing Script

**File:** `tools/bazel/generated_drift.py:30`
**Issue:** The `resources` registry entry declares `python3 utils/translations_and_fonts/generate_all_fonts.py`, but that script is absent in this repo; the checked-in generator is `utils/translations_and_fonts/generate_all_fonts.sh`, and resource headers also have a separate `utils/build.py --generate-resources` path. Once update execution is fixed, this surface will fail immediately or run the wrong generator.
**Fix:**
```python
"resources": DriftCheck(
    "resources",
    ("src/gui/res/cc",),
    ("src/resources/CMakeLists.txt",),
    ("python3", "utils/build.py", "--generate-resources"),
    "bytes",
    "ci-only",
    True,
),
```

### WR-05: Reference Release Compare Does Not Compare Generated Metadata

**File:** `tools/bazel/phase3_workflow.sh:90-93`
**Issue:** `reference_release_compare` calls `artifact_metadata_compare.py` with only the representative matrix and Phase 1 reference docs. Because `artifact_metadata_compare.py` accepts empty `--manifest` and `--status` lists, the target can pass without validating any generated artifact manifest or reference-format status metadata.
**Fix:**
```python
# artifact_metadata_compare.py
if not args.manifest and not args.status:
    raise AssertionError("at least one manifest or status file is required")
```

Then pass the generated `*.manifest.json`, `*.bbf.status.json`, and `*.dfu.status.json` files from the workflow or Bazel target that owns the representative artifacts.

### WR-06: Auxiliary Manifest Matrix Entry Is Not Wired Into Bazel Artifacts

**File:** `tools/bazel/manifests/representative_products.json:91`
**Issue:** The representative matrix advertises `xbuddy_extension_auxiliary_manifest`, but `tools/bazel/BUILD.bazel` defines and includes only the MINI, MINI noboot, MK4, and MINI resource package artifact targets in `representative_release_artifacts`. Builds of the representative artifact surface therefore omit one matrix entry.
**Fix:**
```python
filegroup(
    name = "xbuddy_extension_auxiliary_manifest_artifacts",
    srcs = ["fixtures/auxiliary/auxiliary_firmware_manifest.json"],
)
```

Add that target to `representative_release_artifacts`, or remove the matrix entry if auxiliary manifest-only parity is not part of Phase 3.

## Resolved Info

### IN-01: Root BUILD File Is Ignored By The Current Git Ignore Rule

**File:** `BUILD.bazel:1`
**Issue:** `git check-ignore -v BUILD.bazel` reports `.gitignore:2:/build*`, so normal broad staging can skip the root Bazel entrypoint on this checkout. That makes the root aliases easy to leave out of the Phase 3 commit.
**Fix:** Add a narrow exception such as `!/BUILD.bazel` after `/build*`, or otherwise document and use a forced-add workflow for the root Bazel file.

---

_Reviewed: 2026-06-03T01:52:13Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
