from common.db_models import Run


def populate_run():
    Run(
        id=2,
        dataset_id=30001,
        name="RUN1",
        s3_prefix="s3://test-public-bucket/1000/RUN1",
        https_prefix="http://test.com/10000/RUN1",
    ).save(force_insert=True)
