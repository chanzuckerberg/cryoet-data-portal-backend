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
        original_dir=$(pwd)
        cd /usr/src/app/ingestion_tools/scripts
        set +x
        POSTGRES_URL=$(aws secretsmanager get-secret-value --secret-id ~{environment}/db_uri | jq -r .SecretString | jq -r .db_uri)
        echo python db_import.py load ~{s3_bucket} ~{https_prefix} POSTGRES_URL ~{flags} 1>&2
        python db_import.py load ~{s3_bucket} ~{https_prefix} $POSTGRES_URL ~{flags} 1>&2
        cd $original_dir
        echo "done" > done.txt
    >>>

    runtime {
        docker: docker_image_id
    }
    output {
        String done = read_string("done.txt")
    }
}

task cryoet_data_dbimport_v2_workflow {
    input {
        String done
        String docker_image_id = "apiv2-x86:latest"
        String aws_region
        String s3_bucket
        String https_prefix
        String environment
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
        apt install -y curl unzip jq
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip -q awscliv2.zip && ./aws/install && rm -rf ./aws
        POSTGRES_URL=$(aws secretsmanager get-secret-value --secret-id ~{environment}/v2_db_uri | jq -r .SecretString | jq -r .db_uri)
        # TODO - Scrape ID's from the v1 api so we keep things in sync
        pip install cryoet-data-portal==3.1.1
        cd /app
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
        String v2_docker_image_id = "cryoet_data_ingestion:latest"
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String s3_bucket = "cryoet-data-portal-staging"
        String https_prefix
        String environment
        String flags
        String scrape_flags
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
        done = cryoet_data_dbimport_workflow.done,
        docker_image_id = v2_docker_image_id,
        aws_region = aws_region,
        s3_bucket = s3_bucket,
        https_prefix = https_prefix,
        environment = environment,
        scrape_flags = scrape_flags,
        flags = flags
    }

    output {
        File log = "output.txt"
    }
}
