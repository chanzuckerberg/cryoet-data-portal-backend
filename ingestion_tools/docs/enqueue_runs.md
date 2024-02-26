
## Setup

Before running the script, ensure all the required packages are installed by running

```
cd ingestion_tools/scripts  
pip install -r requirements.txt
```

## Running 

The `enqueue_runs.py` queues the required processing. 

To learn all the options available:
```
python enqueue_runs.py queue --help
```

#### Example:

```
python enqueue_runs.py queue staging  ../dataset_configs/10000.yaml cryoetportal-rawdatasets-dev cryoetportal-output-test --import-dataset-metadata
```

## Building and pushing up an image:

### Building an image:

Use docker build to create an image from the infra_tools folder and push that to the ECR

```
cd ingestion_tools
docker build . -t <account_id>.dkr.ecr.<aws_region>.amazonaws.com/<ecr_repo>:<new_tag> --platform linux/amd64
```

### Pushing image to ECR

```
docker push <account_id>.dkr.ecr.<aws_region>.amazonaws.com/<ecr_repo>:<new_tag>
```
