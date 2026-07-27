#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(
    os.environ.get(
        "BUILD_WORKSPACE_DIRECTORY",
        Path(__file__).resolve().parents[2],
    ))
sys.path.insert(0, (ROOT / "tools/bazel").as_posix())

import phase40_file_length_policy as policy

BASELINE_PATH = ROOT / ".bright-builds-rules-checks.tsv"
TEMPORARY_REASON = (
    "temporary: campaign=policy-test; "
    "remove when file is below 629 lines and campaign gates pass")
OWNED_REASON = (
    "permanent: owned deep module; "
    "deletion-test=removing any coherent region would break the central abstraction"
)


def baseline_entries() -> tuple[policy.LedgerEntry, ...]:
    return policy.parse_ledger(BASELINE_PATH.read_text(encoding="utf-8"))


def render_entries(entries: tuple[policy.LedgerEntry, ...]) -> str:
    return "".join(f"{entry.check_id}\t{entry.path}\t{entry.reason}\n"
                   for entry in sorted(entries, key=lambda entry: entry.path))


class LedgerParsingTests(unittest.TestCase):

    def test_accepts_active_shrink_only_ledger(self) -> None:
        # Arrange
        contents = BASELINE_PATH.read_text(encoding="utf-8")

        # Act
        entries = policy.parse_ledger(contents)
        summary = policy.validate_policy(entries)

        # Assert
        active_temporary_paths = {
            entry.path
            for entry in entries if entry.reason.startswith("temporary:")
        }
        self.assertEqual(
            summary.permanent_count,
            len(policy.FROZEN_PERMANENT_PATHS) + summary.owned_permanent_count,
        )
        self.assertEqual(summary.temporary_count, len(active_temporary_paths))
        self.assertLessEqual(active_temporary_paths,
                             policy.ORIGINAL_TEMPORARY_PATHS)

    def test_rejects_row_with_extra_field(self) -> None:
        # Arrange
        contents = (
            "file-lengths\tsrc/example.cpp\t"
            "temporary: campaign=test; remove when file is below 629 lines "
            "and campaign gates pass\textra\n")

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "exactly three"):
            policy.parse_ledger(contents)

        # Assert
        self.assertIn("extra", contents)

    def test_rejects_duplicate_path(self) -> None:
        # Arrange
        first = baseline_entries()[0]
        contents = render_entries((first, first))

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "duplicate"):
            policy.parse_ledger(contents)

        # Assert
        self.assertEqual(contents.count(first.path), 2)

    def test_rejects_unsorted_paths(self) -> None:
        # Arrange
        entries = baseline_entries()
        contents = "".join((
            f"{entries[1].check_id}\t{entries[1].path}\t{entries[1].reason}\n",
            f"{entries[0].check_id}\t{entries[0].path}\t{entries[0].reason}\n",
        ))

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "sorted"):
            policy.parse_ledger(contents)

        # Assert
        self.assertGreater(entries[1].path, entries[0].path)

    def test_rejects_unapproved_reason(self) -> None:
        # Arrange
        entry = replace(baseline_entries()[0],
                        reason="permanent: because it is large")
        contents = render_entries((entry, ))

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "unapproved reason"):
            policy.parse_ledger(contents)

        # Assert
        self.assertIn("because it is large", contents)


