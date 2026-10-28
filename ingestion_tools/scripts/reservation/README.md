# CryoET Reservation Lambda

This exists to help automate the generation and synchronization of what become deposition YAML files in dataset_configs/.

An S3 file `s3://cryoetportal-biohub-hpc-globus/SUBMISSION_METADATA/reservations.json` holds reservations for data submissions that are in progress,

and REST endpoints exist to reserve new submission IDs (i.e. create an element in that json file.)

Uses AWS lambda, syncs with what's instantiated into the [dataset_configs](https://github.com/chanzuckerberg/cryoet-data-portal-backend/tree/main/ingestion_tools/dataset_configs) git repo.

## Configuration

The Lambda reads its AWS paths from environment variables (set via Terraform / GH
secrets):

| Variable | Required | Default | Description |
|---|---|---|---|
| `RESERVATIONS_BUCKET` | yes | — | S3 bucket holding `reservations.json` |
| `RESERVATIONS_KEY` | no | `SUBMISSION_METADATA/reservations.json` | S3 key for the reservations file |
| `DATASET_CONFIGS_API_URL` | no | GitHub contents API for `ingestion_tools/dataset_configs` | Source of instantiated IDs |
| `GITHUB_TOKEN` | no | — | If set, authenticates the GitHub API call (raises the rate limit from 60 to 5000 req/hr) |

## Build & deploy

The container image is built and pushed to ECR by CI
([`.github/workflows/reservation-build.yaml`](../../../.github/workflows/reservation-build.yaml))
on merges to `main` that touch this directory. Images are tagged with the commit SHA.

Deployment is managed by Terraform in
[`chanzuckerberg/cryoet-infra`](https://github.com/chanzuckerberg/cryoet-infra).

## API Endpoints

Replace `$URL` with the Lambda Function URL (from the Terraform output in `cryoet-infra` includes trailing `/`).

### List reservations (summary)

```bash
curl "${URL}/reservations"
```

Returns next available IDs and counts:

```json
{"next_dataset_id": 10471, "next_deposition_id": 10342, "dataset_count": 150, "deposition_count": 120}
```

### List reservations (full detail)

```bash
curl "${URL}/reservations?detail=true"
```

Returns the full reservation state, keyed by ID:

```json
{
  "datasets": {
    "10469": {"instantiated": true, "reserved_at": "2026-03-25T..."},
    "10470": {"instantiated": false, "reserved_at": "2026-03-25T..."}
  },
  "depositions": {
    "10341": {"instantiated": false, "reserved_at": "2026-03-25T..."}
  },
  "next_dataset_id": 10471,
  "next_deposition_id": 10342
}
```

### Check if a dataset ID is instantiated

```bash
curl "${URL}/reservations/dataset/10469"
```

```json
{"dataset_id": 10469, "instantiated": true, "reservation": {"instantiated": true, "reserved_at": "..."}}
```

### Check if a deposition ID is instantiated

```bash
curl "${URL}/reservations/deposition/10340"
```

```json
{"deposition_id": 10340, "instantiated": true, "reservation": {"instantiated": true, "reserved_at": "..."}}
```

### Reserve a new dataset ID

```bash
curl -X POST "${URL}/reservations/dataset/new"
```

```json
{"dataset_id": 10470}
```

### Reserve a new deposition ID

```bash
curl -X POST "${URL}/reservations/deposition/new"
```

```json
{"deposition_id": 10341}
```
