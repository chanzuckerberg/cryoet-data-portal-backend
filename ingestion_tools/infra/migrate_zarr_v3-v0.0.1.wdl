version 1.0

# Migrate one dataset's published Zarr v2 images to Zarr v3 (scripts/migrate_zarr_v3.py run).

task cryoet_migrate_zarr_v3_workflow {
    input {
        String docker_image_id
        String aws_region
        String src_root
        String dest_root
        String flags
    }

    command <<<
        set -euxo pipefail
        export PYTHONUNBUFFERED=1
        python --version 1>&2
        cd /usr/src/app/ingestion_tools/scripts
        python migrate_zarr_v3.py run --src-root ~{src_root} --dest-root ~{dest_root} ~{flags} 1>&2
    >>>

    runtime {
        docker: docker_image_id
    }
}

workflow cryoet_migrate_zarr_v3 {
    input {
        String docker_image_id = "cryoet_data_ingestion:latest"
        String aws_region = "us-west-2"
        String src_root = "s3://cryoet-data-portal-public"
        String dest_root = "s3://cryoet-data-portal-staging"
        String flags
    }

    call cryoet_migrate_zarr_v3_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        src_root = src_root,
        dest_root = dest_root,
        flags = flags
    }

    output {
        File log = "output.txt"
    }
}
