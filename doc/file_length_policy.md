# File Length Exception Policy

Phase 40 uses `.bright-builds-rules-checks.tsv` as the only active exception authority for the managed file-length checker. The managed checker and `.github/workflows/bright-builds-checks.yml` are immutable inputs to this campaign.

## Ledger contract

Every active row has exactly three tab-separated fields:

```text
file-lengths<TAB>repo-relative-exact-path<TAB>reason
```

Rows are sorted by exact path and unique. Blank paths, non-normalized paths, duplicate paths, unknown check IDs, stale paths, empty reasons, extra fields, and unapproved reason prefixes fail closed.

The baseline is the live managed-checker set captured at Phase 40 start:

- 838 frozen permanent provenance or declarative paths
- 95 shrink-only temporary repo-owned campaign paths
- 933 active exceptions total
- zero unclassified managed-checker findings

No generated projection, second manifest, or merge-base comparison participates in policy. The committed TSV is canonical.

## Approved reason classes

- `permanent: imported/upstream; provenance=...` identifies vendored, upstream, compatibility-stub, or ST CMSIS sources whose ownership lies outside the refactoring campaign.
- `permanent: generated; source=...` identifies checked-in generated outputs and names the owning generator or pipeline.
- `permanent: declarative registry; deletion-test=...` is restricted to the three frozen central registry/configuration paths whose coherent entries cannot be removed without breaking their single authority.
- `temporary: campaign=<id>; remove when file is below 629 lines and campaign gates pass` identifies original repo-owned campaign debt. Temporary membership may only shrink.
- `permanent: owned deep module; deletion-test=...` is unavailable at baseline and may be introduced only for the three locked conversions below after campaign evidence passes.

The only repo-owned paths that may ever convert to permanent deep-module reasons are:

- `src/guiapi/include/Rect16.h`
- `src/connect/planner.cpp`
- `src/gui/screen_tools_mapping.cpp`

No other permanent-owned conversion is authorized. A conversion must retain a path-specific deletion test explaining why removing any coherent region would damage the central abstraction.

## Shrink-only campaign rule

A campaign removes a temporary row in the same atomic change that brings its file below 629 physical lines and proves the preserved contract. Temporary rows cannot be added, transferred to a different path, reclassified from the frozen permanent set, or retained after the checker reports them stale.

Terminal policy requires exact equality with the frozen 838 permanent paths plus the three locked owned deep modules: 841 permanent rows, zero temporary reasons, and zero managed-checker findings.

## Campaign evidence

Every campaign summary records the D-12 evidence fields:

- affected paths
- checker delta
- risk class
- executed targeted commands
- contract comparison
- residual risk

A wrapper that merely prints a reference command is not execution evidence. When a wrapper does not execute its underlying command, the campaign runs that command directly and records its actual status.

## Verification

`just phase40-verify` is the serial campaign and wave gate. It runs focused policy tests, validates the active ledger, and executes `bun scripts/bright-builds-check.ts all`. Terminal reconciliation uses `just phase40-verify --terminal` and is intentionally red until all temporary campaign debt is resolved.

Never suppress a failure by editing `scripts/bright-builds-check.ts` or `.github/workflows/bright-builds-checks.yml`.
