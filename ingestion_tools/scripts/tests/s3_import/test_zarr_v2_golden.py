"""Default ingestion (without --dca) writes Zarr v2 / OME-NGFF 0.4 exactly as before the move to zarr-python 3.

The goldens were recorded with the code of origin/main before the switch (zarr 2.18, ome-zarr 0.9, numpy 1.26) by
tests/data_generators/make_zarr_v2_golden.py: the same files, identical chunk bytes, equal .zgroup/.zarray/.zattrs
and the same MRC data and header (except the label holding the conversion time).
"""

import json
from pathlib import Path

import pytest

from common.fs import FileSystemApi
from common.image import make_pyramids
from tests.data_generators.make_zarr_v2_golden import CASES, run_case

GOLDEN = json.loads((Path(__file__).parents[1] / "fixtures" / "zarr_v2_golden.json").read_text())


@pytest.mark.parametrize("name", sorted(CASES))
def test_default_ingestion_matches_zarr2_output(name: str, tmp_path: Path) -> None:
    fs = FileSystemApi.get_fs_api(mode="local", force_overwrite=False)
    actual = run_case(make_pyramids, fs, tmp_path, name)
    expected = GOLDEN[name]
    assert sorted(actual["zarr"]) == sorted(expected["zarr"]), "different files in the zarr"
    for rel, value in expected["zarr"].items():
        assert actual["zarr"][rel] == value, f"{rel} differs"
    assert actual["mrc"] == expected["mrc"]
