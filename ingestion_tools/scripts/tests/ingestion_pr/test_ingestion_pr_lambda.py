"""Tests for the ingestion-PR lambda: validation, markers, handler, reservation match.

Loaded under a unique module name via importlib because the reservation lambda also
ships a top-level ``lambda_function``; a plain import would clash in ``sys.modules``.
"""

import importlib.util
import io
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[2] / "ingestion_pr" / "lambda_function.py"
_spec = importlib.util.spec_from_file_location("ingestion_pr_lambda_function", _MODULE_PATH)
lf = importlib.util.module_from_spec(_spec)
sys.modules["ingestion_pr_lambda_function"] = lf
_spec.loader.exec_module(lf)


class _FakeNoSuchKeyError(Exception):
    pass


class _FakeS3:
    """Minimal stand-in for the boto3 S3 client used by _check_reserved."""

    def __init__(self, objects, error=None):
        # objects: {(bucket, key): bytes}; a missing key raises NoSuchKey.
        # error: if set, get_object raises it (e.g. AccessDenied/throttling).
        self._objects = objects
        self._error = error
        self.exceptions = type("exc", (), {"NoSuchKey": _FakeNoSuchKeyError})

    def get_object(self, **kwargs):
        if self._error is not None:
            raise self._error
        try:
            body = self._objects[(kwargs["Bucket"], kwargs["Key"])]
        except KeyError:
            raise self.exceptions.NoSuchKey() from None
        return {"Body": io.BytesIO(body)}


def _reservations(dataset_ids=(), deposition_ids=()):
    return {
        "datasets": {str(d): {"instantiated": False, "reserved_at": "t"} for d in dataset_ids},
        "depositions": {str(d): {"instantiated": False, "reserved_at": "t"} for d in deposition_ids},
    }


# --- _match_reservation (pure) ------------------------------------------------


def test_match_both_reserved_returns_no_problems():
    reservations = _reservations(dataset_ids=[800], deposition_ids=[700])
    assert lf._match_reservation(reservations, 700, 800) == []


def test_match_instantiated_id_still_counts_as_reserved():
    reservations = _reservations(dataset_ids=[800], deposition_ids=[700])
    reservations["datasets"]["800"]["instantiated"] = True
    assert lf._match_reservation(reservations, 700, 800) == []


def test_match_missing_dataset_reported():
    reservations = _reservations(dataset_ids=[], deposition_ids=[700])
    problems = lf._match_reservation(reservations, 700, 800)
    assert problems == ["dataset 800 is not reserved"]


def test_match_missing_deposition_reported():
    reservations = _reservations(dataset_ids=[800], deposition_ids=[])
    problems = lf._match_reservation(reservations, 700, 800)
    assert problems == ["deposition 700 is not reserved"]


def test_match_both_missing_reports_both():
    problems = lf._match_reservation(_reservations(), 700, 800)
    assert problems == ["dataset 800 is not reserved", "deposition 700 is not reserved"]


def test_match_tolerates_absent_sections():
    # An empty/partial reservations.json must not blow up; everything is "missing".
    problems = lf._match_reservation({}, 700, 800)
    assert problems == ["dataset 800 is not reserved", "deposition 700 is not reserved"]


# --- _check_reserved (S3 + flag behavior) ------------------------------------


@pytest.fixture
def reservations_env(monkeypatch):
    monkeypatch.setattr(lf, "RESERVATIONS_BUCKET", "res-bucket")
    monkeypatch.setattr(lf, "RESERVATIONS_KEY", "SUBMISSION_METADATA/reservations.json")
    monkeypatch.setattr(lf, "ENFORCE_RESERVATIONS", False)
    key = (lf.RESERVATIONS_BUCKET, lf.RESERVATIONS_KEY)
    return key, monkeypatch


def _install_s3(monkeypatch, objects, error=None):
    monkeypatch.setattr(lf, "s3", _FakeS3(objects, error=error))


