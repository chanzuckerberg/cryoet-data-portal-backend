FROM python:3.12-slim-bookworm AS build
RUN apt-get update && \
    apt-get install -y vim wget nginx nginx-extras procps ripgrep make gcc git && \
    apt-get clean

# Ensure pip/build tooling is sane BEFORE installing poetry or running poetry install.
# Force-reinstall so partial/corrupted installs are replaced.
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade --force-reinstall setuptools wheel packaging

ENV POETRY_VERSION=1.8
# Some base python dependencies to kickstart our container build.
RUN python3 -m pip install --no-cache-dir poetry==$POETRY_VERSION supervisor

# Install dev deps
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Create an empty dir to mount our test app to.
RUN mkdir -p /app
WORKDIR /app

COPY . .
ENV PYTHONPATH=.
ENTRYPOINT []
CMD ["/usr/local/bin/supervisord", "-c", "/app/etc/supervisord.conf"]
