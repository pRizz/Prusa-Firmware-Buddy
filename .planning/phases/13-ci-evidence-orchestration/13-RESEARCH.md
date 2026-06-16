# Phase 13: CI Evidence Orchestration - Research

**Researched:** 2026-06-16
**Domain:** GitHub Actions CI orchestration, source-backed evidence manifests, Bazel/just verifier wiring
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

The following locked decisions, discretion areas, and deferred ideas are copied verbatim from `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md`. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md]

### Locked Decisions

### CI Ownership and Triggering

- **D-01:** Add a new repo-owned CI evidence workflow instead of editing managed Bright Builds workflows. Existing `.github/workflows/bright-builds-auto-update.yml` remains upstream-managed and out of scope.
- **D-02:** The CI evidence workflow should run on pull requests that affect Rust, Bazel, verifier, manifest, planning, workflow, or release-evidence surfaces, and should also support manual `workflow_dispatch` runs.
- **D-03:** Main firmware Jenkins/Holly remains the existing firmware build/test pipeline. Phase 13 may cite it as current CI context, but the new cutover evidence gate should be self-contained and reviewable from repo-owned workflow files.
- **D-04:** CI commands must use repo-owned entrypoints such as Bazel labels, `just` recipes, or phase verifier scripts. Do not hide substantive logic in workflow YAML strings.

### Evidence Manifest Contract

- **D-05:** Add a Phase 13 CI evidence manifest contract that records each gate with requirement ID, owning phase, command, proof scope, expected artifact path, retained artifact kind, status vocabulary, and failure reason semantics.
- **D-06:** CI should generate a run-specific machine-readable evidence manifest under a deterministic ignored output directory, then upload it as an artifact. The checked-in manifest should define the schema and required gates; generated run outputs should stay out of source control.
- **D-07:** Gate rows must map directly to `CIEV-01`, `CIEV-02`, and `CIEV-03`, and should preserve links back to archived v1.0 evidence rows rather than creating roadmap-only claims.
- **D-08:** Failure rows must be actionable: each failed or skipped gate identifies the command, requirement or evidence row, owner phase, artifact path, and failure reason without requiring maintainers to rerun local commands.

### Artifact Retention and Redaction

- **D-09:** CI artifacts should include verifier logs, manifest snapshots, normalized comparison outputs where available, and redacted evidence summaries. The plan may use placeholder or dry-run outputs for non-local gates only when explicitly labeled as pending/non-local.
- **D-10:** Artifact names and paths may be committed as contracts, but generated logs, run manifests, firmware packages, raw crash dumps, private certificates, signing keys, Connect tokens, Wi-Fi credentials, and credential values must not be committed.
- **D-11:** Artifact retention should be visible in the CI workflow through the platform artifact-upload step and should avoid relying on local workspace state after the job exits.
- **D-12:** If a gate cannot run locally in CI yet, the manifest should record a pending or non-local status with the required later evidence, not a pass claim.

### Verification and Failure Ownership