def test_check_skips_when_bucket_unset(monkeypatch):
    monkeypatch.setattr(lf, "RESERVATIONS_BUCKET", None)
    # Should return without touching S3 at all.
    lf._check_reserved(700, 800)


def test_check_skips_when_file_missing(reservations_env):
    _, monkeypatch = reservations_env
    _install_s3(monkeypatch, {})  # no reservations.json present
    lf._check_reserved(700, 800)  # no raise


def test_check_passes_when_reserved(reservations_env):
    key, monkeypatch = reservations_env
    _install_s3(monkeypatch, {key: json.dumps(_reservations([800], [700])).encode()})
    lf._check_reserved(700, 800)  # no raise


def test_check_warn_only_does_not_raise_on_mismatch(reservations_env):
    key, monkeypatch = reservations_env
    _install_s3(monkeypatch, {key: json.dumps(_reservations([], [])).encode()})
    lf._check_reserved(700, 800)  # warns, no raise


def test_check_raises_validation_when_enforced_and_mismatch(reservations_env):
    key, monkeypatch = reservations_env
    monkeypatch.setattr(lf, "ENFORCE_RESERVATIONS", True)
    _install_s3(monkeypatch, {key: json.dumps(_reservations([], [])).encode()})
    with pytest.raises(lf.ValidationError):
        lf._check_reserved(700, 800)


# A read/parse failure must never block the PR in warn-only mode (only enforce raises).


def test_check_warn_only_skips_on_bad_json(reservations_env):
    key, monkeypatch = reservations_env
    _install_s3(monkeypatch, {key: b"{not json"})
    lf._check_reserved(700, 800)  # no raise


def test_check_enforced_raises_config_error_on_bad_json(reservations_env):
    key, monkeypatch = reservations_env
    monkeypatch.setattr(lf, "ENFORCE_RESERVATIONS", True)
    _install_s3(monkeypatch, {key: b"{not json"})
    with pytest.raises(lf.ConfigError):
        lf._check_reserved(700, 800)


def test_check_warn_only_skips_when_not_an_object(reservations_env):
    key, monkeypatch = reservations_env
    _install_s3(monkeypatch, {key: b"[1, 2, 3]"})
    lf._check_reserved(700, 800)  # no raise


def test_check_warn_only_skips_on_access_denied(reservations_env):
    _, monkeypatch = reservations_env
    _install_s3(monkeypatch, {}, error=RuntimeError("AccessDenied"))
    lf._check_reserved(700, 800)  # infra hiccup must not block / dead-letter


def test_check_enforced_raises_config_error_on_access_denied(reservations_env):
    _, monkeypatch = reservations_env
    monkeypatch.setattr(lf, "ENFORCE_RESERVATIONS", True)
    _install_s3(monkeypatch, {}, error=RuntimeError("AccessDenied"))
    with pytest.raises(lf.ConfigError):
        lf._check_reserved(700, 800)


# --- _validate ---------------------------------------------------------------


def _valid_config(deposition_id=700, dataset_id=800, source_prefix="CZII/700/800"):
    return {
        "version": 1,
        "standardization_config": {"deposition_id": deposition_id, "source_prefix": source_prefix},
        "datasets": [{"metadata": {"dataset_identifier": dataset_id}}],
        "depositions": [{"metadata": {"deposition_identifier": deposition_id, "deposition_title": "T"}}],
        "runs": {},
        "voxel_spacings": {},
    }


PREFIX = "CZII/700/800"


def test_validate_happy_path_returns_ids():
    assert lf._validate(_valid_config(), PREFIX) == (700, 800)


def test_validate_accepts_relative_source_prefix():
    config = _valid_config(source_prefix="700/800")
    assert lf._validate(config, PREFIX) == (700, 800)


def test_validate_missing_section():
    config = _valid_config()
    del config["runs"]
    with pytest.raises(lf.ValidationError):
        lf._validate(config, PREFIX)


def test_validate_wrong_prefix_depth():
    with pytest.raises(lf.ValidationError):
        lf._validate(_valid_config(), "CZII/700")


