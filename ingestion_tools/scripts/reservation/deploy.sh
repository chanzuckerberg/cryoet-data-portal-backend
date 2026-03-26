#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STACK_NAME="cryoetportal-submission-reservation"
S3_BUCKET="cryoetportal-biohub-hpc-globus"
S3_KEY="SUBMISSION_METADATA/lambda/reservation_lambda.zip"

echo "Packaging Lambda code..."
cd "$SCRIPT_DIR"
rm -f reservation_lambda.zip
zip reservation_lambda.zip lambda_function.py

echo "Uploading to s3://${S3_BUCKET}/${S3_KEY}..."
aws s3 cp reservation_lambda.zip "s3://${S3_BUCKET}/${S3_KEY}"

echo "Deploying CloudFormation stack: ${STACK_NAME}..."
aws cloudformation deploy \
    --template-file reservation_stack.yaml \
    --stack-name "$STACK_NAME" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        CodeS3Bucket="$S3_BUCKET" \
        CodeS3Key="$S3_KEY" \
    --no-fail-on-empty-changeset

echo "Updating Lambda function code..."
aws lambda update-function-code \
    --function-name cryoetportal-submission-reservation \
    --s3-bucket "$S3_BUCKET" \
    --s3-key "$S3_KEY" \
    --no-cli-pager

echo "Getting Function URL..."
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='FunctionUrl'].OutputValue" \
    --output text

rm -f reservation_lambda.zip
echo "Done."
