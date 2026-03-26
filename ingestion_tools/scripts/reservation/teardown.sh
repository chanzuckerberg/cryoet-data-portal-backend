#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="cryoetportal-submission-reservation"
S3_BUCKET="cryoetportal-biohub-hpc-globus"
S3_KEY="SUBMISSION_METADATA/lambda/reservation_lambda.zip"

echo "Deleting CloudFormation stack: ${STACK_NAME}..."
aws cloudformation delete-stack --stack-name "$STACK_NAME"

echo "Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"

echo "Removing Lambda zip from s3://${S3_BUCKET}/${S3_KEY}..."
aws s3 rm "s3://${S3_BUCKET}/${S3_KEY}"

echo "Teardown complete."