def test_validate_wrong_top_prefix():
    with pytest.raises(lf.ValidationError):
        lf._validate(_valid_config(), "OTHER/700/800")


def test_validate_non_integer_ids():
    with pytest.raises(lf.ValidationError):
        lf._validate(_valid_config(), "CZII/abc/800")


def test_validate_standardization_not_a_mapping():
    config = _valid_config()
    config["standardization_config"] = "nope"
    with pytest.raises(lf.ValidationError):
        lf._validate(config, PREFIX)


def test_validate_deposition_id_mismatch():
    config = _valid_config()
    config["standardization_config"]["deposition_id"] = 999
    with pytest.raises(lf.ValidationError):
        lf._validate(config, PREFIX)


def test_validate_dataset_identifier_mismatch():
    config = _valid_config()
    config["datasets"][0]["metadata"]["dataset_identifier"] = 999
    with pytest.raises(lf.ValidationError):
        lf._validate(config, PREFIX)


def test_validate_source_prefix_mismatch():
    config = _valid_config(source_prefix="CZII/1/2")
    with pytest.raises(lf.ValidationError):
        lf._validate(config, PREFIX)


def test_validate_non_mapping_dataset_entry():
    config = _valid_config()
    config["datasets"] = ["not-a-mapping"]
    with pytest.raises(lf.ValidationError):
        lf._validate(config, PREFIX)


def test_validate_non_list_datasets_is_dropped_not_retried():
    # A scalar `datasets` would TypeError on iteration; must be a clean ValidationError.
    config = _valid_config()
    config["datasets"] = 5
    with pytest.raises(lf.ValidationError):
        lf._validate(config, PREFIX)


# --- _check_datamap_exists ---------------------------------------------------


def test_datamap_absent_skips(monkeypatch):
    config = _valid_config()  # no run_data_map_file
    s3 = MagicMock()
    monkeypatch.setattr(lf, "s3", s3)
    lf._check_datamap_exists(config, "bucket", PREFIX)
    s3.head_object.assert_not_called()


def test_datamap_present_passes(monkeypatch):
    config = _valid_config()
    config["standardization_config"]["run_data_map_file"] = "map.tsv"
    s3 = MagicMock()  # head_object returns a truthy MagicMock (exists)
    monkeypatch.setattr(lf, "s3", s3)
    lf._check_datamap_exists(config, "bucket", PREFIX)
    s3.head_object.assert_called_once_with(Bucket="bucket", Key=f"{PREFIX}/map.tsv")


def test_datamap_missing_is_validation_error(monkeypatch):
    config = _valid_config()
    config["standardization_config"]["run_data_map_file"] = "map.tsv"
    s3 = MagicMock()
    s3.head_object.side_effect = RuntimeError("404")
    monkeypatch.setattr(lf, "s3", s3)
    with pytest.raises(lf.ValidationError):
        lf._check_datamap_exists(config, "bucket", PREFIX)


# --- _load_config ------------------------------------------------------------


def test_load_config_non_utf8_is_validation_error(monkeypatch):
    # Non-UTF-8 bytes must drop (ValidationError), not raise UnicodeDecodeError -> DLQ.
    key = ("b", f"CZII/700/800/{lf.CONFIG_FILENAME}")
    _install_s3(monkeypatch, {key: b"\xff\xfe not utf-8"})
    with pytest.raises(lf.ValidationError):
        lf._load_config("b", "CZII/700/800")


# --- _s3_markers -------------------------------------------------------------


def _s3_message(key, event_name="ObjectCreated:Put", bucket="b"):
    return {"Records": [{"eventName": event_name, "s3": {"bucket": {"name": bucket}, "object": {"key": key}}}]}


def test_markers_yields_exact_marker():
    msg = _s3_message("CZII/700/800/ingest.ready")
    assert list(lf._s3_markers(msg)) == [("b", "CZII/700/800/ingest.ready")]


