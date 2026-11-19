"""Open a Data Portal ingestion PR when an upload drops an ``ingest.ready`` marker.

Triggered via S3 -> SQS; opens a PR adding the uploaded dataset config.
"""

import base64
import json
import logging
import os
import time
from pathlib import PurePosixPath
from urllib.parse import quote, unquote_plus

import boto3
import requests
import yaml
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

logger = logging.getLogger("ingestion_pr")
logger.setLevel(logging.INFO)

CONFIG_FILENAME = "portal_dataset_config.yaml"
MARKER_NAME = "ingest.ready"
CONFIG_DIRECTORY = "ingestion_tools/dataset_configs"
REQUIRED_SECTIONS = {"version", "standardization_config", "datasets", "depositions", "runs", "voxel_spacings"}

GITHUB_SECRET_ID = os.getenv("GITHUB_SECRET_ID")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "chanzuckerberg/cryoet-data-portal-backend")
GITHUB_BASE_BRANCH = "main"
UPLOAD_PREFIX = os.getenv("UPLOAD_PREFIX", "CZII")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() not in ("false", "0", "no")

RESERVATIONS_BUCKET = os.getenv("RESERVATIONS_BUCKET")
RESERVATIONS_KEY = "SUBMISSION_METADATA/reservations.json"
ENFORCE_RESERVATIONS = os.getenv("ENFORCE_RESERVATIONS", "false").lower() in ("true", "1", "yes")

s3 = boto3.client("s3")


class ValidationError(Exception):
    """The uploaded config is bad; drop the message (a retry won't help)."""


class ConfigError(Exception):
    """The Lambda or its credentials are misconfigured; propagate so SQS retries -> DLQ."""


def _load_config(bucket, prefix):
    key = f"{prefix}/{CONFIG_FILENAME}"
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    except s3.exceptions.NoSuchKey as error:
        raise ValidationError(f"No {CONFIG_FILENAME} at s3://{bucket}/{key}") from error
    try:
        content = body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValidationError(f"{CONFIG_FILENAME} is not valid UTF-8: {error}") from error
    try:
        config = yaml.safe_load(content)
    except yaml.YAMLError as error:
        raise ValidationError(f"{CONFIG_FILENAME} is not valid YAML: {error}") from error
    if not isinstance(config, dict):
        raise ValidationError(f"{CONFIG_FILENAME} is not a YAML mapping.")
    return content, config


def _validate(config, prefix):
    """Check required sections and that the IDs + source_prefix match the upload path."""
    if missing := REQUIRED_SECTIONS - config.keys():
        raise ValidationError(f"Config is missing sections: {', '.join(sorted(missing))}.")

    parts = PurePosixPath(prefix).parts
    if len(parts) != 3 or parts[0] != UPLOAD_PREFIX:
        raise ValidationError(f"Upload prefix is not {UPLOAD_PREFIX}/<deposition>/<dataset>: {prefix!r}")
    try:
        deposition_id, dataset_id = int(parts[1]), int(parts[2])
    except ValueError as error:
        raise ValidationError(f"deposition/dataset in the prefix are not integers: {prefix!r}") from error

    standardization = config.get("standardization_config")
    if not isinstance(standardization, dict):
        raise ValidationError("standardization_config must be a mapping.")
    if standardization.get("deposition_id") != deposition_id:
        raise ValidationError("Config deposition_id does not match the upload location.")

    datasets = config.get("datasets") or []
    if not isinstance(datasets, list):
        raise ValidationError("datasets must be a list.")
    if not all(isinstance(entry, dict) and isinstance(entry.get("metadata", {}), dict) for entry in datasets):
        raise ValidationError("datasets entries must be mappings with a metadata mapping.")
    identifiers = [entry.get("metadata", {}).get("dataset_identifier") for entry in datasets]
    if identifiers != [dataset_id]:
        raise ValidationError("Config dataset identifier does not match the upload location.")

    relative_prefix = f"{deposition_id}/{dataset_id}"
    if standardization.get("source_prefix") not in (prefix, relative_prefix):
        raise ValidationError("Config source_prefix does not match the S3 upload location.")

    depositions = config.get("depositions") or []
    if not isinstance(depositions, list):
        raise ValidationError("depositions must be a list.")
    for entry in depositions:
        if not isinstance(entry, dict) or not isinstance(entry.get("metadata", {}), dict):
            raise ValidationError("depositions entries must be mappings with a metadata mapping.")
        if entry.get("metadata", {}).get("deposition_identifier") != deposition_id:
            raise ValidationError("Config deposition identifier does not match the upload location.")

    return deposition_id, dataset_id


