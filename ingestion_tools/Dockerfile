FROM python:3.11.6-bookworm

WORKDIR /usr/src/app
RUN apt update && apt install -y wget
# bio3d.colorado.edu isn't sending an intermediate cert, which breaks openssl (no AIA support). So we're installing it here.
RUN wget http://crt.sectigo.com/SectigoRSAOrganizationValidationSecureServerCA.crt && \
    openssl x509 -in SectigoRSAOrganizationValidationSecureServerCA.crt -out intermediate.pem
RUN wget --ca-certificate intermediate.pem https://bio3d.colorado.edu/imod/AMD64-RHEL5/imod_4.11.24_RHEL7-64_CUDA10.1.sh \
        && bash imod_4.11.24_RHEL7-64_CUDA10.1.sh -yes

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV IMOD_DIR /usr/local/IMOD

COPY ./dataset_configs ./dataset_configs
COPY ./scripts ./scripts
WORKDIR /usr/src/app/scripts
