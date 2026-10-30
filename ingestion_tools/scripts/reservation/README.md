# CryoET Reservation Lambda

Reserves dataset and deposition IDs for in-progress data submissions.

- State lives in `s3://cryoetportal-biohub-hpc-globus/SUBMISSION_METADATA/reservations.json`.
- Syncs with IDs already instantiated in [`dataset_configs`](../../dataset_configs).
- Runs as an AWS Lambda behind a Function URL.

## Configuration (env vars)

| Variable | Required | Default |
|---|---|---|
| `RESERVATIONS_BUCKET` | yes | n/a |
| `RESERVATIONS_KEY` | no | `SUBMISSION_METADATA/reservations.json` |
| `DATASET_CONFIGS_API_URL` | no | GitHub contents API for `dataset_configs` |
| `GITHUB_TOKEN` | no | n/a (raises the GitHub rate limit) |

## Deploy

1. Merge to `main`. CI ([workflow](../../../.github/workflows/reservation-build.yaml)) uploads `SUBMISSION_METADATA/lambda/reservation_lambda-<sha>.zip` to S3.
2. Copy the `lambda_zip_key` from the CI run summary.
3. Set it in [`cryoet-infra`](https://github.com/chanzuckerberg/cryoet-infra) and apply.

**Cutover:** freeze the old CloudFormation function (`cryoetportal-submission-reservation`) first, because it writes the same `reservations.json`. Then repoint `RESERVATION_LAMBDA_URL` (Embrella) and the CLI URL.

## API

`$URL` is the Function URL from the Terraform output (ends with `/`). All calls are `GET`. The URL uses `AWS_IAM` auth, so requests must be **SigV4-signed** (service `lambda`, region `us-west-2`).

| Endpoint | Returns |
|---|---|
| `/reservations` | Next IDs and counts |
| `/reservations?detail=true` | Full state, keyed by ID |
| `/reservations/dataset/<id>` | Whether the dataset ID is instantiated |
| `/reservations/deposition/<id>` | Whether the deposition ID is instantiated |
| `/reservations/dataset/new` | Reserves a new dataset ID: `{"dataset_id": 10470}` |
| `/reservations/deposition/new` | Reserves a new deposition ID: `{"deposition_id": 10341}` |
