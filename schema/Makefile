.DEFAULT_GOAL := build

# include $CORE_VERSION, $API_VERSION, $INGESTION_CONFIG_VERSION
include .version

COMMON_YAML = core/$(CORE_VERSION)/common.yaml
METADATA_YAML = core/$(CORE_VERSION)/metadata.yaml
METADATA_MATERIALIZED_YAML = core/$(CORE_VERSION)/codegen/metadata_materialized.yaml
METADATA_MODELS_PY = core/$(CORE_VERSION)/codegen/metadata_models.py
METADATA_DOCS = core/$(CORE_VERSION)/metadata_docs/

API_MODELS_YAML = api/$(API_VERSION)/api_models.yaml
API_MODELS_MATERIALIZED_YAML = api/$(API_VERSION)/codegen/api_models_materialized.yaml

INGESTION_CONFIG_MODELS_YAML = ingestion_config/$(INGESTION_CONFIG_VERSION)/ingestion_config_models.yaml
INGESTION_CONFIG_MODELS_MATERIALIZED_YAML = ingestion_config/$(INGESTION_CONFIG_VERSION)/codegen/ingestion_config_models_materialized.yaml
INGESTION_CONFIG_MODELS_PY = ingestion_config/$(INGESTION_CONFIG_VERSION)/codegen/ingestion_config_models.py
INGESTION_CONFIG_JSON_SCHEMA = ingestion_config/$(INGESTION_CONFIG_VERSION)/codegen/ingestion_config_models.schema.json

VALIDATE_CONFIGS = ingestion_config/$(INGESTION_CONFIG_VERSION)/ingestion_config_validate.py

.PHONY: clean
clean:
	rm -rf $(METADATA_MATERIALIZED_YAML)
	rm -rf $(METADATA_MODELS_PY)
	rm -rf $(API_MODELS_MATERIALIZED_YAML)
	rm -rf $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML)
	rm -rf $(INGESTION_CONFIG_MODELS_PY)
	rm -rf $(INGESTION_CONFIG_JSON_SCHEMA)
	rm -rf ingestion_config/latest

.PHONY: clean-all
clean-all: CORE_VERSION=*
clean-all: API_VERSION=*
clean-all: INGESTION_CONFIG_VERSION=*
clean-all: clean

.PHONY: clean-docs
clean-docs:
	rm -rf $(METADATA_DOCS)

.PHONY: build
build: clean
	python schema.py materialize $(METADATA_YAML) $(COMMON_YAML) $(METADATA_MATERIALIZED_YAML)
	python schema.py materialize $(API_MODELS_YAML) $(COMMON_YAML) $(API_MODELS_MATERIALIZED_YAML)
	python schema.py materialize $(INGESTION_CONFIG_MODELS_YAML) $(COMMON_YAML) $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML)
	gen-pydantic --black $(METADATA_MATERIALIZED_YAML) > $(METADATA_MODELS_PY)
	gen-pydantic --black $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML) > $(INGESTION_CONFIG_MODELS_PY)
	gen-json-schema $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML) > $(INGESTION_CONFIG_JSON_SCHEMA)
	cd ingestion_config && ln -s $(INGESTION_CONFIG_VERSION) latest && cd ..

# `make build` must be run before `make build-docs`
.PHONY: build-docs
build-docs: clean-docs
	gen-doc -d $(METADATA_DOCS) --no-mergeimports --hierarchical-class-view --stacktrace $(METADATA_MATERIALIZED_YAML)

.PHONY: validate-configs
validate-configs:
	python $(VALIDATE_CONFIGS)

.PHONY: validate-configs-with-network
validate-configs-with-network:
	python $(VALIDATE_CONFIGS) --network-validation
