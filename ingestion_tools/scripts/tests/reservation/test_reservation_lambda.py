"""Tests for the reservation Lambda function.

Uses the moto-backed s3_client from conftest. Only the GitHub API is mocked.
"""

import json
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from mypy_boto3_s3 import S3Client

# Mutilating path here as the lambda function code isn't actually part of this library.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "reservation"))
import lambda_function as lf

FAKE_GIT_RESPONSE = json.dumps([
    {"name": "10001.yaml"},
    {"name": "10002.yaml"},
    {"name": "10003_draft.yaml"},
    {"name": "deposition_10001.yaml"},
    {"name": "deposition_10002.yaml"},
    {"name": "template.yaml"},
    {"name": "gjensen"},
    {"name": "run_data_map"},
]).encode()

EXISTING_RESERVATIONS = {
    "datasets": {
        "10001": {"instantiated": True, "reserved_at": "2026-01-01T00:00:00"},
        "10004": {"instantiated": False, "reserved_at": "2026-02-01T00:00:00"},
    },
    "depositions": {
        "10001": {"instantiated": True, "reserved_at": "2026-01-01T00:00:00"},
        "10003": {"instantiated": False, "reserved_at": "2026-02-01T00:00:00"},
    },
    "next_dataset_id": 10005,
    "next_deposition_id": 10004,
}


def make_event(method, path, query=None):
    return {
        "rawPath": path,
        "requestContext": {"http": {"method": method}},
        "queryStringParameters": query,
    }


def parse(resp):
    return resp["statusCode"], json.loads(resp["body"])


def mock_github():
    resp = MagicMock()
    resp.read.return_value = FAKE_GIT_RESPONSE
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    return resp


@pytest.fixture
def reservation_bucket(s3_client: S3Client, region_name: str) -> str:
    """Create the S3 bucket the Lambda uses."""
    bucket = lf.S3_BUCKET
    try:
        s3_client.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": region_name},
        )
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass
    return bucket


@pytest.fixture(autouse=True)
def reservation_env(s3_client: S3Client, reservation_bucket: str):
    """Point the Lambda at the moto S3 client, clear cache and S3 state, mock GitHub."""
    lf.s3 = s3_client
    lf._cache["data"] = None
    lf._cache["timestamp"] = 0
    try:
        s3_client.delete_object(Bucket=reservation_bucket, Key=lf.S3_KEY)
    except Exception:
        pass
    with patch("lambda_function.urllib.request.urlopen", return_value=mock_github()):
        yield


@pytest.fixture
def seed_reservations(s3_client: S3Client, reservation_bucket: str) -> None:
    """Seed EXISTING_RESERVATIONS into S3."""
    s3_client.put_object(
        Bucket=reservation_bucket,
        Key=lf.S3_KEY,
        Body=json.dumps(EXISTING_RESERVATIONS),
    )


# --- Sync ---

def test_sync_from_empty_s3(reservation_bucket):
    status, body = parse(lf.handler(make_event("GET", "/reservations", {"detail": "true"}), None))

    assert status == 200
    assert body["next_dataset_id"] == 10004
    assert body["next_deposition_id"] == 10003
    assert set(body["datasets"].keys()) == {"10001", "10002", "10003"}
    assert all(v["instantiated"] for v in body["datasets"].values())


def test_sync_merges_git_into_existing(seed_reservations):
    status, body = parse(lf.handler(make_event("GET", "/reservations", {"detail": "true"}), None))

    assert status == 200
    assert set(body["datasets"].keys()) == {"10001", "10002", "10003", "10004"}
    assert set(body["depositions"].keys()) == {"10001", "10002", "10003"}


def test_sync_marks_reserved_as_instantiated(s3_client, reservation_bucket):
    data = {
        "datasets": {"10001": {"instantiated": False, "reserved_at": "2026-01-01T00:00:00"}},
        "depositions": {},
        "next_dataset_id": 10002,
        "next_deposition_id": 10000,
    }
    s3_client.put_object(Bucket=reservation_bucket, Key=lf.S3_KEY, Body=json.dumps(data))

    _, body = parse(lf.handler(make_event("GET", "/reservations", {"detail": "true"}), None))
    assert body["datasets"]["10001"]["instantiated"] is True


