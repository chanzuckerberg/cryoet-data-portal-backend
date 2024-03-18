version 1.0

task cryoet_data_ingestion_workflow {
    input {
        String docker_image_id
        String aws_region
        String config_file
        String input_bucket
        String output_path
        String flags
    }

    command <<<
        set -euxo pipefail
        export PYTHONUNBUFFERED=1
        python --version 1>&2
        ls -l 1>&2
        pwd 1>&2
        cd /usr/src/app/ingestion_tools/scripts
        python standardize_dirs.py convert ~{config_file} ~{input_bucket} ~{output_path} ~{flags} 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_data_ingestion {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String config_file
        String input_bucket = "cryoetportal-rawdatasets-dev"
        String output_path
        String flags
    }

    call cryoet_data_ingestion_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        config_file = config_file,
        input_bucket = input_bucket,
        output_path = output_path,
        flags = flags
    }

    output {
        File log = "output.txt"
    }
}
