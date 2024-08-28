from pytest import Parser, fixture


def pytest_addoption(parser: Parser) -> None:
    """Common options for all tests."""

    # Logging level
    parser.addoption(
        "--verbose-logs",
        action="store_true",
        default=False,
    )

    # Report destination
    parser.addoption(
        "--report_dst",
        action="store",
        default=".",
    )

    # S3 or local
    parser.addoption(
        "--bucket",
        action="store",
        default="cryoet-data-portal-staging",
    )

    # Dataset ID
    parser.addoption(
        "--dataset",
        action="store",
        required=True,
    )

    # Run Name and ID
    parser.addoption(
        "--run_glob",
        action="store",
        default="*",
    )

    # Voxelspacing
    parser.addoption(
        "--voxel_spacing_glob",
        action="store",
        default="*",
    )


@fixture(scope="session")
def bucket(request):
    return request.config.getoption("--bucket")


@fixture(scope="session")
def dataset(request):
    return request.config.getoption("--dataset")


@fixture(scope="session")
def voxel_spacing_glob(request):
    return request.config.getoption("--voxel_spacing_glob")


@fixture(scope="session")
def run_glob(request):
    return request.config.getoption("--run_glob")
