# CryoET Reservation Lambda

This exists to help automate the generation and synchronization of what become deposition YAML files in dataset_configs/.

An S3 file `s3://cryoetportal-biohub-hpc-globus/SUBMISSION_METADATA/reservations.json` holds reservations for data submissions that are in progress,

and REST endpoints exist to reserve new submission IDs (i.e. create an element in that json file.)

Uses AWS lambda, syncs with what's instantiated into the git repo: [dataset_configs](https://github.com/chanzuckerberg/cryoet-data-portal-backend/tree/main/ingestion_tools/dataset_configs) git repo. 

## Prerequisites

- AWS CLI configured with credentials that have permissions to:
  - Create/manage CloudFormation stacks
  - Create IAM roles
  - Create Lambda functions (including Function URLs)
  - Read/write to `s3://cryoetportal-biohub-hpc-globus/SUBMISSION_METADATA/`

## Deploy

```bash
./deploy.sh
```

This will:
1. Zip `lambda_function.py` and upload it to S3
2. Deploy the CloudFormation stack `cryoetportal-submission-reservation`
3. Print the Lambda Function URL

## Teardown

```bash
./teardown.sh
```

Deletes the CloudFormation stack and the Lambda zip from S3. Does **not** delete `reservations.json` to avoid accidental data loss.

## API Endpoints

Replace `$URL` with the Function URL printed by `deploy.sh` (includes trailing `/`).

### List reservations (summary)

```bash
curl "${URL}/reservations"
```

Returns next available IDs and total count:

```json
{"next_dataset_id": 10471, "next_deposition_id": 10342, "reservation_count": 150}
```

### List reservations (full detail)

```bash
curl "${URL}/reservations?detail=true"
```

Returns all reserved ID pairs:

```json
{
  "reservations": [
    {"dataset_id": 10469, "deposition_id": null, "instantiated": true, "reserved_at": "2026-03-25T..."},
    {"dataset_id": 10470, "deposition_id": 10341, "instantiated": false, "reserved_at": "2026-03-25T..."}
  ],
  "next_dataset_id": 10471,
  "next_deposition_id": 10342
}
```

### Check if a dataset ID is instantiated

```bash
curl "${URL}/reservations/dataset/10469"
```

```json
{"dataset_id": 10469, "instantiated": true, "reservation": {"dataset_id": 10469, "deposition_id": null, "instantiated": true, "reserved_at": "..."}}
```

### Check if a deposition ID is instantiated

```bash
curl "${URL}/reservations/deposition/10340"
```

```json
{"deposition_id": 10340, "instantiated": true, "reservation": {"dataset_id": null, "deposition_id": 10340, "instantiated": true, "reserved_at": "..."}}
```

### Reserve a new dataset ID

```bash
curl "${URL}/reservations/dataset/new"
```

```json
{"dataset_id": 10470}
```

### Reserve a new deposition ID

```bash
curl "${URL}/reservations/deposition/new"
```

```json
{"deposition_id": 10341}
```
