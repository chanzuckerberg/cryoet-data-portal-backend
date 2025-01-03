# Releasing updates to Ingestion 

There is no fixed release cycle for updates. Changes merged into the main branch are automatically picked up and incorporated into the subsequent ingestion process.

**Important:** Please ensure that you thoroughly test and validate your changes for regressions before merging them to the main branch. Inaccurate changes can impact the ingestion process.


## How Does the Process Work?

The ingestion process is automated using GitHub Actions. Here’s a breakdown of what happens:

1. When changes are merged into main, the GitHub Actions workflow is triggered.
2. The workflow builds a Docker image and pushes it to the Amazon Elastic Container Registry (ECR) with the main tag.

If no specific tags are provided for batch ingestion, the process defaults to using the `main` tag.


## Testing Changes in AWS Before Merging

To test changes in AWS before they are merged into the main branch, follow these steps:

### 1. Build and Push the Image Locally

You can build the image locally and push it to the remote ECR with a custom tag. Replace `<tag-for-build>` with your desired image tag.

```bash
make push-local-ingestor-build tag=<tag-for-build>
```

This will make the image available in AWS with the specified tag, which can be referenced by your test jobs.


### 2. Push an Already Built Image to AWS

If you've already built the image locally, you can simply push it to AWS by running the following command. Replace `<tag-for-build>`` with your tag, and `<aws-region>`` with the desired AWS region.

```bash
make push-ingestor-build tag=<tag-for-build> region=<aws-region>
```
Once this is done, your image will be available in AWS and ready for use in testing.

------------------

By following these steps, you can ensure that your changes are properly tested in a staging-like environment before they are merged into the main branch.