def test_no_s3_write_when_already_synced(s3_client, reservation_bucket):
    already_synced = {
        "datasets": {
            "10001": {"instantiated": True, "reserved_at": "2026-01-01T00:00:00"},
            "10002": {"instantiated": True, "reserved_at": "2026-01-01T00:00:00"},
            "10003": {"instantiated": True, "reserved_at": "2026-01-01T00:00:00"},
        },
        "depositions": {
            "10001": {"instantiated": True, "reserved_at": "2026-01-01T00:00:00"},
            "10002": {"instantiated": True, "reserved_at": "2026-01-01T00:00:00"},
        },
        "next_dataset_id": 10004,
        "next_deposition_id": 10003,
    }
    s3_client.put_object(Bucket=reservation_bucket, Key=lf.S3_KEY, Body=json.dumps(already_synced))

    lf.handler(make_event("GET", "/reservations"), None)

    # Verify reservations.json wasn't rewritten (still matches what we seeded)
    obj = s3_client.get_object(Bucket=reservation_bucket, Key=lf.S3_KEY)
    stored = json.loads(obj["Body"].read())
    assert stored == already_synced


def test_git_non_yaml_files_ignored(reservation_bucket):
    _, body = parse(lf.handler(make_event("GET", "/reservations", {"detail": "true"}), None))

    assert set(body["datasets"].keys()) == {"10001", "10002", "10003"}
    assert set(body["depositions"].keys()) == {"10001", "10002"}


# --- GET endpoints ---

def test_summary(seed_reservations):
    status, body = parse(lf.handler(make_event("GET", "/reservations"), None))

    assert status == 200
    assert "datasets" not in body
    assert "next_dataset_id" in body
    assert "dataset_count" in body


def test_detail(seed_reservations):
    status, body = parse(lf.handler(make_event("GET", "/reservations", {"detail": "true"}), None))

    assert status == 200
    assert isinstance(body["datasets"], dict)


def test_dataset_instantiated(seed_reservations):
    _, body = parse(lf.handler(make_event("GET", "/reservations/dataset/10001"), None))

    assert body["dataset_id"] == 10001
    assert body["instantiated"] is True


def test_dataset_not_found(seed_reservations):
    _, body = parse(lf.handler(make_event("GET", "/reservations/dataset/99999"), None))
    assert body["instantiated"] is False
    assert body["reservation"] is None


def test_dataset_invalid_id(seed_reservations):
    status, _ = parse(lf.handler(make_event("GET", "/reservations/dataset/abc"), None))
    assert status == 400


def test_deposition_instantiated(seed_reservations):
    _, body = parse(lf.handler(make_event("GET", "/reservations/deposition/10001"), None))
    assert body["instantiated"] is True


def test_deposition_not_found(seed_reservations):
    _, body = parse(lf.handler(make_event("GET", "/reservations/deposition/99999"), None))
    assert body["instantiated"] is False


def test_deposition_invalid_id(seed_reservations):
    status, _ = parse(lf.handler(make_event("GET", "/reservations/deposition/abc"), None))
    assert status == 400


def test_unknown_route_404(seed_reservations):
    status, _ = parse(lf.handler(make_event("GET", "/nonexistent"), None))
    assert status == 404


# --- New reservations ---

def test_new_dataset(seed_reservations):
    _, body = parse(lf.handler(make_event("GET", "/reservations/dataset/new"), None))
    assert body["dataset_id"] == 10005


def test_new_deposition(seed_reservations):
    _, body = parse(lf.handler(make_event("GET", "/reservations/deposition/new"), None))
    assert body["deposition_id"] == 10004


def test_dataset_sequential(seed_reservations):
    _, body1 = parse(lf.handler(make_event("GET", "/reservations/dataset/new"), None))
    _, body2 = parse(lf.handler(make_event("GET", "/reservations/dataset/new"), None))
    assert body2["dataset_id"] == body1["dataset_id"] + 1


def test_deposition_sequential(seed_reservations):
    _, body1 = parse(lf.handler(make_event("GET", "/reservations/deposition/new"), None))
    _, body2 = parse(lf.handler(make_event("GET", "/reservations/deposition/new"), None))
    assert body2["deposition_id"] == body1["deposition_id"] + 1


# --- Cache ---

def test_cache_used_for_get(seed_reservations, s3_client, reservation_bucket):
    lf.handler(make_event("GET", "/reservations"), None)
    s3_client.delete_object(Bucket=reservation_bucket, Key=lf.S3_KEY)

    # Should still work from cache
    status, _ = parse(lf.handler(make_event("GET", "/reservations"), None))
    assert status == 200


def test_cache_expired_triggers_refresh(seed_reservations):
    lf.handler(make_event("GET", "/reservations"), None)
    lf._cache["timestamp"] = time.monotonic() - lf.CACHE_TTL_SECONDS - 1

    status, _ = parse(lf.handler(make_event("GET", "/reservations"), None))
    assert status == 200


def test_new_bypasses_cache(seed_reservations):
    lf.handler(make_event("GET", "/reservations"), None)
    lf._cache["timestamp"] = time.monotonic()

    _, body = parse(lf.handler(make_event("GET", "/reservations/dataset/new"), None))
    assert "dataset_id" in body
