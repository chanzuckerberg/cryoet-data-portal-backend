#!/usr/bin/env python3
"""Generate minimal stub YAML files in ingestion_tools/dataset_configs/.

Inputs (env):
  DATASET_IDS       JSON array of integers, e.g. "[10500,10501]"; "[]" if none
  DEPOSITION_ID     scalar integer string, or empty if no deposition reserved
  DEPOSITION_TYPES  JSON array of strings, e.g. ["annotation","tomogram"]

Outputs:
  ingestion_tools/dataset_configs/<id>.yaml           for each reserved dataset id
  ingestion_tools/dataset_configs/deposition_<id>.yaml when a deposition is reserved

When a deposition is reserved together with one or more datasets, every dataset
stub gets that deposition id wired into standardization_config.deposition_id.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIGS_DIR = REPO_ROOT / "ingestion_tools" / "dataset_configs"


def die(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


def render_dataset_stub(dataset_id: int, deposition_id: int | None) -> str:
    lines = [
        "datasets:",
        "  - metadata:",
        f"      dataset_identifier: {dataset_id}",
    ]
    if deposition_id is not None:
        lines += [
            "standardization_config:",
            f"  deposition_id: {deposition_id}",
        ]
    return "\n".join(lines) + "\n"


def render_deposition_stub(deposition_id: int, deposition_types: list[str]) -> str:
    types_inline = ", ".join(deposition_types)
    return (
        "depositions:\n"
        "  - metadata:\n"
        f"      deposition_identifier: {deposition_id}\n"
        f"      deposition_types: [{types_inline}]\n"
    )


def main() -> None:
    try:
        dataset_ids = json.loads(os.environ.get("DATASET_IDS", "[]") or "[]")
    except json.JSONDecodeError as exc:
        die(f"DATASET_IDS is not valid JSON: {exc}")
    if not isinstance(dataset_ids, list) or not all(isinstance(i, int) for i in dataset_ids):
        die(f"DATASET_IDS must be a JSON array of integers, got: {dataset_ids!r}")

    deposition_id_raw = (os.environ.get("DEPOSITION_ID") or "").strip()
    deposition_id: int | None = None
    if deposition_id_raw:
        try:
            deposition_id = int(deposition_id_raw)
        except ValueError:
            die(f"DEPOSITION_ID must be an integer, got: {deposition_id_raw!r}")

    try:
        deposition_types = json.loads(os.environ.get("DEPOSITION_TYPES", "[]") or "[]")
    except json.JSONDecodeError as exc:
        die(f"DEPOSITION_TYPES is not valid JSON: {exc}")
    if not isinstance(deposition_types, list) or not all(isinstance(t, str) for t in deposition_types):
        die(f"DEPOSITION_TYPES must be a JSON array of strings, got: {deposition_types!r}")

    if not dataset_ids and deposition_id is None:
        die("Nothing to generate: no dataset_ids and no deposition_id.")

    if not CONFIGS_DIR.is_dir():
        die(f"Configs directory not found: {CONFIGS_DIR}")

    written: list[Path] = []

    for ds_id in dataset_ids:
        path = CONFIGS_DIR / f"{ds_id}.yaml"
        if path.exists():
            die(f"Refusing to overwrite existing file: {path}")
        path.write_text(render_dataset_stub(ds_id, deposition_id), encoding="utf-8")
        written.append(path)

    if deposition_id is not None:
        path = CONFIGS_DIR / f"deposition_{deposition_id}.yaml"
        if path.exists():
            die(f"Refusing to overwrite existing file: {path}")
        path.write_text(render_deposition_stub(deposition_id, deposition_types), encoding="utf-8")
        written.append(path)

    print("Wrote:")
    for p in written:
        print(f"  {p.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
