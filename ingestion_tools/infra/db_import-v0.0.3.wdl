version 1.0

task cryoet_data_dbimport_v2_workflow {
    input {
        String docker_image_id = "apiv2-x86:latest"
        String s3_bucket
        String https_prefix
        String environment
        String flags
    }

    command <<<
        set -euxo pipefail
        export PYTHONUNBUFFERED=1
        python --version 1>&2
        ls -l 1>&2
        pwd 1>&2
        set +x
        apt install -y curl unzip jq
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip -q awscliv2.zip && ./aws/install && rm -rf ./aws
        pip install psycopg2-binary
        POSTGRES_URL=$(aws secretsmanager get-secret-value --secret-id ~{environment}/v2_db_uri | jq -r .SecretString | jq -r .db_uri)
        # TODO - Scrape ID's from the v1 api so we keep things in sync
        pip install cryoet-data-portal==3.1.1
        cd /app
        # Read data from s3 into the v2 db.
        echo "Load data from s3" 1>&2
        echo  python3 -m db_import.importer load --postgres_url POSTGRES_URL ~{s3_bucket} ~{https_prefix} ~{flags} 1>&2
        python3 -m db_import.importer load --postgres_url $POSTGRES_URL ~{s3_bucket} ~{https_prefix} ~{flags} 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_data_dbimport {
    input {
        String v2_docker_image_id = "cryoet_data_ingestion:latest"
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String s3_bucket = "cryoet-data-portal-staging"
        String https_prefix
        String environment
        String flags
    }

    call cryoet_data_dbimport_v2_workflow {
        input:
        docker_image_id = v2_docker_image_id,
        s3_bucket = s3_bucket,
        https_prefix = https_prefix,
        environment = environment,
        flags = flags
    }

    output {
        File log = "output.txt"
    }
}
