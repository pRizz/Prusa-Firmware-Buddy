# Deferred Items

## phase40-10-host-target-closure | 2026-07-27 18:29

- **Discovered during:** Plan 40-10 focused host verification
- **Issue:** A clean `connect_planner_tests` link on macOS lacks direct `str_utils` and `string_view_utf8` dependencies. The unchanged Plan 09 binary still executes 21 cases and 197 assertions successfully.
- **Reason deferred:** The parent execution explicitly bounded Rule 3 host-target closure work after two earlier direct dependency fixes; planner source was byte-identical in this plan.
- **Suggested follow-up:** Add the missing implementation sources to the planner test target in a dedicated host-target closure pass and verify a clean relink.

## phase40-10-mini404-libfdt | 2026-07-27 18:29

- **Discovered during:** Plan 40-10 actual simulator parity execution
- **Issue:** Bundled x86_64 Mini404 aborts with status 134 because `/usr/local/opt/dtc/lib/libfdt.1.dylib` is unavailable on the ARM macOS host.
- **Reason deferred:** This is local simulator toolchain infrastructure outside the network/media refactoring scope.
- **Suggested follow-up:** Provide a native Mini404 build or a compatible `libfdt` runtime, then rerun `.venv/bin/pytest tests/integration --firmware build/mk4_release_noboot/firmware.bin`.

## phase40-12-phase10-validation-artifact | 2026-07-27 19:50

- **Discovered during:** Plan 40-12 auxiliary-controller verification
- **Issue:** `just phase10-verify` cannot copy the absent `.planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VALIDATION.md`; 13 tests error before evaluating the implementation, while the independent test passes.
- **Reason deferred:** The missing historical Phase 10 planning artifact predates this refactor and is outside the hardware/auxiliary file-length campaign.
- **Suggested follow-up:** Reconstruct or restore the Phase 10 validation artifact, then rerun `just phase10-verify`.

## phase40-12-simulator-profile-mismatch | 2026-07-27 19:50

- **Discovered during:** Plan 40-12 explicit integration simulator execution
- **Issue:** `.venv/bin/pytest tests/integration --firmware build-plan40-12-xl/xl_release_noboot/firmware.bin` selects the MK4 Mini404 machine and the simulator exits during setup; 6 tests skip and 22 error without behavioral execution.
- **Reason deferred:** The simulator command has no board/profile selector compatible with the XL image used to exercise the Dwarf master adapter, so this provides no refactor-specific simulator evidence.
- **Suggested follow-up:** Provide a matching simulator profile or supported firmware/image pairing and rerun the integration suite.
