version 1.0

task cryoet_data_sync_workflow {
    input {
        String docker_image_id
        String aws_region
        String input_path
        String input_bucket
        String output_bucket
        String output_path
        String flags
    }

    command <<<
        set -euxo pipefail
        # S3 -> S3 sync is a server-side copy, so throughput is bounded by how many requests
        # we keep in flight, not by bandwidth. The CLI default of 10 leaves a multi-vCPU
        # container idle on datasets that are tens of thousands of small objects (zarr).
        aws configure set default.s3.max_concurrent_requests 100
        aws configure set default.s3.max_queue_size 10000
        # tee to output.txt so the result is a real WDL output and gets published under the
        # job's OutputPrefix, instead of existing only in CloudWatch.
        aws s3 sync ~{flags} s3://~{input_bucket}/~{input_path} s3://~{output_bucket}/~{output_path} 2>&1 | tee output.txt 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }

    output {
        File log = "output.txt"
    }
}

workflow cryoet_data_sync {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String input_bucket = "cryoet-data-portal-staging"
        String input_path
        String output_bucket = "cryoet-data-portal-public"
        String output_path
        String flags
    }

    call cryoet_data_sync_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        input_bucket = input_bucket,
        input_path = input_path,
        output_bucket = output_bucket,
        output_path = output_path,
        flags = flags
    }

    output {
        File log = cryoet_data_sync_workflow.log
    }
}
