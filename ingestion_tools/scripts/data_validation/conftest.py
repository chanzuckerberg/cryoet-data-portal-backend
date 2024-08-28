import concurrent.futures
import os.path
import sys
from typing import List, Tuple

import pytest

# from allure_commons.model2 import Label
# from allure_commons.types import LabelType
# from allure_commons._core import plugin_manager
# from allure_pytest.utils import ALLURE_LABEL_MARK
# from pytest import MarkDecorator
# Local fixtures and common functions
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)
sys.path.append(os.path.join(CURRENT_DIR, ".."))
from fixtures.data import *  # noqa: E402, F403
from fixtures.parser import *  # noqa: E402, F403
from fixtures.path import *  # noqa: E402, F403

from common.fs import FileSystemApi, S3Filesystem  # noqa: E402, F403


# ============================================================================
# Pytest parameterized fixtures
# ============================================================================
def run_names(bucket: str, dataset: str, run_glob: str) -> List[str]:
    """All runs matching the run glob pattern in the dataset."""
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
    runs = fs.glob(f"s3://{bucket}/{dataset}/{run_glob}")

    exclude = ["Images", "dataset_metadata.json"]

    run_names = [os.path.basename(run) for run in runs if os.path.basename(run) not in exclude]

    return run_names


def get_voxel_spacing_files(bucket: str, dataset: str, run_names: List[str], voxelspacing_glob: str) -> List[str]:
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)

    tentatives = []

    # Use ThreadPoolExecutor to run glob_task in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the run_names to the glob_task function
        results = executor.map(
            lambda run_name: fs.glob(f"s3://{bucket}/{dataset}/{run_name}/Tomograms/{voxelspacing_glob}"),
            run_names,
        )

        # Combine results
        for result in results:
            tentatives += result

    exclude = ["Images", "dataset_metadata.json"]

    for ex in exclude:
        tentatives = [tent for tent in tentatives if ex not in tent]

    return tentatives


def voxel_spacings(voxel_spacing_files: List[str]) -> List[float]:
    """
    All voxel spacings matching the voxel spacing glob pattern in the dataset.
    Because voxel spacings are subfolders of the the runs, we also constrain the glob to be only for the provided runs.
    """

    voxel_spacings = [
        os.path.basename(voxel_spacing_file).lstrip("VoxelSpacing") for voxel_spacing_file in voxel_spacing_files
    ]
    return list(set(voxel_spacings))


def run_spacing_combinations(
    bucket: str,
    dataset: str,
    run_names: List[str],
    voxel_spacings: List[float],
    voxel_spacing_files: List[str],
) -> List[Tuple[str, float]]:
    """Not all runs have all voxelspacings. Go through each run and find all the spacings present."""
    combos = []

    for run in run_names:
        for vs in voxel_spacings:
            if f"{bucket}/{dataset}/{run}/Tomograms/VoxelSpacing{vs}" in voxel_spacing_files:
                combos.append((run, float(vs)))

    return combos


# ============================================================================


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    # Dataset label for report title
    pytest.dataset = config.getoption("--dataset")

    # Using pytest_generate_tests to parametrize the run_name fixture causes the per-run-fixtures to be run multiple times,
    # but setting the runnames as a label and parametrizing the class with that label leads to desired outcome, i.e.
    # re-use of the per-run fixtures.
    bucket = config.getoption("--bucket")
    dataset = config.getoption("--dataset")
    run_glob = config.getoption("--run_glob")
    pytest.run_name = run_names(bucket, dataset, run_glob)

    voxelspacing_glob = config.getoption("--voxelspacing_glob")
    voxel_spacing_files = get_voxel_spacing_files(bucket, dataset, pytest.run_name, voxelspacing_glob)
    pytest.voxel_spacing = voxel_spacings(voxel_spacing_files)

    pytest.run_spacing_combinations = run_spacing_combinations(
        bucket,
        dataset,
        pytest.run_name,
        pytest.voxel_spacing,
        voxel_spacing_files,
    )
    print("Run and VoxelSpacing combinations: %s", pytest.run_spacing_combinations)

    # Register markers
    config.addinivalue_line("markers", "annotation: Tests concerning the annotation data.")
    config.addinivalue_line("markers", "dataset: Tests concerning the dataset.")
    config.addinivalue_line("markers", "deposition: Tests concerning the deposition data.")
    config.addinivalue_line("markers", "frame: Tests concerning the frames.")
    config.addinivalue_line("markers", "gain: Tests concerning the gain files.")
    config.addinivalue_line("markers", "run: Tests concerning the runs.")
    config.addinivalue_line("markers", "tiltseries: Tests concerning the tiltseries.")
    config.addinivalue_line("markers", "tomogram: Tests concerning the tomogram.")
    config.addinivalue_line("markers", "voxelspacing: Tests concerning the voxelspacing.")
    config.addinivalue_line("markers", "metadata: Tests concerning any metadata.")


# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     # pytest.set_trace()
#     # yield
#     has_epic = False
#     has_feature = False
#     has_story = False

#     paramnames = []
#     params = {}

#     epic = None
#     feature = None
#     story = None

#     for m in item.iter_markers():
#         if m.name == ALLURE_LABEL_MARK:
#             if m.kwargs.get("label_type") == LabelType.EPIC:
#                 has_epic = True
#                 epic = m
#             if m.kwargs.get("label_type") == LabelType.FEATURE:
#                 has_feature = True
#                 feature = m
#             if m.kwargs.get("label_type") == LabelType.STORY:
#                 has_story = True
#                 story = m

#         # if m.name == "parametrize":
#         #     paramnames = m.args[0].strip().split(",")
#         #     ptup = m.args[1][0]
#         #
#         #     if len(paramnames) == 1:
#         #         params[paramnames[0].strip()] = ptup
#         #     else:
#         #         params = {pn.strip(): p for pn, p in zip(paramnames, ptup)}

#     if "dataset" in item.fixturenames:
#         dataset = pytest.dataset
#         epic_name = f"Dataset {dataset}"
#         mark = getattr(pytest.mark, ALLURE_LABEL_MARK)(epic_name, label_type=LabelType.EPIC)
#         item.add_marker(mark)

#     if "run_name" in item.fixturenames:
#         run_name = item.callspec.params["run_name"]
#         feature_name = f"Run {run_name}"
#         mark = getattr(pytest.mark, ALLURE_LABEL_MARK)(feature_name, label_type=LabelType.FEATURE)
#         item.add_marker(mark)

#     if "voxel_spacing" in item.fixturenames:
#         voxelspacing = item.callspec.params["voxel_spacing"]
#         story_name = f"Voxel spacing {voxelspacing}"
#         mark = getattr(pytest.mark, ALLURE_LABEL_MARK)(story_name, label_type=LabelType.STORY)
#         item.add_marker(mark)

#     yield