class ShrinkOnlyPolicyTests(unittest.TestCase):

    def test_rejects_temporary_set_growth(self) -> None:
        # Arrange
        entries = baseline_entries()
        added = policy.LedgerEntry(
            check_id="file-lengths",
            path="src/new_oversized_file.cpp",
            reason=TEMPORARY_REASON,
        )
        grown = policy.parse_ledger(render_entries(entries + (added, )))

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "temporary set grew"):
            policy.validate_policy(grown)

        # Assert
        self.assertNotIn(added.path, policy.ORIGINAL_TEMPORARY_PATHS)

    def test_rejects_frozen_provenance_path_reclassified_as_temporary(
            self) -> None:
        # Arrange
        entries = baseline_entries()
        frozen_path = min(policy.FROZEN_PERMANENT_PATHS)
        changed = tuple(
            replace(entry, reason=TEMPORARY_REASON) if entry.path ==
            frozen_path else entry for entry in entries)
        parsed = policy.parse_ledger(render_entries(changed))

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "frozen permanent"):
            policy.validate_policy(parsed)

        # Assert
        self.assertIn(frozen_path, policy.FROZEN_PERMANENT_PATHS)

    def test_rejects_unauthorized_owned_permanence(self) -> None:
        # Arrange
        entries = baseline_entries()
        unauthorized_path = min(
            entry.path for entry in entries
            if entry.reason.startswith("temporary:")
            and entry.path not in policy.LOCKED_OWNED_PATHS)
        changed = tuple(
            replace(entry, reason=OWNED_REASON) if entry.path ==
            unauthorized_path else entry for entry in entries)
        parsed = policy.parse_ledger(render_entries(changed))

        # Act
        with self.assertRaisesRegex(policy.PolicyError,
                                    "unauthorized owned permanence"):
            policy.validate_policy(parsed)

        # Assert
        self.assertNotIn(unauthorized_path, policy.LOCKED_OWNED_PATHS)

    def test_accepts_temporary_set_shrinkage(self) -> None:
        # Arrange
        entries = baseline_entries()
        active_temporary_entries = tuple(
            entry for entry in entries
            if entry.reason.startswith("temporary:"))
        active_owned_count = sum(
            entry.reason.startswith(policy.OWNED_REASON_PREFIX)
            for entry in entries)
        removed_path = active_temporary_entries[0].path
        changed = tuple(entry for entry in entries
                        if entry.path != removed_path)

        # Act
        summary = policy.validate_policy(changed)

        # Assert
        self.assertEqual(summary.temporary_count,
                         len(active_temporary_entries) - 1)
        self.assertEqual(
            summary.permanent_count,
            len(policy.FROZEN_PERMANENT_PATHS) + active_owned_count,
        )

    def test_accepts_arbitrary_valid_temporary_subset(self) -> None:
        # Arrange
        entries = baseline_entries()
        permanent_entries = tuple(entry for entry in entries
                                  if not entry.reason.startswith("temporary:"))
        temporary_subset = tuple(
            entry for index, entry in enumerate(entries)
            if entry.reason.startswith("temporary:") and index % 3 == 0)

        # Act
        summary = policy.validate_policy(permanent_entries + temporary_subset)

        # Assert
        self.assertEqual(summary.temporary_count, len(temporary_subset))
        self.assertEqual(summary.total_count,
                         len(permanent_entries) + len(temporary_subset))

    def test_accepts_locked_owned_conversion(self) -> None:
        # Arrange
        entries = baseline_entries()
        locked_path = min(policy.LOCKED_OWNED_PATHS)
        locked_entry = next(entry for entry in entries
                            if entry.path == locked_path)
        active_temporary_count = sum(
            entry.reason.startswith("temporary:") for entry in entries)
        active_owned_count = sum(
            entry.reason.startswith(policy.OWNED_REASON_PREFIX)
            for entry in entries)
        changed = tuple(
            replace(entry, reason=OWNED_REASON) if entry.path ==
            locked_path else entry for entry in entries)
        parsed = policy.parse_ledger(render_entries(changed))

        # Act
        summary = policy.validate_policy(parsed)

        # Assert
        was_temporary = locked_entry.reason.startswith("temporary:")
        self.assertEqual(summary.owned_permanent_count,
                         active_owned_count + int(was_temporary))
        self.assertEqual(summary.temporary_count,
                         active_temporary_count - int(was_temporary))


class TerminalPolicyTests(unittest.TestCase):

    def terminal_entries(self) -> tuple[policy.LedgerEntry, ...]:
        entries = baseline_entries()
        terminal_entries = []
        for entry in entries:
            if entry.path in policy.FROZEN_PERMANENT_PATHS:
                terminal_entries.append(entry)
            elif entry.path in policy.LOCKED_OWNED_PATHS:
                terminal_entries.append(replace(entry, reason=OWNED_REASON))
        return tuple(terminal_entries)

    def test_rejects_temporary_owned_path_in_terminal_mode(self) -> None:
        # Arrange
        locked_path = min(policy.LOCKED_OWNED_PATHS)
        entries = tuple(
            replace(entry, reason=TEMPORARY_REASON) if entry.path ==
            locked_path else entry for entry in self.terminal_entries())

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "terminal"):
            policy.validate_policy(entries, terminal=True)

        # Assert
        self.assertEqual(len(policy.ORIGINAL_TEMPORARY_PATHS), 95)

    def test_accepts_exact_terminal_union(self) -> None:
        # Arrange
        entries = self.terminal_entries()

        # Act
        summary = policy.validate_policy(entries, terminal=True)

        # Assert
        self.assertEqual(summary.permanent_count, 841)
        self.assertEqual(summary.temporary_count, 0)
        self.assertEqual(summary.owned_permanent_count, 3)

    def test_rejects_terminal_set_missing_locked_path(self) -> None:
        # Arrange
        entries = self.terminal_entries()
        missing_path = min(policy.LOCKED_OWNED_PATHS)
        incomplete = tuple(entry for entry in entries
                           if entry.path != missing_path)

        # Act
        with self.assertRaisesRegex(policy.PolicyError, "terminal exact set"):
            policy.validate_policy(incomplete, terminal=True)

        # Assert
        self.assertNotIn(missing_path, {entry.path for entry in incomplete})


if __name__ == "__main__":
    unittest.main()
