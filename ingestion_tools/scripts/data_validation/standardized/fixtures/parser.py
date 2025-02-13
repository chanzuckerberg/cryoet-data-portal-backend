from pytest import Parser, fixture


def pytest_addoption(parser: Parser) -> None:
    """Common options for all tests."""

    # S3 or local
    parser.addoption(
        "--bucket",
        action="store",
        default="cryoet-data-portal-staging",
    )

    # Dataset ID
    parser.addoption(
        "--datasets",
        action="store",
    )

    # Run Name
    parser.addoption(
        "--run-glob",
        action="store",
        default="*",
    )

    # Voxelspacing
    parser.addoption(
        "--voxel-spacing-glob",
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
    return request.config.getoption("--voxel-spacing-glob")


@fixture(scope="session")
def run_glob(request):
    return request.config.getoption("--run-glob")
