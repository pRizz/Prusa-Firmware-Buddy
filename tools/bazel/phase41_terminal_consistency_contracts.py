#!/usr/bin/env python3
from __future__ import annotations

# Frozen from the approved Phase 31-41 VALIDATION.md contracts. Runtime
# validation rows are observations and must never define their own expected set.
EXPECTED_VALIDATION_IDENTITIES = {
    31: (
        "31-W0-01",
        "31-W0-02",
        "31-W0-03",
        "31-W0-04",
        "31-W0-05",
    ),
    32: (
        "32-01-01",
        "32-01-02",
        "32-01-03",
        "32-01-04",
    ),
    33: (
        "33-01-01",
        "33-01-02",
        "33-01-03",
        "33-01-04",
    ),
    34: (
        "34-01-01",
        "34-01-02",
        "34-01-03",
    ),
    35: (
        "35-01-01",
        "35-01-02",
        "35-01-03",
    ),
    36: (
        "36-01-01",
        "36-01-02",
        "36-01-03",
        "36-02-01",
        "36-02-02",
    ),
    37: (
        "37-01-01",
        "37-01-02",
        "37-02-01",
        "37-02-02",
        "37-02-03",
    ),
    38: (
        "38-01-01",
        "38-01-02",
        "38-02-01",
        "38-02-02",
        "38-02-03",
    ),
    39: (
        "39-01-01",
        "39-01-02",
        "39-01-03",
    ),
    40: (
        "Baseline",
        "Rust domain",
        "Utilities",
        "Phases 5–11",
        "Phases 13–17",
        "Phases 18–28",
        "Phases 31–38",
        "Firmware tests",
        "Parser/UI/WUI",
        "Network/media",
        "Persistent storage",
        "Hardware/auxiliary",
        "Print/safety",
        "Terminal reconciliation",
    ),
    41: (
        "41-01-01",
        "41-01-02",
        "41-01-03",
        "41-02-01",
        "41-02-02",
        "41-03-01",
        "41-03-02",
    ),
}
