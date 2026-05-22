#!/usr/bin/env python3
"""Parse a GitHub Issue Form body for the reserve-ids workflow.

Reads the issue body from $ISSUE_BODY, extracts the three form fields, validates
them, and writes outputs to $GITHUB_OUTPUT for downstream workflow steps:

  dataset_count       integer 0..20
  reserve_deposition  "yes" | "no"
  deposition_types    JSON array, e.g. ["annotation","tomogram"]; "[]" if none
"""
from __future__ import annotations

import json
import os
import re
import sys

MAX_DATASETS = 20

HEADING_DATASET_COUNT = "Number of dataset IDs to reserve"
HEADING_RESERVE_DEPOSITION = "Also reserve a deposition?"
HEADING_DEPOSITION_TYPES = "Deposition type(s)"

VALID_DEPOSITION_TYPES = {"annotation", "tomogram", "dataset"}


def parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^###\s+(.*?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def parse_checkboxes(block: str) -> list[str]:
    selected: list[str] = []
    for line in block.splitlines():
        m = re.match(r"^\s*-\s*\[(.)]\s*(.+?)\s*$", line)
        if not m:
            continue
        mark, label = m.group(1), m.group(2).strip()
        if mark.lower() == "x":
            selected.append(label)
    return selected


def die(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "")
    if not body.strip():
        die("Issue body is empty.")

    sections = parse_sections(body)

    raw_count = sections.get(HEADING_DATASET_COUNT, "").strip()
    if raw_count in ("", "_No response_"):
        raw_count = "0"
    try:
        dataset_count = int(raw_count)
    except ValueError:
        die(f"'{HEADING_DATASET_COUNT}' must be an integer, got: {raw_count!r}")
    if dataset_count < 0 or dataset_count > MAX_DATASETS:
        die(f"'{HEADING_DATASET_COUNT}' must be between 0 and {MAX_DATASETS}, got: {dataset_count}")

    reserve_deposition = sections.get(HEADING_RESERVE_DEPOSITION, "").strip().lower()
    if reserve_deposition not in ("yes", "no"):
        die(f"'{HEADING_RESERVE_DEPOSITION}' must be 'yes' or 'no', got: {reserve_deposition!r}")

    types_block = sections.get(HEADING_DEPOSITION_TYPES, "")
    deposition_types = parse_checkboxes(types_block)
    unknown = [t for t in deposition_types if t not in VALID_DEPOSITION_TYPES]
    if unknown:
        die(f"Unknown deposition type(s): {unknown}. Allowed: {sorted(VALID_DEPOSITION_TYPES)}")

    if reserve_deposition == "yes" and not deposition_types:
        die("At least one deposition type must be checked when reserving a deposition.")
    if reserve_deposition == "no" and dataset_count == 0:
        die("Nothing to reserve: dataset_count is 0 and reserve_deposition is 'no'.")

    out_path = os.environ.get("GITHUB_OUTPUT")
    if not out_path:
        die("GITHUB_OUTPUT is not set.")
    with open(out_path, "a", encoding="utf-8") as fh:
        fh.write(f"dataset_count={dataset_count}\n")
        fh.write(f"reserve_deposition={reserve_deposition}\n")
        fh.write(f"deposition_types={json.dumps(deposition_types)}\n")

    print(f"Parsed: dataset_count={dataset_count}, reserve_deposition={reserve_deposition}, "
          f"deposition_types={deposition_types}")


if __name__ == "__main__":
    main()
