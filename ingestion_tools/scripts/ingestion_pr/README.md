# CryoET Ingestion-PR Lambda

Opens a Data Portal ingestion PR when a deposition upload finishes. An `ingest.ready` marker in
`s3://cryoetportal-biohub-hpc-globus/CZII/<deposition>/<dataset>/` triggers it
(S3 → SQS → Lambda); it reads the uploaded `portal_dataset_config.yaml`, validates
it, and opens a PR adding `ingestion_tools/dataset_configs/<dataset_id>.yaml`.
Duplicate-PR protection is GitHub-side.

## Configuration (env vars)

| Variable | Required | Default |
|---|---|---|
| `GITHUB_SECRET_ID` | yes | n/a — Secrets Manager id/ARN holding `{app_id, private_key, installation_id?}` |
| `GITHUB_REPOSITORY` | no | `chanzuckerberg/cryoet-data-portal-backend` (lets you test against a sandbox repo) |
| `UPLOAD_PREFIX` | no | `CZII` — top-level S3 upload prefix (matches Embrella's `deposition_sync_destination`) |
| `DRY_RUN` | no | `true` — validate + log, do **not** open a PR |
| `RESERVATIONS_BUCKET` | no | unset — S3 bucket holding `reservations.json`. Unset ⇒ reservation match skipped |
| `ENFORCE_RESERVATIONS` | no | `false` — warn-only; when `true`, reject IDs not present in `reservations.json` |

(`GITHUB_BASE_BRANCH` = `main` and the `reservations.json` key are constants in the code.)

## Reservation match

Before opening a PR, the Lambda matches the upload's `deposition_id`/`dataset_id`
against `reservations.json` — the reservation service's source of truth — so an ID
that never came from it can't reach a PR.
## GitHub credential

The Lambda authenticates as the dedicated **`embrella-ingestion`** GitHub App
(short-lived installation token, scoped to this repo, `contents` + `pull_requests`
write). The App and its Secrets Manager secret `embrella/ingestion/github-app` are
provisioned outside this repo.

## Deploy

1. Merge to `main`. CI ([workflow](../../../.github/workflows/ingestion-pr-build.yaml))
   bundles the deps and uploads `LAMBDA/ingestion_pr_lambda-<sha>.zip` (top-level `LAMBDA/`,
   outside Embrella's `SUBMISSION_METADATA/*` write scope, so it can't be overwritten).
   **This must run once before the first Terraform apply** — the zip has to exist in
   S3 before Terraform creates the function, so the CI job gates the first deploy.
2. Copy the `lambda_zip_key` from the CI run summary.
3. Set it in [`cryoet-infra`](https://github.com/chanzuckerberg/cryoet-infra) and apply.

The Lambda bundles `requests`, `pyyaml`, and `cryptography` (pinned in
`requirements.txt`); `boto3` is provided by the runtime. See the workflow for the
exact `pip` platform flags.

## Validation

`_validate` ties the config to its upload location: required sections present,
`deposition_id` and dataset identifier match the `CZII/<deposition>/<dataset>` path,
and `source_prefix` matches. It also confirms `run_data_map_file` (if set) exists in
S3 — Portal CI validates the schema but has no S3 access, so the Lambda is the only
place that can catch a missing map file before ingestion. Broader schema completeness
is left to Portal CI + the human PR review.
