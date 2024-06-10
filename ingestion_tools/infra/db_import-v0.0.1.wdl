version 1.0

task cryoet_data_dbimport_workflow {
    input {
        String docker_image_id
        String aws_region
        String s3_bucket
        String https_prefix
        String flags
    }

    command <<<
        set -euxo pipefail
        export PYTHONUNBUFFERED=1
        python --version 1>&2
        ls -l 1>&2
        pwd 1>&2
        cd /usr/src/app/ingestion_tools/scripts
	POSTGRES_URL="read this from an AWS secret"
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
        String flags
    }

    call cryoet_data_dbimport_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        s3_bucket = s3_bucket,
        https_prefix = https_prefix,
        flags = flags
    }

    output {
        File log = "output.txt"
    }
}
