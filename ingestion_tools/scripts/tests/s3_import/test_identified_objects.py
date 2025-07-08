import json
from mypy_boto3_s3 import S3Client
import pytest
from importers.identified_object import IdentifiedObjectImporter
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_children, get_run_and_parents


@pytest.mark.parametrize(
    "allow_imports,expected_files",
    [
        (True, ["identified_objects.json", "identified_objects_metadata.json"]),
        (False, []),
    ],
    ids=["import_enabled", "import_disabled"],
)
def test_identified_object_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    allow_imports: bool,
    expected_files: list[str],
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)

    identified_objects = list(IdentifiedObjectImporter.finder(config, **parents))
    for identified_object in identified_objects:
        identified_object.allow_imports = allow_imports
        identified_object.import_item()
        identified_object.import_metadata()

    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/IdentifiedObjects"
    files = get_children(s3_client, test_output_bucket, prefix)

    for expected_file in expected_files:
        assert expected_file in files
    

@pytest.mark.parametrize(
    "file_type,expected_structure",
    [
        ("json", {"min_length": 1}),
        ("metadata", {"required_keys": ["object_count", "file_format", "columns", "identifier"]}),
    ],
    ids=["validate_json_data", "validate_metadata"],
)
def test_identified_object_files(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    file_type: str,
    expected_structure: dict,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)

    identified_objects = list(IdentifiedObjectImporter.finder(config, **parents))
    for identified_object in identified_objects:
        identified_object.import_item()
        identified_object.import_metadata()

    base_path = f"{test_output_bucket}/output/{parents['dataset'].name}/{parents['run'].name}/IdentifiedObjects"

    file_mapping = {
        "json": "identified_objects.json",
        "metadata": "identified_objects_metadata.json",
    }
    
    file_path = f"{base_path}/{file_mapping[file_type]}"

    with s3_fs.open(file_path, "r") as f:
        data = json.load(f)

        if file_type == "json":
            assert isinstance(data, list)
            assert len(data) >= expected_structure["min_length"]
        elif file_type == "metadata":
            for key in expected_structure["required_keys"]:
                assert key in data
            assert data["file_format"] == "csv"
            assert isinstance(data["columns"], list)
            assert data["object_count"] > 0