- **D-13:** Add a Phase 13 verifier and regression tests following the Phase 11 standard-library Python pattern. It should validate the CI evidence manifest, workflow trigger/path coverage, artifact upload wiring, redaction/overclaim guards, Bazel/just exposure, and lifecycle metadata.
- **D-14:** Expose Phase 13 verification through Bazel and `just phase13-verify`, and keep the command narrow enough to run as the Phase 13 local verification gate.
- **D-15:** The workflow should run the aggregate cutover verifier or an explicit Phase 13 wrapper around it, but must keep non-local simulator, hardware, live-service, release-candidate, signing, storage-media, MMU, RS485, toolchanger, retained-code, and maintainer approval evidence classified as pending until later phases attach artifacts.
- **D-16:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 13-2026-06-16T14-21-01`.

### the agent's Discretion

- Exact workflow file name, checked-in manifest file name, output directory, artifact names, retention days, row IDs, helper function boundaries, and schema field order are flexible if the surface remains deterministic, source-backed, redacted, covered by tests, and easy for maintainers to inspect.
- The planner may choose whether Phase 13 has one integrated implementation plan or a small number of sub-tasks inside one plan, but the roadmap expects a single completed plan for the phase.
- Prefer small standard-library Python helpers, JSON manifests, Bazel/just wrappers, and concise workflow steps over broad CI rewrites or firmware build-system changes.

### Deferred Ideas (OUT OF SCOPE)

- Actual simulator flow implementation belongs to Phase 14.
- Hardware, safety, media, UI input, MMU, RS485, and toolchanger evidence execution belongs to Phase 15.
- Live Connect, WUI, TLS, telemetry, proxy, and transfer evidence belongs to Phase 16.
- Release-candidate artifact, signing, provenance, resource, WUI, ESP, MMU, and auxiliary package proof belongs to Phase 17.
- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CIEV-01 | Maintainer can run the aggregate cutover verifier in CI for every pull request that changes Rust, Bazel, verifier, manifest, or release-evidence surfaces. | Use a new repo-owned GitHub Actions workflow with `pull_request.paths` for Rust, Bazel, verifier, manifest, planning, workflow, and release-evidence paths, plus `workflow_dispatch`; route work to a Phase 13 Python wrapper that runs Phase 11 aggregate verification and records results. [VERIFIED: .planning/REQUIREMENTS.md] [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] |
| CIEV-02 | Maintainer can inspect a machine-readable CI evidence manifest that records gate status, owning phase, command, artifact path, and failure reason for each cutover gate. | Add a checked-in Phase 13 manifest contract under `tools/bazel/manifests/` and a generated per-run JSON manifest under `build/ci-evidence/phase13/`; validate fields, status vocabulary, source links, lifecycle, and non-local/pending semantics with `phase13_ci_evidence.py`. [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: tools/bazel/phase11_verify.py] |
| CIEV-03 | Maintainer can download retained CI artifacts for verifier logs, manifest snapshots, normalized comparison outputs, and redacted evidence summaries without relying on local workspace state. | Use `actions/upload-artifact` with explicit artifact name, explicit retention, `if-no-files-found: error`, and upload paths rooted in non-hidden `build/ci-evidence/phase13/`; copy snapshots from hidden `.planning` only after redaction into that directory. [VERIFIED: .planning/REQUIREMENTS.md] [CITED: https://github.com/actions/upload-artifact] |
</phase_requirements>

## Summary

Phase 13 should be planned as a thin CI evidence orchestration layer, not as a new parity proof layer. Phase 11 already provides the aggregate cutover contracts, non-local proof boundaries, redaction scans, source path validation, lifecycle checks, Bazel labels, and `just phase11-verify`; Phase 13 should wrap and retain those outputs in CI while preserving pending/non-local status for later v1.1 phases. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/manifests/phase11_parity_pyramid.json] [VERIFIED: .planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md]

The key implementation surface is a standard-library Python verifier/orchestrator plus a checked-in JSON contract and a new repo-owned GitHub Actions workflow. The workflow YAML should stay thin because Bright Builds code-shape rules say substantial foreign-language logic must live in scripts or repo-owned files, not inline YAML strings. [VERIFIED: standards/core/code-shape.md] [VERIFIED: tools/bazel/phase11_verify.py]

**Primary recommendation:** Create `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase13_ci_evidence_test.py`, `tools/bazel/manifests/phase13_ci_evidence_contract.json`, `.github/workflows/ci-evidence.yml`, Bazel labels/root aliases, and `just phase13-verify`; make the workflow run the Python wrapper, upload `build/ci-evidence/phase13/`, and fail only after evidence artifacts are written. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: justfile] [CITED: https://github.com/actions/upload-artifact]

## Project Constraints (from AGENTS.md)

- `AGENTS.md` is the repo instruction entrypoint, and it requires reading `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before plan, review, implementation, or audit work. [VERIFIED: AGENTS.md]
- The Bright Builds managed workflow block is upstream-owned; downstream fixes belong outside managed blocks and in repo-owned extension points. [VERIFIED: AGENTS.md] [VERIFIED: AGENTS.bright-builds.md]
- The project goal is a Rust+Bazel firmware replacement that preserves current firmware behavior, with Bazel authoritative from the start and `justfile` required for common developer commands. [VERIFIED: AGENTS.md]
- Bright Builds Rules apply with no active local override beyond placeholder rows in `standards-overrides.md`. [VERIFIED: AGENTS.md] [VERIFIED: standards-overrides.md]
- Verification should prefer repo-owned entrypoints over hand-chained low-level commands. [VERIFIED: standards/core/verification.md]
- New pure/business logic needs focused unit tests, and unit tests should make Arrange, Act, Assert clear when structure is not trivial. [VERIFIED: standards/core/testing.md]
- Automation scripts should use early returns where clearer, keep substantial logic out of YAML strings, and write rerunnable diagnostic summaries/logs to gitignored paths. [VERIFIED: standards/core/code-shape.md]
- No project skills were found under `.claude/skills/` or `.agents/skills/` in this session. [VERIFIED: find .claude/skills .agents/skills -maxdepth 2 -name SKILL.md]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python standard library | Repo requires Python 3.8+; local probe found Python 3.14.4 | Manifest parsing, command execution capture, redaction scanning, JSON output, unittest regression tests | Phase 11 verifier and tests are Python stdlib-only and already enforce manifest schema, source paths, lifecycle, security, and wiring checks. [VERIFIED: AGENTS.md] [VERIFIED: python3 --version] [VERIFIED: tools/bazel/phase11_verify.py] |
| GitHub Actions workflow syntax | Current GitHub Docs, 2026 | PR path filters, manual dispatch, minimal permissions, failure/always upload behavior | GitHub supports multiple events, `pull_request.paths`, and `workflow_dispatch`; path filters are the right trigger surface for CIEV-01. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] |
| `actions/upload-artifact` | Current README examples show `@v7`; use current major during implementation unless repo policy pins actions | Retained downloadable CI evidence | Official README documents `retention-days`, `if-no-files-found`, immutable artifact behavior, hidden-file defaults, and artifact digest display. [CITED: https://github.com/actions/upload-artifact] |
| Bazel `shell_binary` wrapper | Local Bazel 9.1.1; repo rule in `tools/bazel/shell_rules.bzl` | Expose `phase13_verify` and `phase13_verify_tests` via `bazel run` | Earlier phases use the local `shell_binary` rule over `rust_workflow.sh`, with data/runfiles declared in `tools/bazel/BUILD.bazel`. [VERIFIED: bazel --version] [VERIFIED: tools/bazel/shell_rules.bzl] [VERIFIED: tools/bazel/BUILD.bazel] |
| `just` facade | Local just 1.48.0 | Provide `just phase13-verify` | Existing `justfile` exposes each completed phase verifier through stable recipes. [VERIFIED: just --version] [VERIFIED: justfile] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| `jq` | Local jq 1.7.1 | Manual developer inspection of generated CI evidence JSON | Use in docs/examples only; do not require it inside Phase 13 verifier because Python stdlib can parse JSON. [VERIFIED: jq --version] |
| `actions/checkout` | Current README usage shows `@v6`; existing managed workflow uses `@v4` and remains out of scope | Check out repository sources in the new repo-owned workflow | Use the current major for the new workflow unless repo policy pins action majors; do not update the managed Bright Builds workflow as part of Phase 13. [CITED: https://github.com/actions/checkout] [VERIFIED: .github/workflows/bright-builds-auto-update.yml] |
| `cargo` / `rustc` | Local cargo/rustc 1.91.1 | Existing Phase 11 `just phase11-verify` runs Rust format, lint, build, and unit tests | Keep Phase 13 CI wrapper Python-first so GitHub Actions does not assume Bazel/just/Rust availability, but preserve Bazel/just exposure tests locally. [VERIFIED: cargo --version] [VERIFIED: rustc --version] [VERIFIED: justfile] |
| Jenkins/Holly `archiveArtifacts` | Existing Jenkinsfile surface | Current main firmware build/test artifact context | Cite as context only; do not move Phase 13 gate into Jenkins because user decision D-03 requires a repo-owned GitHub Actions evidence gate. [VERIFIED: utils/holly/build-pr.jenkins] [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Python stdlib verifier | JSON Schema library or PyYAML | Adds dependencies that the Phase 11 pattern intentionally avoids; stdlib is enough for fixed schema checks and redaction scanning. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: AGENTS.md] |
| Python workflow wrapper | Large inline workflow `run:` blocks | Violates Bright Builds guidance against hiding substantial logic inside YAML strings and makes local reruns harder. [VERIFIED: standards/core/code-shape.md] |
| GitHub Actions artifact upload | Commit generated CI manifests/logs | Generated run outputs are explicitly out of source control, and `.gitignore` already ignores `/build*` and `/target/`. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] [VERIFIED: .gitignore] |
| New repo-owned workflow | Modify `.github/workflows/bright-builds-auto-update.yml` | The Bright Builds workflow is explicitly managed upstream and must remain out of Phase 13 scope. [VERIFIED: .github/workflows/bright-builds-auto-update.yml] [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] |

**Installation:**

No npm, pip, or Cargo dependency addition is recommended for Phase 13. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: AGENTS.md]

