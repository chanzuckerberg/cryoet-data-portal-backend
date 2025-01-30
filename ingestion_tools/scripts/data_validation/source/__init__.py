import os
import sys

import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# For better assertion errors in the helper functions
pytest.register_assert_rewrite(
    "data_validation.shared.helper.angles_helper",
    "data_validation.shared.helper.helper_mrc",
    "data_validation.shared.helper.helper_mrc_zarr",
    "data_validation.shared.helper.helper_tiff_mrc",
    "data_validation.shared.helper.helper_zarr",
    "data_validation.shared.helper.mdoc_helper",
    "data_validation.shared.helper.tilt_angles_helper",
    "data_validation.shared.helper.tiltseries_helper",
    "data_validation.shared.helper.twodee_helper",
)
