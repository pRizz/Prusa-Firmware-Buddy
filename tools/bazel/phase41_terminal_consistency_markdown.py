from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from phase41_terminal_consistency_policy import Violation


@dataclass(frozen=True)
class MarkdownTable:
    headers: tuple[str, ...]
    rows: tuple[dict[str, str], ...]
    valid: bool

    @property
    def normalized_headers(self) -> tuple[str, ...]:
        return tuple(header.casefold() for header in self.headers)


class BoundaryParser:

    def __init__(self, root: Path) -> None:
        self.root = root
        self.violations: list[Violation] = []
        self._phase41_summary_time_loaded = False
        self._maybe_phase41_summary_time: datetime | None = None

    def violation(self, path: str, code: str, observed: object,
                  expected: object) -> None:
        self.violations.append(
            Violation(path, code,
                      str(observed)[:160],
                      str(expected)[:160]))

    def read_text(self, relative_path: str) -> str | None:
        try:
            return (self.root / relative_path).read_text(encoding="utf-8")
        except (FileNotFoundError, OSError, UnicodeError):
            self.violation(relative_path, "P41_BOUNDARY_READ", "unreadable",
                           "readable UTF-8 file")
            return None

    def read_optional_text(self, relative_path: str) -> str | None:
        try:
            return (self.root / relative_path).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except (OSError, UnicodeError):
            self.violation(relative_path, "P41_BOUNDARY_READ", "unreadable",
                           "readable UTF-8 file")
            return None

    def frontmatter(self, path: str,
                    text: str | None) -> dict[str, str] | None:
        if text is None:
            return None
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            self.violation(path, "P41_FRONTMATTER_MALFORMED",
                           "missing opening delimiter", "YAML frontmatter")
            return None
        try:
            closing = lines.index("---", 1)
        except ValueError:
            self.violation(path, "P41_FRONTMATTER_MALFORMED",
                           "missing closing delimiter", "YAML frontmatter")
            return None
        values: dict[str, str] = {}
        for line in lines[1:closing]:
            if not line or line[0].isspace() or ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            if key in values:
                self.violation(path, "P41_FRONTMATTER_DUPLICATE", key,
                               "unique top-level keys")
                return None
            values[key] = raw_value.strip().strip('"').strip("'")
        return values

    def nested_frontmatter(self, path: str,
                           text: str | None) -> dict[str, object] | None:
        if text is None:
            return None
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            self.violation(path, "P41_FRONTMATTER_MALFORMED",
                           "missing opening delimiter", "YAML frontmatter")
            return None
        try:
            closing = lines.index("---", 1)
        except ValueError:
            self.violation(path, "P41_FRONTMATTER_MALFORMED",
                           "missing closing delimiter", "YAML frontmatter")
            return None
        root: dict[str, object] = {}
        stack: list[tuple[int, dict[str, object]]] = [(-2, root)]
        for line_number, line in enumerate(lines[1:closing], start=2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            leading_whitespace = line[:len(line) - len(line.lstrip())]
            indentation = len(leading_whitespace)
            if "\t" in leading_whitespace or indentation % 2 or ":" not in line:
                self.violation(path, "P41_FRONTMATTER_NESTING",
                               f"line {line_number}",
                               "two-space mapping indentation")
                return None
            key, raw_value = line.strip().split(":", 1)
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
                self.violation(path, "P41_FRONTMATTER_NESTING",
                               f"line {line_number}:{key}",
                               "plain mapping key")
                return None
            while stack and indentation <= stack[-1][0]:
                stack.pop()
            if not stack or indentation != stack[-1][0] + 2:
                self.violation(path, "P41_FRONTMATTER_NESTING",
                               f"line {line_number}:indent={indentation}",
                               "one mapping level")
                return None
            mapping = stack[-1][1]
            normalized_keys = {existing.casefold() for existing in mapping}
            if key.casefold() in normalized_keys:
                self.violation(path, "P41_FRONTMATTER_DUPLICATE", key,
                               "unique case-normalized mapping keys")
                return None
            value_text = raw_value.strip()
            if not value_text:
                child: dict[str, object] = {}
                mapping[key] = child
                stack.append((indentation, child))
                continue
            maybe_value = _yaml_scalar(value_text)
            if maybe_value is _INVALID_YAML_SCALAR:
                self.violation(path, "P41_FRONTMATTER_SCALAR",
                               f"line {line_number}:{value_text}",
                               "integer, string, or inline integer list")
                return None
            mapping[key] = maybe_value
        return root

    def required_labeled_block(self,
                               path: str,
                               text: str,
                               label: str,
                               identity: str | None = None) -> str:
        lines = _lines_outside_fences(text)
        pattern = re.compile(rf"^\s*\*\*{re.escape(label)}:\*\*\s*$")
        matches = [
            index for index, line in enumerate(lines)
            if pattern.fullmatch(line)
        ]
        block_name = identity or label
        if len(matches) != 1:
            self.violation(path, "P41_LABELED_BLOCK_REQUIRED",
                           f"{block_name}:{len(matches)}",
                           "one required labeled block")
            return ""
        start = matches[0] + 1
        end = len(lines)
        for index in range(start, len(lines)):
            stripped = lines[index].strip()
            if stripped.startswith("## ") or stripped.startswith("| "):
                end = index
                break
            if index > start and re.fullmatch(r"\*\*[^*]+:\*\*", stripped):
                end = index
                break
        return "\n".join(lines[start:end]).strip()

    def required_section(
        self,
        path: str,
        text: str,
        headings: str | tuple[str, ...],
        identity: str | None = None,
    ) -> str:
        expected_headings = (headings, ) if isinstance(headings,
                                                       str) else headings
        expected = {heading.casefold() for heading in expected_headings}
        sections = [
            section for section in _level_two_sections(text)
            if section[0].casefold() in expected
        ]
        label = identity or " / ".join(expected_headings)
        if len(sections) != 1:
            self.violation(path, "P41_SECTION_REQUIRED",
                           f"{label}:{len(sections)}",
                           "one required level-two section")
            return ""
        return sections[0][1]

    def table_blocks(self, path: str, text: str) -> tuple[MarkdownTable, ...]:
        lines = _lines_outside_fences(text)
        tables: list[MarkdownTable] = []
        index = 0
        while index + 1 < len(lines):
            maybe_header = _table_cells(lines[index])
            maybe_separator = _table_cells(lines[index + 1])
            if (maybe_header is None or maybe_separator is None
                    or len(maybe_header) != len(maybe_separator) or
                    not all(_is_separator(cell) for cell in maybe_separator)):
                index += 1
                continue
            headers = tuple(cell.strip() for cell in maybe_header)
            normalized_headers = tuple(header.casefold() for header in headers)
            valid = True
            if (not all(headers)
                    or len(set(normalized_headers)) != len(headers)):
                self.violation(path, "P41_TABLE_HEADER_DUPLICATE", headers,
                               "unique nonempty case-normalized columns")
                valid = False
            index += 2
            rows: list[dict[str, str]] = []
            while index < len(lines):
                maybe_cells = _table_cells(lines[index])
                if maybe_cells is None:
                    break
                if len(maybe_cells) != len(headers):
                    self.violation(path, "P41_TABLE_ROW_WIDTH",
                                   f"{len(maybe_cells)} cells",
                                   f"{len(headers)} cells")
                    valid = False
                    index += 1
                    continue
                if all(_is_separator(cell) for cell in maybe_cells):
                    self.violation(path, "P41_TABLE_BLOCK_AMBIGUOUS", headers,
                                   "one contiguous header and separator")
                    valid = False
                    index += 1
                    continue
                if valid:
                    rows.append(dict(zip(headers, maybe_cells)))
                index += 1
            tables.append(MarkdownTable(headers, tuple(rows), valid))
        return tuple(tables)

    def required_table(
            self,
            path: str,
            text: str,
            required_columns: tuple[str, ...],
            identity: str,
            any_columns: tuple[str, ...] = (),
    ) -> list[dict[str, str]]:
        required = {column.casefold() for column in required_columns}
        alternatives = {column.casefold() for column in any_columns}
        matches = []
        for table in self.table_blocks(path, text):
            headers = set(table.normalized_headers)
            if required <= headers and (not alternatives
                                        or headers & alternatives):
                matches.append(table)
        if len(matches) != 1:
            self.violation(path, "P41_TABLE_REQUIRED",
                           f"{identity}:{len(matches)}",
                           "one required contiguous table")
            return []
        return list(matches[0].rows) if matches[0].valid else []


def _level_two_sections(text: str) -> tuple[tuple[str, str], ...]:
    headings: list[tuple[int, str, int, int]] = []
    offset = 0
    for line in _lines_with_fence_state(text):
        raw_line, in_fence = line
        if not in_fence:
            maybe_heading = re.fullmatch(r"(#{1,6})[ \t]+(.+?)[ \t]*",
                                         raw_line.rstrip("\r\n"))
            if maybe_heading:
                name = re.sub(r"[ \t]+#+[ \t]*$", "",
                              maybe_heading.group(2)).strip()
                headings.append((len(maybe_heading.group(1)), name, offset,
                                 offset + len(raw_line)))
        offset += len(raw_line)
    sections: list[tuple[str, str]] = []
    for index, (level, name, _, content_start) in enumerate(headings):
        if level != 2:
            continue
        content_end = len(text)
        for next_level, _, next_start, _ in headings[index + 1:]:
            if next_level <= level:
                content_end = next_start
                break
        sections.append((name, text[content_start:content_end]))
    return tuple(sections)


def _lines_with_fence_state(text: str) -> tuple[tuple[str, bool], ...]:
    lines: list[tuple[str, bool]] = []
    maybe_fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        maybe_marker = re.match(r"(`{3,}|~{3,})", stripped)
        is_fence_line = maybe_marker is not None
        lines.append((line, maybe_fence is not None or is_fence_line))
        if maybe_marker is None:
            continue
        marker = maybe_marker.group(1)
        if maybe_fence is None:
            maybe_fence = (marker[0], len(marker))
        elif marker[0] == maybe_fence[0] and len(marker) >= maybe_fence[1]:
            maybe_fence = None
    return tuple(lines)


def _lines_outside_fences(text: str) -> tuple[str, ...]:
    return tuple(line if not in_fence else ""
                 for line, in_fence in _lines_with_fence_state(text))


def _table_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return tuple(cell.strip() for cell in stripped.strip("|").split("|"))


def _is_separator(cell: str) -> bool:
    return re.fullmatch(r":?-{3,}:?", cell.strip()) is not None


_INVALID_YAML_SCALAR = object()


def _yaml_scalar(value: str) -> object:
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return ()
        items = tuple(item.strip() for item in body.split(","))
        if not all(re.fullmatch(r"-?\d+", item) for item in items):
            return _INVALID_YAML_SCALAR
        return tuple(int(item) for item in items)
    if ((value.startswith('"') and value.endswith('"'))
            or (value.startswith("'") and value.endswith("'"))):
        return value[1:-1]
    if re.fullmatch(r"[^\[\]{},#]+", value):
        return value
    return _INVALID_YAML_SCALAR