**Version verification:**

- Local tool probes found Python 3.14.4, Bash 3.2.57, Bazel 9.1.1, just 1.48.0, git 2.53.0, jq 1.7.1, Node 24.13.0, cargo 1.91.1, and rustc 1.91.1. [VERIFIED: python3 --version] [VERIFIED: bash --version] [VERIFIED: bazel --version] [VERIFIED: just --version] [VERIFIED: git --version] [VERIFIED: jq --version] [VERIFIED: node --version] [VERIFIED: cargo --version] [VERIFIED: rustc --version]
- `pre-commit` is not available on the local PATH, but Phase 13 does not need pre-commit for its verifier if it follows the Phase 11 stdlib pattern. [VERIFIED: pre-commit --version]
- GitHub Actions artifact retention defaults and maximums are platform policy, so the workflow should set an explicit `retention-days` value that stays within public-repo limits unless the repo owner chooses otherwise. [CITED: https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization]

## Architecture Patterns

### Recommended Project Structure

```text
.github/workflows/
└── ci-evidence.yml                         # Repo-owned PR/manual evidence workflow
tools/bazel/
├── phase13_ci_evidence.py                  # Contract verifier + CI evidence writer
├── phase13_ci_evidence_test.py             # Stdlib unittest regression tests
├── rust_workflow.sh                        # Add phase13 dispatch cases
├── BUILD.bazel                             # Add phase13 shell_binary labels
└── manifests/
    └── phase13_ci_evidence_contract.json   # Checked-in schema/gate contract
BUILD.bazel                                 # Root aliases and Phase 13 docs filegroup
justfile                                    # just phase13-verify
build/ci-evidence/phase13/                  # Generated, ignored, uploaded run outputs
```

This structure follows the existing phase verifier pattern under `tools/bazel/`, root aliases in `BUILD.bazel`, and `justfile` facade recipes. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: justfile]

### Pattern 1: Checked-In Contract, Generated Run Output

**What:** Keep the durable CI evidence schema and required gate rows in `tools/bazel/manifests/phase13_ci_evidence_contract.json`, and write per-run output files under `build/ci-evidence/phase13/`. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] [VERIFIED: .gitignore]

**When to use:** Use this for CIEV-02 and CIEV-03 so CI evidence is inspectable after the job exits without committing generated logs or manifests. [VERIFIED: .planning/REQUIREMENTS.md]

**Example:**

