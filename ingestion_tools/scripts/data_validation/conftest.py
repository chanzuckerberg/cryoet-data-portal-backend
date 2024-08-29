import concurrent.futures
import os.path
import sys
from typing import List, Tuple

import allure
import pytest

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


def get_voxel_spacing_files(bucket: str, dataset: str, run_names: List[str], voxel_spacing_glob: str) -> List[str]:
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)

    tentatives = []

    # Use ThreadPoolExecutor to run glob_task in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the run_names to the glob_task function
        results = executor.map(
            lambda run_name: fs.glob(f"s3://{bucket}/{dataset}/{run_name}/Tomograms/{voxel_spacing_glob}"),
            run_names,
        )

        # Combine results
        for result in results:
            tentatives += result

    return tentatives


def voxel_spacings(voxel_spacing_files: List[str]) -> List[str]:
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
    """Not all runs have all voxel spacings. Go through each run and find all the spacings present."""
    combos = []

    for run in run_names:
        for vs in voxel_spacings:
            if f"{bucket}/{dataset}/{run}/Tomograms/VoxelSpacing{vs}" in voxel_spacing_files:
                combos.append((run, vs))

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

    voxel_spacing_glob = config.getoption("--voxel_spacing_glob")
    voxel_spacing_files = get_voxel_spacing_files(bucket, dataset, pytest.run_name, voxel_spacing_glob)
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
    config.addinivalue_line(
        "markers",
        "tilt_angles: Tests concerning the tilt angle (spans multiple entities: .tlt, .rawtlt, .mdoc, tiltseries_metadata.json, frames).",
    )
    config.addinivalue_line("markers", "tomogram: Tests concerning the tomogram.")
    config.addinivalue_line("markers", "voxel_spacing: Tests concerning voxel spacings.")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item):
    if "voxel_spacing" in item.fixturenames:
        allure.dynamic.story(f"VoxelSpacing {item.callspec.params['voxel_spacing']}")
    if "run_name" in item.fixturenames:
        allure.dynamic.feature(f"Run {item.callspec.params['run_name']}")
    if "dataset" in item.fixturenames:
        allure.dynamic.epic(f"Dataset {pytest.dataset}")
    yield
