.DEFAULT_GOAL := build

# include $CORE_VERSION, $INGESTION_CONFIG_VERSION
include .version

COMMON_YAML = core/$(CORE_VERSION)/common.yaml
METADATA_YAML = core/$(CORE_VERSION)/metadata.yaml
METADATA_MATERIALIZED_YAML = core/$(CORE_VERSION)/codegen/metadata_materialized.yaml
METADATA_MODELS_PY = core/$(CORE_VERSION)/codegen/metadata_models.py
METADATA_DOCS = core/$(CORE_VERSION)/metadata_docs/

INGESTION_CONFIG_MODELS_YAML = ingestion_config/$(INGESTION_CONFIG_VERSION)/ingestion_config_models.yaml
INGESTION_CONFIG_MODELS_MATERIALIZED_YAML = ingestion_config/$(INGESTION_CONFIG_VERSION)/codegen/ingestion_config_models_materialized.yaml
INGESTION_CONFIG_MODELS_PY = ingestion_config/$(INGESTION_CONFIG_VERSION)/codegen/ingestion_config_models.py
INGESTION_CONFIG_JSON_SCHEMA = ingestion_config/$(INGESTION_CONFIG_VERSION)/codegen/ingestion_config_models.schema.json

VALIDATE_CONFIGS = ingestion_config/$(INGESTION_CONFIG_VERSION)/ingestion_config_validate.py

.PHONY: clean-core
clean-core:
	rm -f $(METADATA_MATERIALIZED_YAML)

.PHONY: clean-ingestion-config
clean-ingestion-config:
	rm -f $(METADATA_MODELS_PY)
	rm -f $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML)
	rm -f $(INGESTION_CONFIG_MODELS_PY)
	rm -f $(INGESTION_CONFIG_JSON_SCHEMA)

.PHONY: clean-docs
clean-docs:
	rm -rf $(METADATA_DOCS)

.PHONY: clean
clean:
	make clean-core CORE_VERSION=$(CORE_VERSION)
	make clean-ingestion-config INGESTION_CONFIG_VERSION=$(INGESTION_CONFIG_VERSION)

.PHONY: clean-all
clean-all: CORE_VERSION=*
clean-all: INGESTION_CONFIG_VERSION=*
clean-all: clean
	rm -rf ingestion_config/latest

.PHONY: build
build: build-ingestion-config

# To build-ingestion-config for the non-default version, run `make build-ingestion-config INGESTION_CONFIG_VERSION=v2.0.0 CORE_VERSION=v2.0.0`
.PHONY: build-ingestion-config
build-ingestion-config: clean-core clean-ingestion-config
	python3 schema.py materialize $(METADATA_YAML) $(COMMON_YAML) $(METADATA_MATERIALIZED_YAML)
	python3 schema.py materialize $(INGESTION_CONFIG_MODELS_YAML) $(COMMON_YAML) $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML)

# Have to explicitly set `--meta AUTO`, see https://github.com/linkml/linkml/issues/2685; fixed in linkml 1.9.3 (but still in pre-release)
	linkml generate pydantic --black $(METADATA_MATERIALIZED_YAML) --meta AUTO > $(METADATA_MODELS_PY)
	linkml generate pydantic $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML) --meta AUTO > $(INGESTION_CONFIG_MODELS_PY)
	linkml generate json-schema $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML) > $(INGESTION_CONFIG_JSON_SCHEMA)
	cd ingestion_config && ln -sf $(INGESTION_CONFIG_VERSION) latest && cd ..

# `make build` must be run before `make build-docs`
.PHONY: build-docs
build-docs: clean-docs
	linkml generate doc -d $(METADATA_DOCS) --no-mergeimports --hierarchical-class-view --stacktrace $(METADATA_MATERIALIZED_YAML)

.PHONY: validate-configs
validate-configs:
	python $(VALIDATE_CONFIGS)

.PHONY: validate-configs-with-network
validate-configs-with-network:
	python $(VALIDATE_CONFIGS) --network-validation --verbose