```json
{
  "schema_version": "1",
  "phase": "13-ci-evidence-orchestration",
  "phase_lifecycle_id": "13-2026-06-16T14-21-01",
  "output_root": "build/ci-evidence/phase13",
  "gates": [
    {
      "id": "ciev-01-aggregate-cutover-verifier",
      "requirement_id": "CIEV-01",
      "owning_phase": "13-ci-evidence-orchestration",
      "command": "python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13",
      "proof_scope": "ci",
      "expected_artifact_path": "build/ci-evidence/phase13/run-manifest.json",
      "retained_artifact_kind": "machine-readable-ci-manifest",
      "allowed_statuses": ["passed", "failed", "skipped", "pending-non-local"],
      "failure_reason_semantics": "failed and skipped rows must name command, owner phase, requirement/evidence row, artifact path, and reason"
    }
  ]
}
```

Source pattern: Phase 11 manifests use schema version, phase, lifecycle id, required row IDs, source artifacts, commands, proof scope, and status vocabularies. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] [VERIFIED: tools/bazel/phase11_verify.py]

### Pattern 2: CI Wrapper Writes Evidence Before Failing

**What:** The Phase 13 CI wrapper should execute each gate, capture stdout/stderr to log files, write `run-manifest.json`, copy redacted source snapshots into `build/ci-evidence/phase13/`, then return a nonzero exit code if required gates failed. [VERIFIED: tools/bazel/phase11_verify.py] [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/expressions]

**When to use:** Use this for CIEV-02 and CIEV-03 so failure ownership survives in artifacts even when the workflow status is red. [VERIFIED: .planning/REQUIREMENTS.md]

**Example:**

```python
def run_gate(root: Path, gate: dict[str, object], output_dir: Path) -> dict[str, object]:
    command = require_string(gate, "command", gate["id"])
    log_path = output_dir / "logs" / f"{gate['id']}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        shlex.split(command),
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    log_path.write_text(result.stdout, encoding="utf-8")

    return {
        "id": gate["id"],
        "requirement_id": gate["requirement_id"],
        "owning_phase": gate["owning_phase"],
        "command": command,
        "status": "passed" if result.returncode == 0 else "failed",
        "artifact_path": log_path.as_posix(),
        "failure_reason": "" if result.returncode == 0 else f"exit code {result.returncode}",
    }
```

Source pattern: Phase 11 already uses `subprocess.run(..., stdout=PIPE, stderr=STDOUT, check=False)` and returns actionable verifier messages. [VERIFIED: tools/bazel/phase11_verify.py]

### Pattern 3: Thin Workflow YAML

**What:** The workflow should check out the repo, run one repo-owned Python command, upload the evidence directory with explicit retention, and avoid embedding schema logic in YAML. [VERIFIED: standards/core/code-shape.md] [CITED: https://github.com/actions/upload-artifact]

**When to use:** Use this for CIEV-01 and CIEV-03. [VERIFIED: .planning/REQUIREMENTS.md]

**Example:**

```yaml
name: CI Evidence

on:
  workflow_dispatch:
  pull_request:
    paths:
      - "rust/**"
      - "Cargo.toml"
      - "Cargo.lock"
      - "BUILD.bazel"
      - "MODULE.bazel"
      - "tools/bazel/**"
      - ".planning/**"
      - ".github/workflows/**"
      - "justfile"

permissions:
  contents: read

jobs:
  cutover-evidence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Run CI evidence wrapper
        run: python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13

      - name: Upload CI evidence
        if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v7
        with:
          name: phase13-ci-evidence-${{ github.run_id }}
          path: build/ci-evidence/phase13/
          retention-days: 30
          if-no-files-found: error
```

GitHub Docs require separately configured events when one event has filters and another does not, and `pull_request.paths` is the documented path-filter mechanism. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]

### Anti-Patterns to Avoid

- **Editing the Bright Builds managed workflow:** `.github/workflows/bright-builds-auto-update.yml` is upstream-managed and out of Phase 13 scope. [VERIFIED: .github/workflows/bright-builds-auto-update.yml] [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md]
- **Uploading `.planning/**` directly:** `actions/upload-artifact` ignores hidden files/directories by default, and `.planning` is a hidden directory; copy redacted snapshots into `build/ci-evidence/phase13/manifest-snapshots/` instead. [CITED: https://github.com/actions/upload-artifact] [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md]
- **Using `continue-on-error` to keep upload running:** That can make failing gates look green in the PR UI; keep the wrapper responsible for producing artifacts, then fail the step after writing evidence. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/expressions]
- **Making workflow YAML the source of truth:** Workflow YAML should invoke repo-owned scripts; it should not define gate schema, status vocabularies, redaction rules, or path validation. [VERIFIED: standards/core/code-shape.md]
- **Treating pending simulator/hardware/live/release gates as passed:** Phase 13 must preserve pending/non-local classifications until Phases 14-18 attach evidence. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CI artifact retention | Custom zip/upload script or committed logs | `actions/upload-artifact` with explicit `retention-days`, `if-no-files-found: error`, and a non-hidden output directory | GitHub's action already handles retained workflow artifacts and documents retention, hidden-file behavior, immutable artifacts, and artifact IDs/digests. [CITED: https://github.com/actions/upload-artifact] |
| Trigger changed-path detection | Custom git diff logic inside YAML | `pull_request.paths` for the declared CI evidence surfaces | GitHub evaluates path filters for `pull_request` and supports glob patterns. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] |
| Evidence schema validation | Generic JSON schema dependency | Phase-specific Python validators matching Phase 11 | The contract has fixed row IDs and project-specific overclaim/redaction semantics, which Phase 11 already validates with stdlib Python. [VERIFIED: tools/bazel/phase11_verify.py] |
| Secret redaction checks | Ad hoc grep commands in YAML | Reuse Phase 11-style regex checks inside `phase13_ci_evidence.py` | Existing tests already reject private-key headers, certificate bytes, token/password field names, and overclaim phrases. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/phase11_verify_test.py] |
| Local command facade | New CI-only command names | Bazel `shell_binary` labels and `just phase13-verify` | Existing phases expose verifier tests before aggregate verification through `tools/bazel/BUILD.bazel`, `rust_workflow.sh`, root aliases, and `justfile`. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: tools/bazel/rust_workflow.sh] [VERIFIED: justfile] |