def _check_datamap_exists(config, bucket, prefix):
    """Confirm run_data_map_file (if set) is in S3 — Portal CI can't (no S3 access)."""
    datamap = (config.get("standardization_config") or {}).get("run_data_map_file")
    if not datamap:
        return
    try:
        s3.head_object(Bucket=bucket, Key=f"{prefix}/{datamap}")
    except ClientError as error:
        # Only a "not found" is a bad upload (drop). Throttling, 5xx, or a
        # permissions problem must propagate so SQS retries -> DLQ
        if error.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
            raise ValidationError(f"run_data_map_file not found in S3: {datamap}") from error
        raise


def _match_reservation(reservations, deposition_id, dataset_id):
    """Pure check: return problems for upload IDs missing from reservations.json."""
    problems = []
    datasets = reservations.get("datasets") or {}
    depositions = reservations.get("depositions") or {}
    if str(dataset_id) not in datasets:
        problems.append(f"dataset {dataset_id} is not reserved")
    if str(deposition_id) not in depositions:
        problems.append(f"deposition {deposition_id} is not reserved")
    return problems


def _check_reserved(deposition_id, dataset_id):
    """Match upload IDs against reservations.json; warn-only unless ENFORCE_RESERVATIONS."""
    if not RESERVATIONS_BUCKET:
        if ENFORCE_RESERVATIONS:
            raise ConfigError("Reservation store is not configured.")
        logger.info("RESERVATIONS_BUCKET unset; skipping reservation match.")
        return
    try:
        body = s3.get_object(Bucket=RESERVATIONS_BUCKET, Key=RESERVATIONS_KEY)["Body"].read()
        reservations = json.loads(body)
        if not isinstance(reservations, dict):
            raise ValueError("reservations.json is not a JSON object.")
    except s3.exceptions.NoSuchKey as error:
        if ENFORCE_RESERVATIONS:
            raise ConfigError("reservations.json not found.") from error
        logger.warning(
            "No reservations.json at s3://%s/%s; skipping reservation match.",
            RESERVATIONS_BUCKET,
            RESERVATIONS_KEY,
        )
        return
    except Exception as error:
        # Warn-only must never block the PR; only enforcement turns a read failure fatal.
        if ENFORCE_RESERVATIONS:
            raise ConfigError(f"Could not read reservations.json: {error}") from error
        logger.warning("Could not read reservations.json (%s); skipping match (warn-only).", error)
        return

    problems = _match_reservation(reservations, deposition_id, dataset_id)
    if not problems:
        return
    message = f"Reservation mismatch: {'; '.join(problems)}."
    if ENFORCE_RESERVATIONS:
        raise ValidationError(message)
    logger.warning("%s (ENFORCE_RESERVATIONS off; opening PR anyway)", message)


class GitHubIngestionPR:
    """Open (or find) the ingestion PR via the GitHub App API."""

    def __init__(self):
        if not GITHUB_SECRET_ID:
            raise ConfigError("GITHUB_SECRET_ID is not configured.")
        secret = boto3.client("secretsmanager").get_secret_value(SecretId=GITHUB_SECRET_ID)
        creds = json.loads(secret["SecretString"])
        app_id = str(creds.get("app_id") or "")
        private_key = creds.get("private_key") or ""
        installation_id = creds.get("installation_id")
        if not app_id or not private_key.strip():
            raise ConfigError("GitHub App credentials are not provisioned (app_id/private_key missing).")
        try:
            key = serialization.load_pem_private_key(private_key.encode(), password=None)
        except ValueError as error:
            raise ConfigError("GitHub App private key is not a valid PEM key.") from error

        def encode(value):
            return base64.urlsafe_b64encode(value).rstrip(b"=")

        now = int(time.time())
        header = encode(b'{"alg":"RS256","typ":"JWT"}')
        claims = encode(json.dumps({"iat": now - 60, "exp": now + 540, "iss": app_id}).encode())
        unsigned = header + b"." + claims
        signature = key.sign(unsigned, padding.PKCS1v15(), hashes.SHA256())
        jwt = (unsigned + b"." + encode(signature)).decode()

        self.repository = GITHUB_REPOSITORY
        self.base_branch = GITHUB_BASE_BRANCH
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {jwt}", "Accept": "application/vnd.github+json"})
        try:
            if not installation_id:
                installation = self.session.get(
                    f"https://api.github.com/repos/{self.repository}/installation", timeout=30,
                )
                installation.raise_for_status()
                installation_id = installation.json()["id"]
            token = self.session.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                timeout=30,
                json={
                    "repositories": [self.repository.split("/")[1]],
                    "permissions": {"contents": "write", "pull_requests": "write"},
                },
            )
            token.raise_for_status()
            self.session.headers.update({"Authorization": f"Bearer {token.json()['token']}"})
        except Exception:
            self.session.close()
            raise

    def request(self, method, path, *, allow_missing=False, **kwargs):
        response = self.session.request(
            method, f"https://api.github.com/repos/{self.repository}/{path}", timeout=30, **kwargs,
        )
        if allow_missing and response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def find(self, branch):
        pulls = self.request(
            "GET",
            "pulls",
            params={"state": "all", "head": f"{self.repository.split('/')[0]}:{branch}", "base": self.base_branch},
        )
        return pulls[0] if pulls else None

    def content(self, filename, ref):
        return self.request("GET", f"contents/{CONFIG_DIRECTORY}/{filename}", params={"ref": ref}, allow_missing=True)

    def create(self, branch, filename, config_text, *, title, body):
        existing = self.find(branch)
        if existing:
            return existing["html_url"]
        if self.content(filename, self.base_branch):
            raise ValidationError(
                f"{filename} already exists on {self.base_branch}; refusing to replace an ingested dataset.",
            )
        ref_path = f"git/ref/heads/{quote(branch, safe='/')}"
        if not self.request("GET", ref_path, allow_missing=True):
            base = self.request("GET", f"git/ref/heads/{quote(self.base_branch, safe='/')}")
            self.request("POST", "git/refs", json={"ref": f"refs/heads/{branch}", "sha": base["object"]["sha"]})
        previous = self.content(filename, branch)
        encoded = base64.b64encode(config_text.encode()).decode()
        if previous is None or "".join(previous.get("content", "").split()) != encoded:
            payload = {"message": title, "content": encoded, "branch": branch}
            if previous:
                payload["sha"] = previous["sha"]
            self.request("PUT", f"contents/{CONFIG_DIRECTORY}/{filename}", json=payload)
        # A previous request may have committed before its response was lost.
        existing = self.find(branch)
        if existing:
            return existing["html_url"]
        result = self.request(
            "POST", "pulls", json={"title": title, "body": body, "head": branch, "base": self.base_branch},
        )
        return result["html_url"]


