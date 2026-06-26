from common.fs import FileSystemApi


def _keys(s3_client, bucket: str) -> set[str]:
    resp = s3_client.list_objects_v2(Bucket=bucket)
    return {o["Key"] for o in resp.get("Contents", [])}


def test_rm_s3_recursive_deletes_only_the_prefix(s3_fs: FileSystemApi, s3_client, test_output_bucket: str) -> None:
    keys = [
        "ds/Annotations/123/a.zarr/.zgroup",
        "ds/Annotations/123/a.zarr/0/0/0",
        "ds/Annotations/123/foo[1].mrc",  # glob metachars must be deleted as a literal
        "ds/Annotations/124/keep.json",  # sibling -- must survive
        "ds/Annotations/1234/keep.json",  # prefix-overlap -- must survive (trailing-slash guard)
    ]
    for k in keys:
        s3_client.put_object(Bucket=test_output_bucket, Key=k, Body=b"x")

    s3_fs.rm(f"{test_output_bucket}/ds/Annotations/123", recursive=True)

    assert _keys(s3_client, test_output_bucket) == {
        "ds/Annotations/124/keep.json",
        "ds/Annotations/1234/keep.json",
    }


def test_rm_s3_single_object(s3_fs: FileSystemApi, s3_client, test_output_bucket: str) -> None:
    s3_client.put_object(Bucket=test_output_bucket, Key="ds/x.json", Body=b"x")
    s3_client.put_object(Bucket=test_output_bucket, Key="ds/y.json", Body=b"y")

    s3_fs.rm(f"{test_output_bucket}/ds/x.json")

    assert _keys(s3_client, test_output_bucket) == {"ds/y.json"}


def test_rm_local_recursive(local_fs: FileSystemApi, tmp_path) -> None:
    folder = tmp_path / "123"
    (folder / "a.zarr" / "0").mkdir(parents=True)
    (folder / "a.zarr" / ".zgroup").write_text("{}")
    (folder / "a.zarr" / "0" / "0").write_text("x")
    sibling = tmp_path / "124"
    sibling.mkdir()
    (sibling / "keep.json").write_text("{}")

    local_fs.rm(str(folder), recursive=True)

    assert not folder.exists()
    assert (sibling / "keep.json").exists()


def test_rm_local_single_file(local_fs: FileSystemApi, tmp_path) -> None:
    f = tmp_path / "x.json"
    f.write_text("{}")

    local_fs.rm(str(f))

    assert not f.exists()