**Key insight:** Phase 13's complexity is evidence ownership and lifecycle truth, not CI mechanics; the plan should reuse platform artifact upload and Phase 11 verifier patterns while making the CI wrapper deterministic and locally testable. [VERIFIED: tools/bazel/phase11_verify.py] [CITED: https://github.com/actions/upload-artifact]

## Common Pitfalls

### Pitfall 1: Hidden `.planning` Paths Are Not Uploaded

**What goes wrong:** Artifact upload silently omits snapshots under `.planning/` because hidden files and directories are ignored by default. [CITED: https://github.com/actions/upload-artifact]

**Why it happens:** `actions/upload-artifact` defines hidden files as files beginning with `.` or files inside folders beginning with `.`, and `.planning` matches that rule. [CITED: https://github.com/actions/upload-artifact]

**How to avoid:** Copy only redacted planning snapshots needed for evidence into `build/ci-evidence/phase13/manifest-snapshots/` and upload that non-hidden directory. [VERIFIED: .gitignore] [CITED: https://github.com/actions/upload-artifact]

**Warning signs:** Workflow uploads `path: .planning/...`, or uses `include-hidden-files: true` without explicit exclusions and redaction tests. [CITED: https://github.com/actions/upload-artifact]

### Pitfall 2: Path-Filtered Required Check Stays Pending

**What goes wrong:** A required PR check can remain pending if path filters skip the workflow. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]

**Why it happens:** GitHub Docs state skipped workflows due to path filtering, branch filtering, or commit messages leave associated checks in a Pending state. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]

**How to avoid:** Either do not make this path-filtered workflow a universally required branch protection check, or add a separate always-running lightweight status if branch protection needs an always-present check. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]

**Warning signs:** Branch protection requires "CI Evidence" but PRs touching only docs outside the filter never run it. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]

### Pitfall 3: Artifact Upload Does Not Run After Failure

**What goes wrong:** The verifier step fails before the upload step, so maintainers see a red workflow but cannot download the evidence manifest. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/expressions]

**Why it happens:** GitHub applies a default `success()` condition unless an `if` expression includes a status check function. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/expressions]

**How to avoid:** Make the Phase 13 wrapper write artifacts before returning failure, and set the upload step to `if: ${{ !cancelled() }}` or another explicit status condition. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/expressions]

**Warning signs:** The workflow has no explicit `if` on the artifact upload step, or the wrapper exits on first failed gate before writing `run-manifest.json`. [VERIFIED: standards/core/code-shape.md]

### Pitfall 4: CI Evidence Overclaims Later-Phase Proof

**What goes wrong:** A CI run marks simulator, hardware, live-service, release-candidate, signing, retained-code, or approval evidence as passed even though Phase 13 only orchestrates local/CI evidence. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md]

**Why it happens:** Phase 11 contains many non-local rows that are source-backed locally but not cutover-ready. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json]

**How to avoid:** Phase 13 status vocabulary should include `pending-non-local`, and the verifier must reject pass claims for later-phase surfaces unless attached artifacts exist and the owning later phase is complete. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: .planning/ROADMAP.md]

**Warning signs:** Words such as `cutover complete`, `hardware verified locally`, `simulator passed locally`, `byte-identical firmware`, or `reference path removed` appear in generated or checked-in Phase 13 evidence. [VERIFIED: tools/bazel/phase11_verify.py]

### Pitfall 5: Workflow Permissions Are Too Broad

**What goes wrong:** The new workflow gets write-capable `GITHUB_TOKEN` permissions even though it only checks out code, runs verifiers, and uploads artifacts. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token]

**Why it happens:** Action code can access `github.token` even if the token is not explicitly passed, so permissions should be minimized. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token]

**How to avoid:** Set workflow or job `permissions: contents: read`; do not add secrets or write scopes for Phase 13. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token]

**Warning signs:** `permissions: write-all`, `contents: write`, repository secrets, or signing tokens appear in the workflow. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token]

## Code Examples

### Phase 13 Verifier Modes

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 13 CI evidence orchestration.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--workflow-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--output-dir", default="build/ci-evidence/phase13")
    return parser.parse_args()
