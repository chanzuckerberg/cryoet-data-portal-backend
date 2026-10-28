# Container image for the reservation Lambda.
# Built and pushed to ECR by .github/workflows/reservation-build.yaml;
# deployed by Terraform in chanzuckerberg/cryoet-infra.
FROM public.ecr.aws/lambda/python:3.12

# boto3 ships in the Lambda Python base image and the function otherwise only
# uses the standard library, so there are no extra dependencies to install.

COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

# <module>.<function>
CMD ["lambda_function.handler"]
