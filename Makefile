export docker_compose:=docker compose -f ./docker-compose.yml -f ./ingestion_tools/docker-compose.yml

.PHONY: init
init: ingestor-init apiv2-init

.PHONY: stop
stop:
	$(docker_compose) --profile '*' stop

.PHONY: build
build:
	$(docker_compose) --profile '*' build $(image)

.PHONY: start
start:
	$(docker_compose) --profile ingestor start

.PHONY: ingestor-init
ingestor-init:
	$(docker_compose) --profile ingestor up -d
	cd ./test_infra/; ./seed_moto.sh

.PHONY: apiv2-init
apiv2-init:
	docker compose --profile apiv2 up -d
	cd ./test_infra/; ./seed_moto.sh
	$(MAKE) -C apiv2 alembic-upgrade-head

.PHONY: clean
clean:
	$(docker_compose) --profile '*' down

.PHONY: ingestor-test-s3
ingestor-test-s3:
	docker compose exec ingestor pytest -vvv -s . -k s3_import

.PHONY: apiv2-test
apiv2-test:  ## Run apiv2 tests
	$(docker_compose) exec graphql-api pytest -vvv

.PHONY: push-local-ingestor-build
push-local-ingestor-build:
	aws_region=$$(aws configure get region); \
	account_id=$$(aws sts get-caller-identity | jq -r ".Account"); \
	ecr_repo=$$account_id.dkr.ecr.$$aws_region.amazonaws.com; \
	$(MAKE) push-ingestor-build ecr_repo=$$ecr_repo/cryoet-staging tag=$(tag) aws_region=$$aws_region; \
	$(MAKE) push-ingestor-build-apiv2 ecr_repo=$$ecr_repo/apiv2-x86 tag=$(tag) aws_region=$$aws_region;

.PHONY: push-ingestor-build
push-ingestor-build:
	cd ./ingestion_tools/; docker build . -t $(ecr_repo):$(tag) --platform linux/amd64;
	aws ecr get-login-password --region $(aws_region) | docker login --username AWS --password-stdin $(ecr_repo); \
	docker push $(ecr_repo):$(tag);

.PHONY: push-ingestor-build-apiv2
push-ingestor-build-apiv2:
	cd ./apiv2/; docker build . -t $(ecr_repo):$(tag) --platform linux/amd64;
	aws ecr get-login-password --region $(aws_region) | docker login --username AWS --password-stdin $(ecr_repo); \
	docker push $(ecr_repo):$(tag);

.PHONY: db-import-dataset
db-import-dataset:
	AWS_PROFILE=cryoet-dev aws-oidc exec -- docker run --rm=true -v $$PWD/apiv2:/app -e AWS_REGION -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN -e AWS_DEFAULT_OUTPUT --network cryoback_default -ti graphql-api python3 -m db_import.importer load --s3-prefix 10001 --import-everything --postgres_url postgresql+psycopg://postgres:postgres@db:5432/cryoetv2 cryoet-data-portal-public http://localhost:8000  --import-depositions --deposition-id 10301 --deposition-id 10303

.PHONY: update-api-schema
update-api-schema:
	$(MAKE) -C apiv2 update-schema
	pre-commit run --all-files