```

Source pattern: Phase 11 verifier uses mode flags for quick, all, requirement, comparison, cutover, security, Rust, and wiring checks. [VERIFIED: tools/bazel/phase11_verify.py]

### Phase 13 Test Shape

```python
def test_workflow_rejects_missing_artifact_upload(self) -> None:
    # Arrange
    temp_dir, root = self.make_temp_root()
    with temp_dir:
        self.copy_phase13_surface(root)
        self.write_file(root, ".github/workflows/ci-evidence.yml", "name: CI Evidence\n")

        # Act
        result = self.run_verifier(["--workflow-only"], maybe_root=root)

    # Assert
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("actions/upload-artifact", result.stdout)
```

Source pattern: Phase 11 verifier tests use `unittest`, temp roots, fixture copying, subprocess execution, and explicit Arrange/Act/Assert comments. [VERIFIED: tools/bazel/phase11_verify_test.py] [VERIFIED: standards/core/testing.md]

### Bazel And Just Wiring

```python
errors.extend(
    require_file_contains(
        root,
        Path("justfile"),
        [
            "phase13-verify:",
            "bazel run //tools/bazel:phase13_verify_tests",
            "bazel run //tools/bazel:phase13_verify",
        ],
    )
)
```

Source pattern: Phase 11 wiring check verifies `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, root `BUILD.bazel`, and `justfile` contain required labels and commands. [VERIFIED: tools/bazel/phase11_verify.py]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Local-only cutover evidence and `just phase11-verify` | CI-retained run manifest and uploaded evidence bundle | Phase 13 scope, v1.1 roadmap | Maintainers can inspect CI evidence without local reruns. [VERIFIED: .planning/ROADMAP.md] |
| Uploading source hidden directories directly | Copy redacted snapshots into non-hidden evidence output directory before upload | Current `actions/upload-artifact` behavior | Avoids skipped hidden files and reduces accidental secret upload risk. [CITED: https://github.com/actions/upload-artifact] |
| Mutable or shared artifact names across jobs | Unique per-run artifact names or explicit overwrite semantics | Upload-artifact v4+ behavior described in current README | Avoids accidental artifact mutation/corruption. [CITED: https://github.com/actions/upload-artifact] |
| Unscoped `GITHUB_TOKEN` permissions | Explicit minimum `permissions` | GitHub Actions documented security practice | Limits token exposure for a read-only verifier workflow. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token] |

**Deprecated/outdated:**

- Treating `.github/workflows/bright-builds-auto-update.yml` as editable downstream is outdated for this repo because the file is managed upstream. [VERIFIED: .github/workflows/bright-builds-auto-update.yml] [VERIFIED: AGENTS.bright-builds.md]
- Treating Phase 11 non-local rows as passed CI proof is invalid; Phase 11 explicitly preserves simulator, hardware, live network/TLS, storage media, release-candidate, signing, MMU, RS485, toolchanger, retained-code acceptance, maintainer approval, and reference demotion as residual gates. [VERIFIED: .planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `actions/upload-artifact@v7` is the current major to use because the current official README examples show `@v7`; if repo policy intentionally pins older action majors, the planner should use that policy instead. [ASSUMED] | Standard Stack / Workflow Example | Workflow action version review churn; low behavioral risk if verifier checks artifact semantics rather than exact major. |
| A2 | `retention-days: 30` is a reasonable default because GitHub allows 1-90 days for public repos and 1-400 for private repos, but organization policy may set a lower cap. [ASSUMED] | Architecture Patterns | CI may reject a retention value above org cap; planner can lower the contract value while keeping explicit retention. |

## Open Questions

1. **Artifact retention policy**
   - What we know: GitHub defaults artifacts/logs to 90 days and allows public repo settings from 1 to 90 days and private repo settings from 1 to 400 days. [CITED: https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization]
   - What's unclear: The Prusa GitHub organization or enterprise maximum retention cap is not visible from the repository. [ASSUMED]
   - Recommendation: Use explicit `retention-days: 30` unless the org cap requires a lower value; make the Phase 13 verifier require explicit retention but allow the chosen value to be changed in one manifest/workflow contract. [ASSUMED]

2. **CI runner tool availability**
   - What we know: Local probes found Bazel and just installed, but GitHub-hosted runner availability was not verified from this repo. [VERIFIED: bazel --version] [VERIFIED: just --version]
   - What's unclear: Whether this repository's GitHub Actions environment has Bazel, just, and Rust preinstalled or should install them. [ASSUMED]
   - Recommendation: Make the workflow run `python3 tools/bazel/phase13_ci_evidence.py --ci` directly and let Phase 13 verifier validate Bazel/just exposure locally; do not require Bazel/just in the GitHub workflow unless the plan adds explicit setup steps. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md]

3. **Branch protection strategy**
   - What we know: GitHub path-filtered workflows can leave required checks pending when skipped. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]
   - What's unclear: Which checks are required in this repository's branch protection settings. [ASSUMED]
   - Recommendation: Do not assume this path-filtered workflow can be a universal required check without a companion always-running check or branch-protection review. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 13 verifier, tests, CI wrapper | yes | 3.14.4 local | Use repo minimum Python 3.8+ in CI. [VERIFIED: python3 --version] [VERIFIED: AGENTS.md] |
