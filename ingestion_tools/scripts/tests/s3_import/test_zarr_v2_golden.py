"""Default ingestion (without --dca) writes Zarr v2 / OME-NGFF 0.4 exactly as before the move to zarr-python 3.

The goldens were recorded with the code of origin/main before the switch (zarr 2.18, ome-zarr 0.9, numpy 1.26) by
tests/data_generators/make_zarr_v2_golden.py: the same files, equal .zgroup/.zarray/.zattrs, identical chunk content
and Blosc headers, and the same MRC data and header (except the label holding the conversion time).
"""

import json
import os
from pathlib import Path

import pytest

from common.fs import FileSystemApi
from common.image import make_pyramids
from tests.data_generators.make_zarr_v2_golden import CASES, SAMPLE_TOMOS, run_case

GOLDEN = json.loads((Path(__file__).parents[1] / "fixtures" / "zarr_v2_golden.json").read_text())
SAMPLE_TOMOS_S3 = "test-public-bucket/input_bucket/sample_tomos/"


def fetch_sample_tomos(dest: Path) -> Path:
    """Copy the sample inputs from the seeded test bucket (seed_moto.sh syncs test_infra/test_files there)."""
    fs = FileSystemApi.get_fs_api(
        mode="s3",
        force_overwrite=False,
        client_kwargs={"endpoint_url": os.getenv("ENDPOINT_URL", "http://motoserver:5566")},
    )
    fs.s3fs.get(SAMPLE_TOMOS_S3, f"{dest}/", recursive=True)
    return dest


@pytest.fixture(scope="module")
def sample_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """test_infra/test_files/input_bucket/sample_tomos from the checkout, or from the test bucket where the checkout
    is not available (the ingestor container only holds ingestion_tools)."""
    if SAMPLE_TOMOS.is_dir():
        return SAMPLE_TOMOS
    return fetch_sample_tomos(tmp_path_factory.mktemp("sample_tomos"))


@pytest.mark.parametrize("name", sorted(CASES))
def test_default_ingestion_matches_zarr2_output(name: str, tmp_path: Path, sample_dir: Path) -> None:
    fs = FileSystemApi.get_fs_api(mode="local", force_overwrite=False)
    actual = run_case(make_pyramids, fs, tmp_path, name, sample_dir=sample_dir)
    expected = GOLDEN[name]
    assert sorted(actual["zarr"]) == sorted(expected["zarr"]), "different files in the zarr"
    for rel, value in expected["zarr"].items():
        assert actual["zarr"][rel] == value, f"{rel} differs"
    assert actual["mrc"] == expected["mrc"]


def test_sample_inputs_from_the_test_bucket_match_the_checkout(tmp_path: Path) -> None:
    """The bucket copy used in the container holds the same sample inputs the goldens were recorded from."""
    if not SAMPLE_TOMOS.is_dir():
        pytest.skip("no checkout of test_infra here")
    fetched = fetch_sample_tomos(tmp_path)
    for p in SAMPLE_TOMOS.rglob("*"):
        if p.is_file():
            assert (fetched / p.relative_to(SAMPLE_TOMOS)).read_bytes() == p.read_bytes(), p.name
