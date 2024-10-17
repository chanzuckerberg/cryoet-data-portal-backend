version 1.0


task cryoet_folder_migration_workflow {
    input {
        String docker_image_id
        String aws_region
        String config_file
        String output_bucket
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
        echo python migrate_folder_structure.py migrate ~{config_file} ~{output_bucket} ~{flags} 1>&2
        python migrate_folder_structure.py migrate ~{config_file} ~{output_bucket} ~{flags} 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_folder_migration {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String config_file
        String output_bucket
        String flags
    }

    call cryoet_folder_migration_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        config_file = config_file,
        output_bucket = output_bucket,
        flags = flags
    }

    output {
        File log = "output.txt"
    }
}
