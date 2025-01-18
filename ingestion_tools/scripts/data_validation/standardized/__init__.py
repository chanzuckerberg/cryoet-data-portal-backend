import os
import sys

import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)
sys.path.append(os.path.join(CURRENT_DIR, ".."))

# For better assertion errors in the helper functions
pytest.register_assert_rewrite(
    "data_validation.standardized.tests.annotation.helper_point",
    "data_validation.standardized.tests.helper_images",
    "data_validation.standardized.tests.helper_metadata",
    "data_validation.standardized.tests.helper_mrc_zarr",
    "data_validation.standardized.tests.helper_mrc",
    "data_validation.standardized.tests.helper_zarr",
)
