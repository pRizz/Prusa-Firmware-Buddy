---
phase: 36-normalize-evidence-and-blocker-rows
reviewed: 2026-07-26T03:16:56Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - tools/bazel/phase32_blocker_register_triage.py
  - tools/bazel/phase32_blocker_register_triage_test.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 36: Code Review Report

**Reviewed:** 2026-07-26T03:16:56Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

The Phase 36 gap closure correctly handles the four default Phase 27/28 producer containers: missing or mistyped collections and non-object members become one atomic critical `malformed` blocker; unsupported top-level envelopes become one critical `unknown_unclassified` blocker; empty collections remain valid; canonical source-only IDs are stable; and the complete non-authorizing output bundle is published.

One regression remains in the configurable input-directory boundary. The public `--phase27-output-dir` and `--phase28-output-dir` options accept descendant directories under their canonical roots, but the new adapter lookup recognizes only the four default full paths. Valid producer bundles in accepted nested directories now abort before publication.

Repository guidance materially applied from `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the architecture, code-shape, testing, and verification standards. The review treated producer JSON as boundary data, required fail-closed behavior without swallowing unrelated validation errors, and checked that Phase 32 gains no downstream decision authority.

Verification performed:

- `python3 -m py_compile tools/bazel/phase32_blocker_register_triage.py tools/bazel/phase32_blocker_register_triage_test.py` — passed.
- `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` — 37 tests passed.
- Contract-only and wiring-only modes — passed.
- Default quick generation and security scan — passed; six required bundle files were present, with 43 canonical rows, 43 handoff rows, 43 unique IDs, and universal proof ineligibility.
- `git diff --check 3d04a5719..HEAD` for the two-file scope — passed.
- Focused nested-directory probe — reproduced the warning with exit code 1 and `ERROR: no Phase 27/28 container adapter for build/ci-evidence/phase27/nested/residual-risk-register.json`.

## Warnings

### WR-01: Container lookup breaks supported nested producer output directories

**File:** `tools/bazel/phase32_blocker_register_triage.py:1204-1207`

**Issue:** `phase27_rows()` and `phase28_rows()` deliberately accept any repo-relative descendant of `build/ci-evidence/phase27` or `build/ci-evidence/phase28` through `path_under()`, matching the producer scripts' scoped output-directory contract. The new loader then looks up the actual artifact path in `PHASE27_28_CONTAINER_ADAPTERS`, whose keys contain only the default full paths. As a result, a valid bundle supplied with `--phase27-output-dir build/ci-evidence/phase27/nested` or the Phase 28 equivalent raises `VerificationError` before emitting the register, derived views, handoff, or report. This is a behavioral regression from the previous direct container loading and also prevents malformed nested-run artifacts from receiving the intended visible fail-closed blocker.

**Fix:** Select the immutable adapter mapping by logical artifact role rather than by the caller-selected physical path. For example, pass a fixed adapter key separately from the actual source path:

```python
def load_phase27_28_container(
    root: Path,
    artifact_path: Path,
    adapter_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mapping = PHASE27_28_CONTAINER_ADAPTERS.get(adapter_path)
    if mapping is None:
        raise VerificationError(
            f"no Phase 27/28 container adapter for {adapter_path.as_posix()}"
        )
    # Read and report provenance using artifact_path.


residual_items, residual_problem_rows = load_phase27_28_container(
    root,
    residual_path,
    DEFAULT_PHASE27_OUTPUT_DIR / "residual-risk-register.json",
)
```

Apply the same separation at all four call sites and add valid and malformed nested-directory regressions for both Phase 27 and Phase 28.

______________________________________________________________________

_Reviewed: 2026-07-26T03:16:56Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