| Bash | `rust_workflow.sh`, `justfile` shell | yes | GNU bash 3.2.57 local | Keep scripts POSIX-ish plus existing Bash pattern. [VERIFIED: bash --version] [VERIFIED: tools/bazel/rust_workflow.sh] |
| Bazel | Local label exposure and `just phase13-verify` | yes | 9.1.1 local | Workflow can run Python wrapper directly if Bazel is not installed in GitHub Actions. [VERIFIED: bazel --version] |
| just | Developer facade | yes | 1.48.0 local | Direct `bazel run //tools/bazel:phase13_verify` remains available. [VERIFIED: just --version] |
| Git | Local inspection and CI checkout context | yes | 2.53.0 local | GitHub checkout action supplies workspace in CI. [VERIFIED: git --version] [CITED: https://github.com/actions/checkout] |
| jq | Manual JSON inspection only | yes | 1.7.1 local | Python stdlib JSON parser. [VERIFIED: jq --version] |
| cargo/rustc | Existing Rust checks if `just phase11-verify` is run | yes | cargo/rustc 1.91.1 local | Phase 13 CI wrapper should not require Rust unless the plan explicitly adds setup. [VERIFIED: cargo --version] [VERIFIED: rustc --version] |
| pre-commit | Existing Holly formatting stage; not Phase 13 verifier | no | not on PATH | Do not require pre-commit for Phase 13 local gate. [VERIFIED: pre-commit --version] |

**Missing dependencies with no fallback:**

- None for the recommended Phase 13 Python-first local verification path. [VERIFIED: tools/bazel/phase11_verify.py]

**Missing dependencies with fallback:**

- `pre-commit` is missing locally; Phase 13 can avoid it by using Python stdlib tests and existing Bazel/just wiring. [VERIFIED: pre-commit --version]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` plus Phase 13 verifier modes and Bazel/just smoke wiring. [VERIFIED: tools/bazel/phase11_verify_test.py] |
| Config file | `.planning/config.json` has `workflow.nyquist_validation: true`; Bazel/just config lives in `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, and `justfile`. [VERIFIED: .planning/config.json] [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: justfile] |
| Quick run command | `python3 tools/bazel/phase13_ci_evidence.py --quick` [ASSUMED] |
| Full suite command | `just phase13-verify` [ASSUMED] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CIEV-01 | Workflow triggers on PR path changes for Rust, Bazel, verifier, manifest, planning, workflow, and release-evidence surfaces, and supports `workflow_dispatch`. | verifier/unit | `python3 tools/bazel/phase13_ci_evidence_test.py` and `python3 tools/bazel/phase13_ci_evidence.py --workflow-only` | no - Wave 0 |
| CIEV-02 | Checked-in contract and generated run manifest expose gate status, owner phase, command, artifact path, and failure reason. | verifier/unit | `python3 tools/bazel/phase13_ci_evidence_test.py` and `python3 tools/bazel/phase13_ci_evidence.py --contract-only --ci --output-dir build/ci-evidence/phase13` | no - Wave 0 |
| CIEV-03 | Workflow uploads retained logs, manifest snapshots, normalized comparisons, and redacted summaries from non-hidden output directory with explicit retention. | verifier/unit | `python3 tools/bazel/phase13_ci_evidence.py --workflow-only --security-only` | no - Wave 0 |

### Sampling Rate

- **Per task commit:** Run the focused mode for the touched surface: `--contract-only`, `--workflow-only`, `--security-only`, or `--wiring-only`. [VERIFIED: .planning/config.json] [VERIFIED: tools/bazel/phase11_verify.py]
- **Per wave merge:** Run `python3 tools/bazel/phase13_ci_evidence_test.py` and `python3 tools/bazel/phase13_ci_evidence.py --quick`. [ASSUMED]
- **Phase gate:** Run `just phase13-verify`, `python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13`, and `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" verify lifecycle 13 --require-plans --raw`. [VERIFIED: .planning/config.json] [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase13_ci_evidence_contract.json` - covers CIEV-01, CIEV-02, CIEV-03 gate contract. [VERIFIED: .planning/REQUIREMENTS.md]
- [ ] `tools/bazel/phase13_ci_evidence.py` - contract verifier, workflow verifier, security scan, CI run writer. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md]
- [ ] `tools/bazel/phase13_ci_evidence_test.py` - regression tests for missing fields, hidden upload paths, overclaim strings, redaction markers, path filters, and failure manifest semantics. [VERIFIED: tools/bazel/phase11_verify_test.py]
- [ ] `.github/workflows/ci-evidence.yml` - repo-owned PR/manual workflow. [VERIFIED: .github/workflows/stale.yml] [VERIFIED: .github/workflows/bright-builds-auto-update.yml]
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 13 verifier labels/facade. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: tools/bazel/rust_workflow.sh] [VERIFIED: justfile]

## Security Domain

### Applicable ASVS Categories

OWASP ASVS is a web application security verification standard, and this project template requires mapping applicable categories for security-relevant phases. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 13 must not add authentication flows or secrets; use default GitHub token only through platform actions. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token] |
| V3 Session Management | no | No application session state is introduced. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] |
| V4 Access Control | yes | Set workflow/job `permissions: contents: read` and avoid write scopes. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token] |
| V5 Input Validation | yes | Validate manifest schema, row IDs, source paths, artifact paths, status vocabulary, and path traversal using Phase 11-style Python checks. [VERIFIED: tools/bazel/phase11_verify.py] |
| V6 Cryptography | yes, limited | Do not generate, upload, or commit private keys, certificates, signing material, token values, firmware payload bytes, or raw crash dumps. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] [VERIFIED: tools/bazel/phase11_verify.py] |

### Known Threat Patterns for Phase 13

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Artifact leaks secret-bearing evidence | Information Disclosure | Redaction scanner rejects private-key headers, certificate markers, token/password/private-key field names, raw crash dumps, firmware payload markers, and checked-in generated run outputs. [VERIFIED: tools/bazel/phase11_verify.py] |
| Workflow overclaims non-local proof | Spoofing / Repudiation | Status vocabulary requires `pending-non-local` for later-phase gates and rejects overclaim phrases. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md] |
| Path traversal in artifact/source paths | Tampering | Use repo-relative path validation matching Phase 11 `require_source_artifacts`. [VERIFIED: tools/bazel/phase11_verify.py] |
| YAML hides unreviewed command logic | Tampering / Maintainability | Keep workflow YAML as thin orchestration and put schema/run logic in Python. [VERIFIED: standards/core/code-shape.md] |
| Excessive GitHub token permissions | Elevation of Privilege | Set minimum workflow permissions and do not pass secrets. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token] |

## Likely Files Planner Should Modify

- `.github/workflows/ci-evidence.yml` or similar repo-owned workflow; do not edit `.github/workflows/bright-builds-auto-update.yml`. [VERIFIED: .github/workflows/bright-builds-auto-update.yml]
- `tools/bazel/manifests/phase13_ci_evidence_contract.json` for checked-in gate/schema contract. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json]
- `tools/bazel/phase13_ci_evidence.py` for contract validation, CI run output generation, redaction/overclaim scanning, workflow checks, and wiring checks. [VERIFIED: tools/bazel/phase11_verify.py]
- `tools/bazel/phase13_ci_evidence_test.py` for stdlib regression coverage. [VERIFIED: tools/bazel/phase11_verify_test.py]
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` for Bazel/just exposure. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: tools/bazel/rust_workflow.sh] [VERIFIED: justfile]
- `.gitignore` only if the plan chooses an output directory outside `/build*` or `/target/`; recommended output under `build/ci-evidence/phase13/` needs no `.gitignore` change. [VERIFIED: .gitignore]

## Sources

### Primary (HIGH confidence)

- `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md` - locked Phase 13 decisions, deferred scope, lifecycle ID, canonical references. [VERIFIED]
- `.planning/REQUIREMENTS.md` - CIEV-01, CIEV-02, CIEV-03 requirement text. [VERIFIED]
- `.planning/ROADMAP.md` - Phase 13 goal, dependencies, success criteria, later-phase boundaries. [VERIFIED]
- `.planning/STATE.md` - v1.1 current position and carried decisions. [VERIFIED]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/verification.md`, `standards/core/testing.md`, `standards/core/code-shape.md` - repo and Bright Builds constraints. [VERIFIED]
- `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`, `tools/bazel/manifests/phase11_*.json` - existing aggregate verifier, tests, manifests, overclaim/redaction/lifecycle patterns. [VERIFIED]
- `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - Bazel and just wiring pattern. [VERIFIED]
- `.github/workflows/bright-builds-auto-update.yml`, `.github/workflows/stale.yml`, `utils/holly/build-pr.jenkins` - managed workflow boundary, existing GitHub Actions style, Holly artifact context. [VERIFIED]

### Secondary (MEDIUM confidence)

- GitHub Actions workflow syntax docs - path filters, multiple events, path-filter pending behavior, job permissions syntax. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]
- GitHub Actions expressions docs - status check functions and default success behavior. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/expressions]
- GitHub GITHUB_TOKEN docs - least-privilege token permissions. [CITED: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token]
- `actions/checkout` README - current checkout major and workspace behavior. [CITED: https://github.com/actions/checkout]
- `actions/upload-artifact` README - retention-days, no-files behavior, hidden files, immutable artifacts, artifact IDs/digests. [CITED: https://github.com/actions/upload-artifact]
- GitHub artifact/log retention docs - default and configurable retention limits. [CITED: https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization]
- OWASP ASVS project page - security verification standard context. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

### Tertiary (LOW confidence)

- None used as authoritative sources. [VERIFIED: source review]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - Phase 13 is constrained to existing stdlib Python, Bazel, just, and GitHub Actions surfaces; local and official docs were checked. [VERIFIED: tools/bazel/phase11_verify.py] [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]
- Architecture: HIGH - Existing Phase 11 verifier/manifests/tests and Bazel/just wiring provide direct patterns. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/BUILD.bazel]
- Pitfalls: HIGH - Hidden artifact behavior, path-filter pending behavior, token permission guidance, and status conditions are documented by GitHub; overclaim/redaction risks are enforced by Phase 11. [CITED: https://github.com/actions/upload-artifact] [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] [VERIFIED: tools/bazel/phase11_verify.py]

**Research date:** 2026-06-16
**Valid until:** 2026-07-16 for repo-specific patterns; recheck GitHub Actions action versions and artifact docs before implementation if planning starts after that date. [ASSUMED]