def _process(bucket, marker_key):
    """Validate one upload and open its ingestion PR. Returns a status dict."""
    prefix = marker_key.rsplit("/", 1)[0]
    config_text, config = _load_config(bucket, prefix)
    deposition_id, dataset_id = _validate(config, prefix)
    _check_datamap_exists(config, bucket, prefix)
    _check_reserved(deposition_id, dataset_id)

    branch = f"deposition-{deposition_id}-dataset-{dataset_id}"
    filename = f"{dataset_id}.yaml"
    title = f"feat: ingest dataset {dataset_id}"
    body = (
        f"Uploaded by Embrella.\n\nDataset: {dataset_id}\nDeposition: {deposition_id}\n"
        f"Source: `s3://{bucket}/{prefix}`\n\n"
        "This is the uploaded config, unchanged. Portal CI performs ingestion-schema validation.\n"
        "`run_to_data_map.tsv` and source files remain in the uploaded S3 prefix."
    )

    if DRY_RUN:
        logger.info("DRY_RUN: would open PR %r (file %s/%s) on %s", title, CONFIG_DIRECTORY, filename, branch)
        return {"dataset_id": dataset_id, "deposition_id": deposition_id, "branch": branch, "dry_run": True}

    github = GitHubIngestionPR()
    try:
        url = github.create(branch, filename, config_text, title=title, body=body)
    finally:
        github.session.close()
    logger.info("Opened ingestion PR for dataset %s: %s", dataset_id, url)
    return {"dataset_id": dataset_id, "deposition_id": deposition_id, "branch": branch, "pr": url}


def _s3_markers(message):
    """Yield (bucket, key) for each ingest.ready ObjectCreated record in an S3 notification."""
    for s3_record in message.get("Records", []):
        if not s3_record.get("eventName", "").startswith("ObjectCreated"):
            continue
        bucket = s3_record["s3"]["bucket"]["name"]
        key = unquote_plus(s3_record["s3"]["object"]["key"])
        # Exact basename, so foo_ingest.ready / xingest.ready don't match.
        if key.rsplit("/", 1)[-1] == MARKER_NAME:
            yield bucket, key


def handler(event, context):
    """SQS -> S3 entry point (batch_size = 1)."""
    for record in event.get("Records", []):
        try:
            message = json.loads(record["body"])
        except (KeyError, ValueError):
            logger.warning("Skipping SQS record with no parseable body.")
            continue
        for bucket, key in _s3_markers(message):
            logger.info("Processing marker s3://%s/%s", bucket, key)
            try:
                logger.info("Done: %s", _process(bucket, key))
            except ValidationError as error:
                logger.error("Validation failed for s3://%s/%s: %s", bucket, key, error)
    return {"ok": True}