def test_markers_rejects_suffixed_name():
    msg = _s3_message("CZII/700/800/foo_ingest.ready")
    assert list(lf._s3_markers(msg)) == []


def test_markers_ignores_non_objectcreated():
    msg = _s3_message("CZII/700/800/ingest.ready", event_name="ObjectRemoved:Delete")
    assert list(lf._s3_markers(msg)) == []


def test_markers_url_decodes_key():
    # S3 percent-encodes special chars in the key; _s3_markers must decode them.
    msg = _s3_message("CZII/a%20b/800/ingest.ready")
    assert list(lf._s3_markers(msg)) == [("b", "CZII/a b/800/ingest.ready")]


# --- handler (drop vs. retry) ------------------------------------------------


def _sqs_event(key="CZII/700/800/ingest.ready", body=None):
    inner = body if body is not None else json.dumps(_s3_message(key))
    return {"Records": [{"body": inner}]}


def test_handler_drops_validation_error(monkeypatch):
    # A bad upload (ValidationError) is logged and the message succeeds — no retry.
    monkeypatch.setattr(lf, "_process", MagicMock(side_effect=lf.ValidationError("bad config")))
    assert lf.handler(_sqs_event(), None) == {"ok": True}


def test_handler_propagates_config_error(monkeypatch):
    # A misconfig (ConfigError) must propagate so SQS retries -> DLQ.
    monkeypatch.setattr(lf, "_process", MagicMock(side_effect=lf.ConfigError("no creds")))
    with pytest.raises(lf.ConfigError):
        lf.handler(_sqs_event(), None)


def test_handler_propagates_unexpected_error(monkeypatch):
    monkeypatch.setattr(lf, "_process", MagicMock(side_effect=RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        lf.handler(_sqs_event(), None)


def test_handler_success_calls_process(monkeypatch):
    process = MagicMock(return_value={"dry_run": True})
    monkeypatch.setattr(lf, "_process", process)
    assert lf.handler(_sqs_event(), None) == {"ok": True}
    process.assert_called_once_with("b", "CZII/700/800/ingest.ready")


def test_handler_skips_unparseable_body(monkeypatch):
    process = MagicMock()
    monkeypatch.setattr(lf, "_process", process)
    assert lf.handler(_sqs_event(body="{not json"), None) == {"ok": True}
    process.assert_not_called()


# --- GitHubIngestionPR.create (dedup paths, mocked session) ------------------


class _FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _FakeSession:
    def __init__(self, router):
        self._router = router
        self.calls = []
        self.headers = {}

    def request(self, method, url, **kwargs):
        self.calls.append((method, url))
        return self._router(method, url, kwargs)

    def close(self):
        pass


def _make_github(router):
    gh = object.__new__(lf.GitHubIngestionPR)
    gh.repository = "chanzuckerberg/cryoet-data-portal-backend"
    gh.base_branch = "main"
    gh.session = _FakeSession(router)
    return gh


def test_create_reuses_existing_pr():
    def router(method, url, kwargs):
        if method == "GET" and url.endswith("/pulls"):
            return _FakeResponse(200, [{"html_url": "http://existing-pr"}])
        raise AssertionError(f"unexpected call: {method} {url}")

    gh = _make_github(router)
    url = gh.create("branch", "800.yaml", "text", title="t", body="b")
    assert url == "http://existing-pr"
    # No PUT/POST happened — the existing PR short-circuits everything.
    assert all(method == "GET" for method, _ in gh.session.calls)


def test_create_refuses_when_file_on_base():
    def router(method, url, kwargs):
        if method == "GET" and url.endswith("/pulls"):
            return _FakeResponse(200, [])  # no open PR
        if method == "GET" and "/contents/" in url:
            return _FakeResponse(200, {"sha": "abc", "content": "x"})  # file exists on main
        raise AssertionError(f"unexpected call: {method} {url}")

    gh = _make_github(router)
    with pytest.raises(lf.ValidationError):
        gh.create("branch", "800.yaml", "text", title="t", body="b")
