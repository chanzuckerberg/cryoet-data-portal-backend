FROM hasura/graphql-engine:v2.25.1.cli-migrations-v3
# Install DB certs.
ADD https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem /usr/local/share/ca-certificates/global-bundle.crt
RUN update-ca-certificates

ADD ./migrations /hasura-migrations
ADD ./metadata /hasura-metadata
ADD . /app
