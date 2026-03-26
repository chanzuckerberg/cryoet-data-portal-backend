import json
import re
import time
import urllib.request
from datetime import datetime, timezone
import boto3

S3_BUCKET = "cryoetportal-biohub-hpc-globus"
S3_KEY = "SUBMISSION_METADATA/reservations.json"
GITHUB_API_URL = "https://api.github.com/repos/chanzuckerberg/cryoet-data-portal-backend/contents/ingestion_tools/dataset_configs"
CACHE_TTL_SECONDS = 10

s3 = boto3.client("s3")

# Module-level cache (persists across warm Lambda invocations)
_cache = {"data": None, "timestamp": 0}

EMPTY_DATA = {
    "datasets": {},
    "depositions": {},
    "next_dataset_id": 10000,
    "next_deposition_id": 10000,
}

def load_reservations():
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return json.loads(obj["Body"].read())
    except s3.exceptions.NoSuchKey:
        return {**EMPTY_DATA}
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return {**EMPTY_DATA}
        raise

def save_reservations(data):
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )

def fetch_git_ids():
    DATASET_RE = re.compile(r"^(\d+)(?:_draft)?\.yaml$")
    DEPOSITION_RE = re.compile(r"^deposition_(\d+)\.yaml$")

    req = urllib.request.Request(GITHUB_API_URL, headers={"Accept": "application/vnd.github.v3+json"})
    with urllib.request.urlopen(req) as resp:
        items = json.loads(resp.read())
    dataset_ids = set()
    deposition_ids = set()
    for item in items:
        name = item["name"]
        m = DATASET_RE.match(name)
        if m:
            dataset_ids.add(int(m.group(1)))
            continue
        m = DEPOSITION_RE.match(name)
        if m:
            deposition_ids.add(int(m.group(1)))
    return dataset_ids, deposition_ids

def sync_with_git(data):
    git_dataset_ids, git_deposition_ids = fetch_git_ids()
    changed = False
    now = datetime.now(timezone.utc).isoformat()

    for did in sorted(git_dataset_ids):
        key = str(did)
        if key not in data["datasets"]:
            data["datasets"][key] = {"instantiated": True, "reserved_at": now}
            changed = True
        elif not data["datasets"][key].get("instantiated"):
            data["datasets"][key]["instantiated"] = True
            changed = True

    for dep_id in sorted(git_deposition_ids):
        key = str(dep_id)
        if key not in data["depositions"]:
            data["depositions"][key] = {"instantiated": True, "reserved_at": now}
            changed = True
        elif not data["depositions"][key].get("instantiated"):
            data["depositions"][key]["instantiated"] = True
            changed = True

    all_dataset_ids = {int(k) for k in data["datasets"]}
    all_deposition_ids = {int(k) for k in data["depositions"]}
    next_d = (max(all_dataset_ids) + 1) if all_dataset_ids else 10000
    next_dep = (max(all_deposition_ids) + 1) if all_deposition_ids else 10000
    if next_d != data.get("next_dataset_id") or next_dep != data.get("next_deposition_id"):
        changed = True
    data["next_dataset_id"] = next_d
    data["next_deposition_id"] = next_dep

    if changed:
        save_reservations(data)
    return data

def get_synced_data(force_refresh=False):
    """Return reservation data, using cached version if within TTL."""
    now = time.monotonic()
    if not force_refresh and _cache["data"] is not None and (now - _cache["timestamp"]) < CACHE_TTL_SECONDS:
        return _cache["data"]

    data = load_reservations()
    data = sync_with_git(data)
    _cache["data"] = data
    _cache["timestamp"] = now
    return data

def respond(status, body):
    return {"statusCode": status, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body)}

def handler(event, context):
    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    query = event.get("queryStringParameters") or {}

    # /reservations/dataset/new or /reservations/deposition/new force a fresh sync
    is_new = path in ("/reservations/dataset/new", "/reservations/deposition/new")
    data = get_synced_data(force_refresh=is_new)

    # GET /reservations
    if path == "/reservations" and method == "GET":
        if query.get("detail") == "true":
            return respond(200, data)
        return respond(200, {
            "next_dataset_id": data["next_dataset_id"],
            "next_deposition_id": data["next_deposition_id"],
            "dataset_count": len(data["datasets"]),
            "deposition_count": len(data["depositions"]),
        })

    # GET /reservations/dataset/{id}
    if path.startswith("/reservations/dataset/") and path != "/reservations/dataset/new" and method == "GET":
        try:
            did = int(path.split("/")[-1])
        except ValueError:
            return respond(400, {"error": "Invalid dataset id"})
        entry = data["datasets"].get(str(did))
        return respond(200, {"dataset_id": did, "instantiated": bool(entry and entry.get("instantiated")), "reservation": entry})

    # GET /reservations/deposition/{id}
    if path.startswith("/reservations/deposition/") and path != "/reservations/deposition/new" and method == "GET":
        try:
            dep_id = int(path.split("/")[-1])
        except ValueError:
            return respond(400, {"error": "Invalid deposition id"})
        entry = data["depositions"].get(str(dep_id))
        return respond(200, {"deposition_id": dep_id, "instantiated": bool(entry and entry.get("instantiated")), "reservation": entry})


    # GET /reservations/dataset/new — reserve a new dataset_id
    if path == "/reservations/dataset/new" and method == "GET":
        new_did = data["next_dataset_id"]
        now = datetime.now(timezone.utc).isoformat()
        data["datasets"][str(new_did)] = {"instantiated": False, "reserved_at": now}
        data["next_dataset_id"] = new_did + 1
        save_reservations(data)
        _cache["data"] = data
        _cache["timestamp"] = time.monotonic()
        return respond(200, {"dataset_id": new_did})

    # GET /reservations/deposition/new — reserve a new deposition_id
    if path == "/reservations/deposition/new" and method == "GET":
        new_dep = data["next_deposition_id"]
        now = datetime.now(timezone.utc).isoformat()
        data["depositions"][str(new_dep)] = {"instantiated": False, "reserved_at": now}
        data["next_deposition_id"] = new_dep + 1
        save_reservations(data)
        _cache["data"] = data
        _cache["timestamp"] = time.monotonic()
        return respond(200, {"deposition_id": new_dep})

    return respond(404, {"error": "Not found"})