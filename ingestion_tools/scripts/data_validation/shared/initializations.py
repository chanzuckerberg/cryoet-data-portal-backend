import allure
import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item):
    """
    This hook integrates allure to dynamically annotate the test reports with
    details such as the dataset, run, and voxel spacing being tested.
    """
    if "voxel_spacing" in item.fixturenames:
        allure.dynamic.story(f"VoxelSpacing {item.callspec.params['voxel_spacing']}")
    if "run_name" in item.fixturenames:
        allure.dynamic.feature(f"Run {item.callspec.params['run_name']}")
    if "dataset" in item.fixturenames:
        allure.dynamic.epic(f"Dataset {pytest.cryoet.dataset}")
    yield
