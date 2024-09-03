import pytest

# For better assertion errors in the helper functions
pytest.register_assert_rewrite("helper_mrc", "helper_images", "helper_metadata", "annotation.helper_point")
