version 1.0

task cryoet_data_validation {
    input {
        String docker_image_id
        String aws_region
        String input_bucket
        String output_bucket
        String output_dir
        String extra_args
        String dataset
    }

    command <<<
        set -euxo pipefail
        export PYTHONUNBUFFERED=1
        python --version 1>&2
        ls -l 1>&2
        pwd 1>&2
        # TODO - create separate image for running validations that includes allure.
        echo ==== 1>&2
        echo Installing Allure 1>&2
        echo ==== 1>&2
        apt update && apt install -y default-jre-headless
        wget -q https://github.com/allure-framework/allure2/releases/download/2.32.0/allure_2.32.0-1_all.deb
        dpkg -i allure_2.32.0-1_all.deb
        echo ==== 1>&2
        echo Running tests 1>&2
        echo ==== 1>&2
        cd /usr/src/app/ingestion_tools/scripts/data_validation/standardized
        python allure_tests.py --output-dir ~{output_dir} --datasets ~{dataset} --history --input-bucket ~{input_bucket} --output-bucket ~{output_bucket} --extra-args '~{extra_args}' 1>&2
        >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_data_validation_wf {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String input_bucket
        String output_bucket
        String output_dir
        String extra_args
        String dataset
    }

    call cryoet_data_validation {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        input_bucket = input_bucket,
        output_bucket = output_bucket,
        output_dir = output_dir,
        extra_args = extra_args,
        dataset = dataset
    }

    output {
        File log = "output.txt"
    }
}
