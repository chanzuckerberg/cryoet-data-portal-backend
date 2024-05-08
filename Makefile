export docker_compose:=docker compose -f ./docker-compose.yml -f ./ingestion_tools/docker-compose.yml

.PHONY: init
init: ingestor-init api-init

.PHONY: stop
stop:
	$(docker_compose) --profile '*' stop

.PHONY: start
start:
	$(docker_compose) --profile ingestor start

.PHONY: ingestor-init
ingestor-init:
	$(docker_compose) --profile ingestor up -d
	cd ./test_infra/; ./seed_moto.sh

.PHONY: api-init
api-init:
	docker compose --profile api up -d
	cd ./test_infra/; ./seed_moto.sh
	docker compose cp test_infra/sql db:/tmp/sql
	docker compose exec db sh -c 'cat /tmp/sql/seed_db_data.sql | psql postgres://postgres:postgres@127.0.0.1:5432/cryoet'

.PHONY: clean
clean:
	$(docker_compose) --profile '*' down

.PHONY: ingestor-test-db-init
ingestor-test-db-init:
	docker compose up db -d
	docker compose cp test_infra/sql db:/tmp/sql
	docker compose exec db sh -c 'cat /tmp/sql/schema.sql | psql postgres://postgres:postgres@127.0.0.1:5432/cryoet'
	docker compose exec db sh -c 'cat /tmp/sql/seed_db_enum.sql | psql postgres://postgres:postgres@127.0.0.1:5432/cryoet'

.PHONY: ingestor-test-db
ingestor-test-db:
	docker compose exec ingestor pytest -vvv -s . -k db_import

.PHONY: ingestor-test-s3
ingestor-test-s3:
	docker compose exec ingestor pytest -vvv -s . -k s3_import

.PHONY: push-local-ingestor-build
push-local-ingestor-build:
	aws_region=$$(aws configure get region); \
	account_id=$$(aws sts get-caller-identity | jq -r ".Account"); \
	ecr_repo=$$account_id.dkr.ecr.$$aws_region.amazonaws.com; \
	aws ecr get-login-password --region $$aws_region | docker login --username AWS --password-stdin $$ecr_repo; \
	make push-ingestor-build ecr_repo=$$ecr_repo/cryoet-staging tag=$(tag);

.PHONY: push-ingestor-build
push-ingestor-build:
	cd ./ingestion_tools/; docker build . -t $(ecr_repo):$(tag) --platform linux/amd64;
	docker push $(ecr_repo):$(tag);
