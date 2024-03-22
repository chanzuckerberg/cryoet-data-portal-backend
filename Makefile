.PHONY: init
init: ingestor-init api-init

.PHONY: ingestor-init
ingestor-init:
	docker compose -f ./docker-compose.yml -f ./ingestion_tools/docker-compose.yml --profile ingestor up -d
	cd ./test_infra/; ./seed_moto.sh

.PHONY: api-init
api-init:
	docker compose --profile api up -d
	cd ./test_infra/; ./seed_moto.sh
	docker compose cp test_infra/seed_db_data.sql db:/tmp/seed_db_data.sql
	docker compose exec db sh -c 'cat /tmp/seed_db_data.sql | psql postgres://postgres:postgres@127.0.0.1:5432/cryoet'

.PHONY: clean
clean:
	docker compose --profile '*' down

.PHONY: ingestor-test-db-init
ingestor-test-db-init:
	# Starting up cryoet-api ensures we are running the test against the latest schema
	docker compose up db cryoet-api -d

.PHONY: ingestor-test-db
ingestor-test-db:
	docker compose exec ingestor pytest -vvv -s . -k db_import

.PHONY: ingestor-test-s3
ingestor-test-s3:
	docker compose exec ingestor pytest -vvv -s . -k s3_import
