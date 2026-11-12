import json
from unittest.mock import patch

import mrcfile
import numpy as np
import pytest
import zarr
from tenacity import stop_after_attempt, wait_none

from common import cryoet_profile as cp
from common.fs import FileSystemApi
from common.image import make_pyramids
from common.ome_zarr_writer import write_label_pyramid, write_region, write_v2_pyramid
from common.retry import is_s3_throttling

# Test retry constants (shorter times for fast test execution)
TEST_RETRY_MAX_ATTEMPTS = 3


def open_output(s3_fs: FileSystemApi, zarr_path: str) -> zarr.Group:
    return zarr.open_group(s3_fs.zarr_store(zarr_path), mode="r")


def read_json(s3_fs: FileSystemApi, path: str) -> dict:
    with s3_fs.open(path, "r") as f:
        return json.load(f)


def test_convert_mrc_to_mrc(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_mrc.mrc"
    make_pyramids(s3_fs, output_path, input_file)

    output_mrc = s3_fs.localreadable(output_path + ".mrc")
    mrc = mrcfile.open(output_mrc, "r")
    assert round(mrc.voxel_size.y.item(), 2) == 14.08

    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32

    assert round(mrc.header.rms.item(), 2) == 1.12
    assert round(mrc.header.dmean.item(), 1) == 2.5
    assert round(mrc.header.dmax.item(), 1) == 4
    assert round(mrc.header.dmin.item(), 1) == 1

    assert mrc.header.nxstart.item() == 0
    assert mrc.header.nystart.item() == 0
    assert mrc.header.nzstart.item() == 0

    assert mrc.header.mx.item() == 4
    assert mrc.header.my.item() == 4
    assert mrc.header.mz.item() == 4


def test_convert_zarr_to_mrc(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    # a Zarr v2 / OME-NGFF 0.4 source, as deposited (e.g. from copick)
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_omezarr.zarr"
    make_pyramids(s3_fs, output_path, input_file)

    output_mrc = s3_fs.localreadable(output_path + ".mrc")
    mrc = mrcfile.open(output_mrc, "r")
    assert round(mrc.voxel_size.y.item(), 2) == 14.08

    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32

    assert round(mrc.header.rms.item(), 2) == 1.12
    assert round(mrc.header.dmean.item(), 1) == 2.5
    assert round(mrc.header.dmax.item(), 1) == 4
    assert round(mrc.header.dmin.item(), 1) == 1

    assert mrc.header.nxstart.item() == 0
    assert mrc.header.nystart.item() == 0
    assert mrc.header.nzstart.item() == 0

    assert mrc.header.mx.item() == 4
    assert mrc.header.my.item() == 4
    assert mrc.header.mz.item() == 4


@pytest.mark.parametrize("input_name", ["input_mrc.mrc", "input_omezarr.zarr"])
def test_convert_mrc_to_omezarr(s3_fs: FileSystemApi, test_output_bucket: str, input_name: str) -> None:
    """Default ingestion: Zarr v2 / OME-NGFF 0.4 as before (3 levels, scale-only transforms, '/' chunk keys).
    test_zarr_v2_golden.py checks that the output is the same as that of the code before zarr-python 3."""
    output_path = f"{test_output_bucket}/output"
    make_pyramids(s3_fs, output_path, f"test-public-bucket/input_bucket/sample_tomos/{input_name}")

    group = open_output(s3_fs, f"{output_path}.zarr")
    assert group.metadata.zarr_format == 2
    attrs = group.attrs
    assert attrs["multiscales"][0]["axes"][0] == {"name": "z", "unit": "angstrom", "type": "space"}
    assert len(attrs["multiscales"][0]["datasets"]) == 3
    spacing = 14.08
    for ds in attrs["multiscales"][0]["datasets"]:
        assert ds["coordinateTransformations"][0]["scale"] == [spacing, spacing, spacing]
        spacing *= 2
    img_dim = 4
    for level in ("0", "1", "2"):
        assert group[level].shape == (img_dim, img_dim, img_dim)
        assert group[level].dtype == np.float32
        img_dim //= 2
    assert s3_fs.exists(f"{output_path}.zarr/.zattrs")
    assert not s3_fs.exists(f"{output_path}.zarr/zarr.json")
    assert s3_fs.exists(f"{output_path}.zarr/0/0/0/0")


@pytest.mark.parametrize("input_name", ["input_mrc.mrc", "input_omezarr.zarr"])
def test_convert_to_omezarr_v3_without_profile(s3_fs: FileSystemApi, test_output_bucket: str, input_name: str) -> None:
    """With --dca, volumes other than tomograms and tilt series (segmentation masks) keep their 3-level pyramid,
    written as Zarr v3 / OME-NGFF 0.5."""
    output_path = f"{test_output_bucket}/output"
    make_pyramids(s3_fs, output_path, f"test-public-bucket/input_bucket/sample_tomos/{input_name}", zarr_format=3)

    group = open_output(s3_fs, f"{output_path}.zarr")
    assert group.metadata.zarr_format == 3
    ome = group.attrs["ome"]
    assert ome["version"] == "0.5"
    assert ome["multiscales"][0]["axes"][0] == {"name": "z", "unit": "angstrom", "type": "space"}
    assert len(ome["multiscales"][0]["datasets"]) == 3
    spacing = 14.08
    for ds in ome["multiscales"][0]["datasets"]:
        assert ds["coordinateTransformations"][0]["scale"] == [spacing, spacing, spacing]
        spacing *= 2
    img_dim = 4
    for level in ("0", "1", "2"):
        assert group[level].shape == (img_dim, img_dim, img_dim)
        img_dim //= 2
    assert s3_fs.exists(f"{output_path}.zarr/zarr.json")
    assert not s3_fs.exists(f"{output_path}.zarr/.zattrs")
    assert s3_fs.exists(f"{output_path}.zarr/0/c/0/0/0")


@pytest.mark.parametrize("input_name", ["input_mrc.mrc", "input_omezarr.zarr"])
def test_convert_to_profile_volume(s3_fs: FileSystemApi, test_output_bucket: str, input_name: str) -> None:
    """Tomograms: int16 codes in a 5-D sharded Zarr v3 array, with the CF attributes, translations and statistics of
    the cryoET profile; the MRC is unchanged (float32 level 0)."""
    output_path = f"{test_output_bucket}/output"
    input_file = f"test-public-bucket/input_bucket/sample_tomos/{input_name}"
    make_pyramids(s3_fs, output_path, input_file, image_type="volume", voxel_spacing=14.08)

    zarr_path = f"{output_path}.zarr"
    group_meta = read_json(s3_fs, f"{zarr_path}/zarr.json")
    arrays = {k: read_json(s3_fs, f"{zarr_path}/{k}/zarr.json") for k in ("0", "1", "2")}
    assert cp.check_profile(group_meta, arrays) == []
    assert [arrays[k]["shape"] for k in ("0", "1", "2")] == [[1, 1, 4, 4, 4], [1, 1, 2, 2, 2], [1, 1, 1, 1, 1]]
    translation = group_meta["attributes"]["ome"]["multiscales"][0]["datasets"][1]["coordinateTransformations"][1]
    assert translation["translation"] == pytest.approx([0.0, 0.0, 7.04, 7.04, 7.04])
    assert s3_fs.exists(f"{zarr_path}/0/c/0/0/0/0/0")  # one shard

    mrc = mrcfile.open(s3_fs.localreadable(output_path + ".mrc"), "r")
    group = open_output(s3_fs, zarr_path)
    codes = group["0"][0, 0]
    decoded = cp.decode_codes(codes, dict(group["0"].attrs))
    # the sample tomogram holds integers: the encoding is lossless
    assert group["0"].attrs["scale_factor"] == 1.0
    np.testing.assert_array_equal(decoded, mrc.data)
    stats = group.attrs["dca"]["normalization_statistics"]["0"]["dataset_statistics"]
    assert stats["mean"] == pytest.approx(float(codes.mean()))


def test_convert_to_profile_tilt_series(s3_fs: FileSystemApi, test_output_bucket: str, tmp_path) -> None:
    """Tilt series: float32, Fourier-cropped levels, one shard per tilt, odd image sizes allowed."""
    data = np.random.default_rng(0).normal(10.0, 2.0, size=(3, 66, 43)).astype(np.float32)
    local_mrc = tmp_path / "ts.mrc"
    with mrcfile.new(local_mrc) as mrc:
        mrc.set_data(data)
        mrc.voxel_size = 1.68
    input_file = f"{test_output_bucket}/input/ts.mrc"
    s3_fs.s3fs.put(str(local_mrc), input_file)

    output_path = f"{test_output_bucket}/ts_output"
    make_pyramids(s3_fs, output_path, input_file, scale_z_axis=False, image_type="tilt_series", voxel_spacing=1.68)

    zarr_path = f"{output_path}.zarr"
    group_meta = read_json(s3_fs, f"{zarr_path}/zarr.json")
    arrays = {k: read_json(s3_fs, f"{zarr_path}/{k}/zarr.json") for k in ("0", "1", "2")}
    assert cp.check_profile(group_meta, arrays) == []
    group = open_output(s3_fs, zarr_path)
    np.testing.assert_array_equal(group["0"][:], data)
    assert group["2"].shape == (3, cp.fourier_plan(66, 4).m, cp.fourier_plan(43, 4).m)
    sections = group.attrs["dca"]["normalization_statistics"]["0"]["section_statistics"]
    assert sorted(sections) == ["0", "1", "2"]
    np.testing.assert_array_equal(mrcfile.open(s3_fs.localreadable(output_path + ".mrc")).data, data)


def test_mrc_int_overflow_fix(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/unsigned_ints.mrc"
    make_pyramids(s3_fs, output_path, input_file)

    output_mrc = s3_fs.localreadable(output_path + ".mrc")
    mrc = mrcfile.open(output_mrc, "r")
    assert mrc.header.dmin == -128
    assert mrc.header.dmax == 127
    assert mrc.data[0, 0, 0] == 0  # Original value was -128
    assert mrc.data[0, 1, 0] == -128  # Original value was 0
    assert mrc.data[0, 2, 0] == 127  # Original value was -1
    assert mrc.data[0, 3, 0] == -1  # Original value was 127


def test_mrc_int_normal(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/signed_ints.mrc"
    make_pyramids(s3_fs, output_path, input_file)

    output_mrc = s3_fs.localreadable(output_path + ".mrc")
    mrc = mrcfile.open(output_mrc, "r")
    assert mrc.header.dmin == -128
    assert mrc.header.dmax == 127
    assert mrc.data[0, 0, 0] == -128
    assert mrc.data[0, 1, 0] == 0
    assert mrc.data[0, 2, 0] == -1
    assert mrc.data[0, 3, 0] == 127


def test_is_s3_throttling() -> None:
    """Test that is_s3_throttling correctly identifies throttling errors."""
    # Test positive cases - should return True for throttling errors
    assert is_s3_throttling(Exception("SlowDown"))
    assert is_s3_throttling(Exception("SlowDown: Please reduce your request rate"))
    assert is_s3_throttling(Exception("503 Service Unavailable"))
    assert is_s3_throttling(Exception("Service Unavailable"))
    assert is_s3_throttling(Exception("Throttling exception"))
    assert is_s3_throttling(Exception("Request was throttled"))
    # Test case-insensitivity
    assert is_s3_throttling(Exception("SLOWDOWN"))
    assert is_s3_throttling(Exception("service UNAVAILABLE"))
    # Test OSError with Service Unavailable (as seen in production)
    assert is_s3_throttling(OSError("[Errno 16] Service Unavailable"))

    # Test negative cases - should return False for non-throttling errors
    assert not is_s3_throttling(Exception("File not found"))
    assert not is_s3_throttling(ValueError("Invalid data"))
    assert not is_s3_throttling(Exception("Access denied"))
    assert not is_s3_throttling(Exception("404 Not Found"))
    assert not is_s3_throttling(Exception("Connection reset"))


@pytest.fixture
def fast_retries():
    """Retry write_region without waiting, at most TEST_RETRY_MAX_ATTEMPTS times."""
    original_wait, original_stop = write_region.retry.wait, write_region.retry.stop
    write_region.retry.wait = wait_none()
    write_region.retry.stop = stop_after_attempt(TEST_RETRY_MAX_ATTEMPTS)
    yield
    write_region.retry.wait, write_region.retry.stop = original_wait, original_stop


TEST_PYRAMID = [np.ones((4, 4, 4), dtype=np.int8), np.ones((2, 2, 2), dtype=np.int8)]
TEST_SPACING = [(14.08, 14.08, 14.08), (28.16, 28.16, 28.16)]
PYRAMID_WRITERS = pytest.mark.parametrize("writer", [write_v2_pyramid, write_label_pyramid], ids=["zarr_v2", "zarr_v3"])


@PYRAMID_WRITERS
def test_write_region_retries_on_s3_slowdown(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    fast_retries,
    writer,
) -> None:
    """Writes retry on S3 SlowDown errors and eventually succeed."""
    call_count = 0
    max_failures = 2
    original_setitem = zarr.Array.__setitem__

    def flaky_setitem(self, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= max_failures:
            raise Exception("SlowDown: Please reduce your request rate")
        return original_setitem(self, *args, **kwargs)

    output_path = f"{test_output_bucket}/test_retry_output.zarr"
    with patch.object(zarr.Array, "__setitem__", flaky_setitem):
        writer(s3_fs, TEST_PYRAMID, output_path, TEST_SPACING)

    # 2 failures + 1 success for the first level, 1 call for the second
    assert call_count == 4, f"Expected 4 calls (2 failures + 2 successes), got {call_count}"
    np.testing.assert_array_equal(open_output(s3_fs, output_path)["0"][:], TEST_PYRAMID[0])


@PYRAMID_WRITERS
def test_write_region_raises_after_max_retries(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    fast_retries,
    writer,
) -> None:
    def always_fails(self, *args, **kwargs):
        raise Exception("SlowDown: Please reduce your request rate")

    output_path = f"{test_output_bucket}/test_retry_fail_output.zarr"
    with patch.object(zarr.Array, "__setitem__", always_fails), pytest.raises(Exception, match="SlowDown"):
        writer(s3_fs, TEST_PYRAMID, output_path, TEST_SPACING)


@PYRAMID_WRITERS
def test_write_region_does_not_retry_non_throttling_errors(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    fast_retries,
    writer,
) -> None:
    call_count = 0

    def non_throttle_error(self, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise ValueError("Some other error that should not be retried")

    output_path = f"{test_output_bucket}/test_no_retry_output.zarr"
    with patch.object(zarr.Array, "__setitem__", non_throttle_error), pytest.raises(ValueError, match="Some other"):
        writer(s3_fs, TEST_PYRAMID, output_path, TEST_SPACING)
    assert call_count == 1, f"Expected 1 call (no retry for non-throttling error), got {call_count}"
