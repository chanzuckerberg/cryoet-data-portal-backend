import concurrent.futures
import os.path
from typing import List, Tuple

import allure
import pytest

# Local fixtures and common functions
from fixtures.data import *  # noqa: E402, F403
from fixtures.parser import *  # noqa: E402, F403
from fixtures.path import *  # noqa: E402, F403

from common.fs import FileSystemApi, S3Filesystem  # noqa: E402, F403

# ============================================================================
# Pytest parametrized fixtures
# ============================================================================


def get_run_folders(fs: S3Filesystem, bucket: str, datasets: List[str], run_glob: str) -> List[str]:
    """
    A helper function to retrieve all valid run folders across all datasets.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        run_folder_template = f"s3://{bucket}/{{}}/{run_glob}"

        run_folders_lists = executor.map(
            lambda dataset: fs.glob(run_folder_template.format(dataset)),
            datasets,
        )
        # Flatten the list of lists
        run_folders = [run_folder for run_folders_list in run_folders_lists for run_folder in run_folders_list]

        exclude = ["Images", "dataset_metadata.json"]
        run_folders = [run_folder for run_folder in run_folders if os.path.basename(run_folder) not in exclude]

        return run_folders


def get_runs_set(run_folders: List[str]) -> List[str]:
    """All runs that occur over all datasets."""
    return [os.path.basename(run_folder) for run_folder in run_folders]


def dataset_run_combinations(
    bucket: str,
    datasets: List[str],
    runs: List[str],
    run_folders: List[str],
) -> List[Tuple[str, str]]:
    """All valid dataset and run combinations matching the run glob pattern across all datasets."""
    combos = []

    for dataset in datasets:
        for run in runs:
            if f"{bucket}/{dataset}/{run}" in run_folders:
                combos.append((dataset, run))

    return combos


def get_voxel_spacing_files(
    fs: S3Filesystem,
    bucket: str,
    dataset_run_combinations: List[Tuple[str, str]],
    voxel_spacing_glob: str,
) -> List[str]:
    """
    A helper function to retrieve all valid voxel spacing files across all dataset + runs.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        voxel_spacing_file_template = f"s3://{bucket}/{{}}/{{}}/Tomograms/{voxel_spacing_glob}"

        voxel_spacing_files_lists = executor.map(
            lambda dataset_run_tuple: fs.glob(
                voxel_spacing_file_template.format(dataset_run_tuple[0], dataset_run_tuple[1]),
            ),
            dataset_run_combinations,
        )
        voxel_spacing_files = [
            voxel_spacing_file
            for voxel_spacing_file_list in voxel_spacing_files_lists
            for voxel_spacing_file in voxel_spacing_file_list
        ]

        return voxel_spacing_files


def get_voxel_spacings_set(voxel_spacing_files: List[str]) -> List[str]:
    """
    All voxel spacings that occur over all datasets and runs.
    """

    # Get only the voxel spacing value, remove the "VoxelSpacing" folder prefix
    voxel_spacings = [
        os.path.basename(voxel_spacing_file).lstrip("VoxelSpacing") for voxel_spacing_file in voxel_spacing_files
    ]
    return list(set(voxel_spacings))


def dataset_run_spacing_combinations(
    bucket: str,
    dataset_run_combinations: List[Tuple[str, str]],
    voxel_spacings: List[float],
    voxel_spacing_files: List[str],
) -> List[Tuple[str, str, float]]:
    """
    All valid dataset, run, and voxel spacing combinations. Returns a list of combinations in the form of
    (dataset, run_name, voxel_spacing).
    """
    combos = []

    for dataset_run_tuple in dataset_run_combinations:
        for vs in voxel_spacings:
            if (
                f"{bucket}/{dataset_run_tuple[0]}/{dataset_run_tuple[1]}/Tomograms/VoxelSpacing{vs}"
                in voxel_spacing_files
            ):
                combos.append(dataset_run_tuple + (vs,))
    return combos


# ============================================================================


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """
    This hook sets up the necessary parameters for the tests by:
    - Retrieving datasets and run folders from the S3 bucket.
    - Generating dataset and run combinations.
    - Fetching voxel spacing files and generating dataset-run-spacing combinations.
    - Registering test markers to categorize tests based on different aspects such as dataset, runs, and voxel spacings.
    """
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)

    # Using pytest_generate_tests to parametrize the fixtures causes the per-run-fixtures to be run multiple times,
    # but setting the parameterizations as labels and parametrizing the class with that label leads to desired outcome, i.e.
    # re-use of the per-run fixtures.
    if not config.getoption("--datasets"):
        dataset_raw = [os.path.basename(dataset) for dataset in fs.glob(f"s3://{config.getoption('--bucket')}/*")]
        pytest.dataset = [dataset for dataset in dataset_raw if dataset.isdigit()]
    else:
        pytest.dataset = [dataset for dataset in config.getoption("--datasets").split(",") if dataset.isdigit()]
    bucket = config.getoption("--bucket")
    run_glob = config.getoption("--run-glob")
    voxel_spacing_glob = config.getoption("--voxel-spacing-glob")
    print("Datasets: %s", pytest.dataset)

    run_folders = get_run_folders(fs, bucket, pytest.dataset, run_glob)
    pytest.run_name = get_runs_set(run_folders)
    pytest.dataset_run_combinations = dataset_run_combinations(bucket, pytest.dataset, pytest.run_name, run_folders)
    print("Dataset and run combinations: %s", pytest.dataset_run_combinations)

    voxel_spacing_files = get_voxel_spacing_files(fs, bucket, pytest.dataset_run_combinations, voxel_spacing_glob)
    pytest.voxel_spacing = get_voxel_spacings_set(voxel_spacing_files)
    pytest.dataset_run_spacing_combinations = dataset_run_spacing_combinations(
        bucket,
        pytest.dataset_run_combinations,
        pytest.voxel_spacing,
        voxel_spacing_files,
    )

    print("Dataset, run, and voxel spacing combinations: %s", pytest.dataset_run_spacing_combinations)

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
    """
    This hook integrates allure to dynamically annotate the test reports with
    details such as the dataset, run, and voxel spacing being tested.
    """
    if "voxel_spacing" in item.fixturenames:
        allure.dynamic.story(f"VoxelSpacing {item.callspec.params['voxel_spacing']}")
    if "run_name" in item.fixturenames:
        allure.dynamic.feature(f"Run {item.callspec.params['run_name']}")
    if "dataset" in item.fixturenames:
        allure.dynamic.epic(f"Dataset {pytest.dataset}")
    yield
