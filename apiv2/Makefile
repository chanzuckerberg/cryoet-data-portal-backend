SHELL := /bin/bash

FOLDER = /app
APP_CONTAINER=graphql-api

### DATABASE VARIABLES #################################################
LOCAL_DB_NAME=cryoetv2
LOCAL_DB_SERVER=db:5432
LOCAL_DB_USERNAME=postgres
LOCAL_DB_PASSWORD=postgres
LOCAL_DB_CONN_STRING = postgresql://$(LOCAL_DB_USERNAME):$(LOCAL_DB_PASSWORD)@$(LOCAL_DB_SERVER)/$(LOCAL_DB_NAME)

### DOCKER ENV VARS #################################################
export DOCKER_BUILDKIT:=1
export COMPOSE_DOCKER_CLI_BUILD:=1
export docker_compose:=docker compose
# IMPORTANT!! VSCode's support for devcontainers is pretty dependent on NOT
# having a bunch of old `docker compose run` containers laying around. It basically
# just hangs on OSX trying to launch itself in a container if it can't figure out
# which one to use, so it's *VERY* important to include the --rm flag when invoking
# docker compose run.
export docker_compose_run:=docker compose run --rm

### HELPFUL #################################################
.PHONY: help
help: ## display help for this makefile
	@echo "### SHARED FUNCTIONS ###"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo "### SHARED FUNCTIONS END ###"

### DOCKER LOCAL DEV #########################################
.PHONY: build
build: ## Build docker containers
	rm -rf dist/*.whl
	$(docker_compose) build

.PHONY: update-schema
update-schema: codegen alembic-autogenerate alembic-upgrade-head
	# $(docker_compose_run) $(CONTAINER) ruff check --fix .
	$(docker_compose_run) $(APP_CONTAINER) sh -c 'strawberry export-schema main:schema > /app/graphql_api/schema.graphql'
	linkml generate erdiagram --structural --classes Alignment --classes AnnotationAuthor --classes AnnotationFile --classes AnnotationShape --classes Annotation --classes DatasetAuthor --classes DatasetFunding --classes Dataset --classes DepositionAuthor --classes Deposition --classes Frame --classes PerSectionAlignmentParameters --classes PerSectionParameters --classes Run --classes Tiltseries --classes TomogramAuthor --classes TomogramVoxelSpacing --classes Tomogram schema/schema.yaml> schema/README.md
	docker compose up -d
	sleep 5 # wait for the app to reload after having files updated.
	docker compose exec $(APP_CONTAINER) python3 -m sgqlc.introspection --exclude-deprecated --exclude-description http://localhost:9009/graphql graphql_api/schema.json

.PHONY: seed-moto
seed-moto: ## Seed the moto db by running the ./bin/seed_moto.sh script
	touch .moto_recording
	./bin/seed_moto.sh

.PHONY: clean
clean: ## Remove all codegen'd artifacts.
	$(docker_compose) --profile '*' down

.PHONY: start
start: ## Start the local dev environment.
	$(docker_compose) up -d

.PHONY: codegen
codegen: ## Run codegen to convert the LinkML schema to a GQL API
	$(docker_compose_run) $(APP_CONTAINER) python3 -m platformics.cli.main api generate --template-override-paths ./template_overrides --schemafile ./schema/schema.yaml --skip-render-files --output-prefix .
	$(docker_compose_run) $(APP_CONTAINER) black .

.PHONY: test
test: ## Run tests
	$(docker_compose) exec $(APP_CONTAINER) pytest -vvv

.PHONY: test-file
test-file: init ## Run tests for a specific file, ex: make test-file FILE=tests/test_file.py
	$(docker_compose) exec $(APP_CONTAINER) pytest -vvv $(FILE)

.PHONY: restart
restart: ## Restart the GQL service
	$(docker_compose_run) $(APP_CONTAINER) supervisorctl restart graphql_api

.PHONY: stop
stop: ## Stop the local dev environment.
	$(docker_compose) --profile '*' stop

.PHONY: seed
seed: ## Seed the dev db with a reasonable set of starting data.
	$(docker_compose) exec $(APP_CONTAINER) python3 scripts/seed.py

.PHONY: pgconsole
pgconsole: ## Connect to the local postgres database.
	$(docker_compose) exec db psql "$(LOCAL_DB_CONN_STRING)"

.PHONY: logs
logs: ## Tail the logs of the dev env containers. ex: make logs CONTAINER=graphql-api
	$(docker_compose) logs -f $(CONTAINER)

.PHONY: token
token: ## Copy an auth token for this local dev env to the system clipboard
	TOKEN=$$($(docker_compose_run) $(APP_CONTAINER) python3 -m platformics.cli.main auth generate-token 111 --project 444:owner --expiration 99999); echo '{"Authorization":"Bearer '$$TOKEN'"}' | tee >(pbcopy)

.PHONY: update-cli
update-cli:  ## Update the GQL types used by the CLI
	$(docker_compose) exec $(APP_CONTAINER) python3 -m sgqlc.introspection --exclude-deprecated --exclude-description http://localhost:8042/graphql graphql_api/schema.json
	$(docker_compose) exec $(APP_CONTAINER) sgqlc-codegen schema graphql_api/schema.json cli/gql_schema.py

.PHONY: fix-poetry-lock
fix-poetry-lock: ## Fix poetry lockfile after merge conflict & repairing pyproject.toml
	git checkout --theirs poetry.lock
	$(docker_compose_run) $(APP_CONTAINER) poetry lock --no-update

.PHONY: update-python-deps
update-python-deps: ## Update poetry.lock to reflect pyproject.toml file changes.
	$(docker_compose) exec $(APP_CONTAINER) poetry update


### ALEMBIC #############################################
.PHONY: alembic-upgrade-head
alembic-upgrade-head: ## Run alembic migrations locally
	$(docker_compose_run) $(APP_CONTAINER) alembic upgrade head

.PHONY: alembic-undo-migration
alembic-undo-migration: ## Downgrade the latest alembic migration
	$(docker_compose_run) $(APP_CONTAINER) alembic downgrade -1

.PHONY: alembic-autogenerate
alembic-autogenerate: ## Create new alembic migrations files based on SA schema changes.
	$(docker_compose_run) $(APP_CONTAINER) alembic revision --autogenerate -m "autogenerated" --rev-id $$(date +%Y%m%d_%H%M%S)
