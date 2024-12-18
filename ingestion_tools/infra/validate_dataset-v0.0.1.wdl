version 1.0

task cryoet_data_validation {
    input {
        String docker_image_id
        String aws_region
        String config_file
        String input_bucket
        String output_bucket
        String dataset
    }

    command <<<
        set -euxo pipefail
        export PYTHONUNBUFFERED=1
        python --version 1>&2
        ls -l 1>&2
        pwd 1>&2
        cd /usr/src/app/ingestion_tools/scripts
        python allure_tests.py --datasets ~{dataset} --input-bucket ~{input_bucket} --output-bucket ~{output_bucket}
        >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_data_validation {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String config_file
        String input_bucket
        String output_bucket
        String dataset
    }

    call cryoet_data_validation {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        config_file = config_file,
        input_bucket = input_bucket,
        output_bucket = output_bucket,
        dataset = dataset
    }

    output {
        File log = "output.txt"
    }
}
