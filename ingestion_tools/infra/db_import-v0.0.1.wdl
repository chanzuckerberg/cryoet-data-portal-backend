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
        touch done.txt
        cd /usr/src/app/ingestion_tools/scripts
        set +x
        POSTGRES_URL=$(aws secretsmanager get-secret-value --secret-id ~{environment}/db_uri | jq -r .SecretString | jq -r .db_uri)
        echo python db_import.py load ~{s3_bucket} ~{https_prefix} POSTGRES_URL ~{flags} 1>&2
        python db_import.py load ~{s3_bucket} ~{https_prefix} $POSTGRES_URL ~{flags} 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }
    output {
        String entity_id = read_string("entity_id")
        File done = "metadata.tsv"
    }
}

task cryoet_data_dbimport_v2_workflow {
    input {
        String docker_image_id
        String aws_region
        String s3_bucket
        String https_prefix
        String environment
        Boolean delete_first
        String scrape_flags
        String flags
    }

    command <<<
        set -euxo pipefail
        export PYTHONUNBUFFERED=1
        python --version 1>&2
        ls -l 1>&2
        pwd 1>&2
        set +x
        POSTGRES_URL=$(aws secretsmanager get-secret-value --secret-id ~{environment}/v2_db_uri | jq -r .SecretString | jq -r .db_uri)
        # Scrape ID's from the v1 api so we keep things in sync
        if [ -n "~{delete_first}" ]; then
          python3 -m scripts.delete_dataset --db-uri $POSTGRES_URL --i-am-super-sure yes ~{dataset_id};
        fi
        python3 -m scripts.scrape ~{environment} --db-uri $POSTGRES_URL ~{scrape_flags}
        # Scrape ID's from the v1 api so we keep things in sync
        python3 -m scripts.scrape ~{environment} --db-uri $POSTGRES_URL ~{scrape_flags}
        # Read data from s3 into the v2 db.
        python3 -m db_import.importer load --postgres_url $POSTGRES_URL ~{s3_bucket} ~{https_prefix} ~{flags}
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
    call cryoet_data_dbimport_v2_workflow {
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
