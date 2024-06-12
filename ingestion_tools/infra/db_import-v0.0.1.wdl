version 1.0

task cryoet_data_dbimport_workflow {
    input {
        String docker_image_id
        String aws_region
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
        cd /usr/src/app/ingestion_tools/scripts
        set +x
        POSTGRES_URL=$(aws secretsmanager get-secret-value --secret-id ~{environment}/db_uri | jq -r .SecretString | jq -r .db_uri)
        echo python db_import.py load ~{s3_bucket} ~{https_prefix} POSTGRES_URL ~{flags} 1>&2
        python db_import.py load ~{s3_bucket} ~{https_prefix} $POSTGRES_URL ~{flags} 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_data_dbimport {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String s3_bucket = "cryoet-data-portal-staging"
        String https_prefix
        String environment
        String flags
    }

    call cryoet_data_dbimport_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        s3_bucket = s3_bucket,
        https_prefix = https_prefix,
        environment = environment,
        flags = flags
    }

    output {
        File log = "output.txt"
    }
}
