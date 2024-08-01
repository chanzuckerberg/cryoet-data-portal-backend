.DEFAULT_GOAL := build

# include $CORE_VERSION, $API_VERSION, $DATASET_CONFIG_VERSION
include .version

COMMON_YAML = core/$(CORE_VERSION)/common.yaml
METADATA_YAML = core/$(CORE_VERSION)/metadata.yaml
METADATA_MATERIALIZED_YAML = core/$(CORE_VERSION)/codegen/metadata_materialized.yaml
METADATA_MODELS_PY = core/$(CORE_VERSION)/codegen/metadata_models.py
METADATA_DOCS = core/$(CORE_VERSION)/metadata_docs/

API_MODELS_YAML = api/$(API_VERSION)/api_models.yaml
API_MODELS_MATERIALIZED_YAML = api/$(API_VERSION)/codegen/api_models_materialized.yaml

DATASET_CONFIG_MODELS_YAML = dataset_config/$(DATASET_CONFIG_VERSION)/dataset_config_models.yaml
DATASET_CONFIG_MODELS_MATERIALIZED_YAML = dataset_config/$(DATASET_CONFIG_VERSION)/codegen/dataset_config_models_materialized.yaml
DATASET_CONFIG_MODELS_PY = dataset_config/$(DATASET_CONFIG_VERSION)/codegen/dataset_config_models.py
DATASET_CONFIG_JSON_SCHEMA = dataset_config/$(DATASET_CONFIG_VERSION)/codegen/dataset_config_models.schema.json

VALIDATE_CONFIGS = dataset_config/$(DATASET_CONFIG_VERSION)/dataset_config_validate.py

.PHONY: clean
clean:
	rm -rf $(METADATA_DOCS)
	rm -rf $(METADATA_MATERIALIZED_YAML)
	rm -rf $(METADATA_MODELS_PY)
	rm -rf $(API_MODELS_MATERIALIZED_YAML)
	rm -rf $(DATASET_CONFIG_MODELS_MATERIALIZED_YAML)
	rm -rf $(DATASET_CONFIG_MODELS_PY)
	rm -rf $(DATASET_CONFIG_JSON_SCHEMA)

.PHONY: clean-all
clean-all: CORE_VERSION=*
clean-all: API_VERSION=*
clean-all: DATASET_CONFIG_VERSION=*
clean-all: clean

.PHONY: build
build: clean
	python schema.py materialize $(METADATA_YAML) $(COMMON_YAML) $(METADATA_MATERIALIZED_YAML)
	python schema.py materialize $(API_MODELS_YAML) $(COMMON_YAML) $(API_MODELS_MATERIALIZED_YAML)
	python schema.py materialize $(DATASET_CONFIG_MODELS_YAML) $(COMMON_YAML) $(DATASET_CONFIG_MODELS_MATERIALIZED_YAML)
	gen-doc -d $(METADATA_DOCS) --no-mergeimports --hierarchical-class-view --stacktrace $(METADATA_MATERIALIZED_YAML)
	gen-pydantic --black $(METADATA_MATERIALIZED_YAML) > $(METADATA_MODELS_PY)
	gen-pydantic --black $(DATASET_CONFIG_MODELS_MATERIALIZED_YAML) > $(DATASET_CONFIG_MODELS_PY)
	gen-json-schema $(DATASET_CONFIG_MODELS_MATERIALIZED_YAML) > $(DATASET_CONFIG_JSON_SCHEMA)

.PHONY: validate-configs
validate-configs:
	python $(VALIDATE_CONFIGS)

.PHONY: validate-configs-with-network
validate-configs-with-network:
	python $(VALIDATE_CONFIGS) --network-validation
