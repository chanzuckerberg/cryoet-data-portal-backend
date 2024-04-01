version 1.0

task cryoet_data_ingestion_workflow {
    input {
        String docker_image_id
        String aws_region
        String input_bucket
        String dataset
    }

    command <<<
        set -euxo pipefail
	    export PYTHONUNBUFFERED=1
	    python --version 1>&2
	    ls -l 1>&2
	    pwd 1>&2
        cd /usr/src/app/ingestion_tools/scripts
	python fix_zarr_attrs.py upgrade ~{input_bucket} ~{dataset} 00011 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_data_ingestion {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String input_bucket
        String dataset
    }

    call cryoet_data_ingestion_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        input_bucket = input_bucket,
        dataset = dataset,
    }

    output {
        File log = "output.txt"
    }
}
