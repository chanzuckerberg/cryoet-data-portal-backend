import pytest

# For better assertion errors in the helper functions
pytest.register_assert_rewrite(
    "tests.annotation.helper_point",
    "tests.helper_images",
    "tests.helper_metadata",
    "tests.helper_mrc_zarr",
    "tests.helper_mrc",
    "tests.helper_zarr",
)
