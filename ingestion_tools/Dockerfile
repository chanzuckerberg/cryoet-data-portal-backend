FROM python:3.11.6-bookworm

WORKDIR /usr/src/app
RUN mkdir ingestion_tools

# Base utilities
RUN apt update && apt install -y wget unzip jq

# IMOD helps with MRC ingestion
# bio3d.colorado.edu isn't sending an intermediate cert, which breaks openssl (no AIA support). So we're installing it here.
RUN wget http://crt.sectigo.com/SectigoRSAOrganizationValidationSecureServerCA.crt && \
    openssl x509 -in SectigoRSAOrganizationValidationSecureServerCA.crt -out /tmp/intermediate.pem && \
    wget --ca-certificate /tmp/intermediate.pem https://bio3d.colorado.edu/imod/AMD64-RHEL5/imod_4.11.24_RHEL7-64_CUDA10.1.sh \
        && bash imod_4.11.24_RHEL7-64_CUDA10.1.sh -yes && rm /tmp/intermediate.pem

# Install the AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install && rm -rf ./aws

ENV IMOD_DIR /usr/local/IMOD

# Get our packaging house in order
RUN pip install --upgrade pip
ENV POETRY_VERSION=1.8.3
RUN python3 -m pip install --no-cache-dir poetry==$POETRY_VERSION

# Install our dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
ENV PYTHONPATH=.
RUN poetry install

COPY . ./ingestion_tools/
WORKDIR /usr/src/app/ingestion_tools/scripts
