from unittest.mock import patch

import mrcfile
import numpy as np
import pytest
import zarr
from ome_zarr.io import parse_url
from ome_zarr.reader import Reader as Reader
from tenacity import stop_after_attempt, wait_none

from common.fs import FileSystemApi
from common.image import (
    ZarrWriter,
    make_pyramids,
)
from common.retry import is_s3_throttling

# Test retry constants (shorter times for fast test execution)
TEST_RETRY_MAX_ATTEMPTS = 3


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


def test_convert_mrc_to_omezarr(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_mrc.mrc"
    make_pyramids(s3_fs, output_path, input_file)

    fsstore = zarr.storage.FSStore(url=f"{output_path}.zarr", mode="r", fs=s3_fs.s3fs)
    loc = parse_url(fsstore)
    attrs = loc.root_attrs
    assert attrs["multiscales"][0]["axes"][0] == {"name": "z", "unit": "angstrom", "type": "space"}

    assert len(attrs["multiscales"][0]["datasets"]) == 3
    spacing = 14.08
    for ds in attrs["multiscales"][0]["datasets"]:
        assert ds["coordinateTransformations"][0]["scale"] == [spacing, spacing, spacing]
        spacing *= 2

    reader = Reader(loc)
    nodes = list(reader())
    assert len(nodes[0].data) == 3
    img_dim = 4
    for node in nodes[0].data:
        assert node.shape == (img_dim, img_dim, img_dim)
        img_dim /= 2
    assert s3_fs.exists(f"{output_path}.zarr/0/0/0/0")


def test_convert_omezarr_to_omezarr(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_omezarr.zarr"
    make_pyramids(s3_fs, output_path, input_file)

    fsstore = zarr.storage.FSStore(url=f"{output_path}.zarr", mode="r", fs=s3_fs.s3fs)
    loc = parse_url(fsstore)
    attrs = loc.root_attrs
    assert attrs["multiscales"][0]["axes"][0] == {"name": "z", "unit": "angstrom", "type": "space"}

    assert len(attrs["multiscales"][0]["datasets"]) == 3
    spacing = 14.08
    for ds in attrs["multiscales"][0]["datasets"]:
        assert ds["coordinateTransformations"][0]["scale"] == [spacing, spacing, spacing]
        spacing *= 2

    reader = Reader(loc)
    nodes = list(reader())
    assert len(nodes[0].data) == 3
    img_dim = 4
    for node in nodes[0].data:
        assert node.shape == (img_dim, img_dim, img_dim)
        img_dim /= 2
    assert s3_fs.exists(f"{output_path}.zarr/0/0/0/0")


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


def test_write_data_retries_on_s3_slowdown(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    """Test that write_data retries on S3 SlowDown errors and eventually succeeds."""
    # Patch retry settings for fast test execution (no wait between retries)
    original_write_wait = ZarrWriter.write_data.retry.wait
    original_write_stop = ZarrWriter.write_data.retry.stop
    original_init_wait = ZarrWriter._init_zarr_store.retry.wait
    original_init_stop = ZarrWriter._init_zarr_store.retry.stop

    ZarrWriter.write_data.retry.wait = wait_none()
    ZarrWriter.write_data.retry.stop = stop_after_attempt(TEST_RETRY_MAX_ATTEMPTS)
    ZarrWriter._init_zarr_store.retry.wait = wait_none()
    ZarrWriter._init_zarr_store.retry.stop = stop_after_attempt(TEST_RETRY_MAX_ATTEMPTS)

    try:
        call_count = 0
        max_failures = 2

        # Store reference to the original method
        original_create_dataset = zarr.hierarchy.Group.create_dataset

        def mock_create_dataset(self, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= max_failures:
                raise Exception("SlowDown: Please reduce your request rate")
            return original_create_dataset(self, *args, **kwargs)

        # Create test data: small pyramid with 2 levels
        test_data = [
            np.ones((4, 4, 4), dtype=np.float32),
            np.ones((2, 2, 2), dtype=np.float32),
        ]
        test_voxel_spacing = [
            (14.08, 14.08, 14.08),
            (28.16, 28.16, 28.16),
        ]

        output_path = f"{test_output_bucket}/test_retry_output.zarr"

        with patch.object(zarr.hierarchy.Group, "create_dataset", mock_create_dataset):
            writer = ZarrWriter(s3_fs, output_path)
            writer.write_data(test_data, test_voxel_spacing)

        # Should have had 2 failures + 1 success for the first pyramid level
        # The second pyramid level adds more calls
        assert call_count >= 3, f"Expected at least 3 calls (2 failures + 1 success), got {call_count}"

        # Verify the write eventually succeeded by checking the output exists
        assert s3_fs.exists(f"{output_path}/0")
    finally:
        # Restore original retry settings
        ZarrWriter.write_data.retry.wait = original_write_wait
        ZarrWriter.write_data.retry.stop = original_write_stop
        ZarrWriter._init_zarr_store.retry.wait = original_init_wait
        ZarrWriter._init_zarr_store.retry.stop = original_init_stop


def test_write_data_raises_after_max_retries(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    """Test that write_data raises exception after max retries are exhausted."""
    # Patch retry settings for fast test execution (no wait between retries)
    original_write_wait = ZarrWriter.write_data.retry.wait
    original_write_stop = ZarrWriter.write_data.retry.stop
    original_init_wait = ZarrWriter._init_zarr_store.retry.wait
    original_init_stop = ZarrWriter._init_zarr_store.retry.stop

    ZarrWriter.write_data.retry.wait = wait_none()
    ZarrWriter.write_data.retry.stop = stop_after_attempt(TEST_RETRY_MAX_ATTEMPTS)
    ZarrWriter._init_zarr_store.retry.wait = wait_none()
    ZarrWriter._init_zarr_store.retry.stop = stop_after_attempt(TEST_RETRY_MAX_ATTEMPTS)

    try:

        def mock_create_dataset_always_fails(self, *args, **kwargs):
            raise Exception("SlowDown: Please reduce your request rate")

        test_data = [np.ones((4, 4, 4), dtype=np.float32)]
        test_voxel_spacing = [(14.08, 14.08, 14.08)]

        output_path = f"{test_output_bucket}/test_retry_fail_output.zarr"

        with patch.object(zarr.hierarchy.Group, "create_dataset", mock_create_dataset_always_fails):
            writer = ZarrWriter(s3_fs, output_path)
            with pytest.raises(Exception, match="SlowDown"):
                writer.write_data(test_data, test_voxel_spacing)
    finally:
        # Restore original retry settings
        ZarrWriter.write_data.retry.wait = original_write_wait
        ZarrWriter.write_data.retry.stop = original_write_stop
        ZarrWriter._init_zarr_store.retry.wait = original_init_wait
        ZarrWriter._init_zarr_store.retry.stop = original_init_stop


def test_write_data_does_not_retry_non_throttling_errors(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    """Test that write_data does not retry on non-throttling errors."""
    # Patch retry settings for fast test execution (no wait between retries)
    original_write_wait = ZarrWriter.write_data.retry.wait
    original_write_stop = ZarrWriter.write_data.retry.stop
    original_init_wait = ZarrWriter._init_zarr_store.retry.wait
    original_init_stop = ZarrWriter._init_zarr_store.retry.stop

    ZarrWriter.write_data.retry.wait = wait_none()
    ZarrWriter.write_data.retry.stop = stop_after_attempt(TEST_RETRY_MAX_ATTEMPTS)
    ZarrWriter._init_zarr_store.retry.wait = wait_none()
    ZarrWriter._init_zarr_store.retry.stop = stop_after_attempt(TEST_RETRY_MAX_ATTEMPTS)

    try:
        call_count = 0

        def mock_create_dataset_non_throttle_error(self, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ValueError("Some other error that should not be retried")

        test_data = [np.ones((4, 4, 4), dtype=np.float32)]
        test_voxel_spacing = [(14.08, 14.08, 14.08)]

        output_path = f"{test_output_bucket}/test_no_retry_output.zarr"

        with patch.object(zarr.hierarchy.Group, "create_dataset", mock_create_dataset_non_throttle_error):
            writer = ZarrWriter(s3_fs, output_path)
            with pytest.raises(ValueError, match="Some other error"):
                writer.write_data(test_data, test_voxel_spacing)

        # Should only have been called once - no retry for non-throttling errors
        assert call_count == 1, f"Expected 1 call (no retry for non-throttling error), got {call_count}"
    finally:
        # Restore original retry settings
        ZarrWriter.write_data.retry.wait = original_write_wait
        ZarrWriter.write_data.retry.stop = original_write_stop
        ZarrWriter._init_zarr_store.retry.wait = original_init_wait
        ZarrWriter._init_zarr_store.retry.stop = original_init_stop
