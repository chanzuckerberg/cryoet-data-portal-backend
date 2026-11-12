.DEFAULT_GOAL := build

# include $CORE_VERSION, $INGESTION_CONFIG_VERSION, $METADATA_FILES_VERSION, $DCA_METADATA_VERSION
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

METADATA_FILES_MODELS_YAML = metadata_files/$(METADATA_FILES_VERSION)/metadata_files.yaml
METADATA_FILES_MODELS_MATERIALIZED_YAML = metadata_files/$(METADATA_FILES_VERSION)/codegen/metadata_files_materialized.yaml
METADATA_FILES_MODELS_PY = metadata_files/$(METADATA_FILES_VERSION)/codegen/metadata_files.py
METADATA_FILES_JSON_SCHEMA = metadata_files/$(METADATA_FILES_VERSION)/codegen/metadata_files.schema.json

# The dca block in the zarr.json of images ingested with --dca (cryoET storage profile). Its generated JSON Schema is
# also copied into ingestion_tools, because the ingestor image only contains ingestion_tools/; check_profile validates
# against that copy. Regenerate both with `make build-dca-metadata` and commit them.
DCA_METADATA_YAML = dca_metadata/$(DCA_METADATA_VERSION)/dca_metadata.yaml
DCA_METADATA_JSON_SCHEMA = dca_metadata/$(DCA_METADATA_VERSION)/codegen/dca_metadata.schema.json
DCA_METADATA_INGESTION_COPY = ../ingestion_tools/scripts/common/codegen/dca_metadata.schema.json

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

.PHONY: clean-metadata-files
clean-metadata-files:
	rm -f $(METADATA_MODELS_PY)
	rm -f $(METADATA_FILES_MODELS_MATERIALIZED_YAML)
	rm -f $(METADATA_FILES_MODELS_PY)
	rm -f $(METADATA_FILES_JSON_SCHEMA)

.PHONY: clean-dca-metadata
clean-dca-metadata:
	rm -f $(DCA_METADATA_JSON_SCHEMA)

.PHONY: clean-docs
clean-docs:
	rm -rf $(METADATA_DOCS)

.PHONY: clean
clean:
	make clean-core CORE_VERSION=$(CORE_VERSION)
	make clean-ingestion-config INGESTION_CONFIG_VERSION=$(INGESTION_CONFIG_VERSION)
	make clean-metadata-files METADATA_FILES_VERSION=$(METADATA_FILES_VERSION)
	make clean-dca-metadata DCA_METADATA_VERSION=$(DCA_METADATA_VERSION)

.PHONY: clean-all
clean-all: CORE_VERSION=*
clean-all: INGESTION_CONFIG_VERSION=*
clean-all: METADATA_FILES_VERSION=*
clean-all: DCA_METADATA_VERSION=*
clean-all: clean
	rm -rf ingestion_config/latest

.PHONY: build
build: build-ingestion-config build-metadata-files build-dca-metadata

# To build-ingestion-config for the non-default version, run `make build-ingestion-config INGESTION_CONFIG_VERSION=v2.0.0 CORE_VERSION=v2.0.0`
.PHONY: build-ingestion-config
build-ingestion-config: clean-core clean-ingestion-config
	python3 schema.py materialize $(METADATA_YAML) $(COMMON_YAML) $(METADATA_MATERIALIZED_YAML)
	python3 schema.py materialize $(INGESTION_CONFIG_MODELS_YAML) $(COMMON_YAML) $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML)

	linkml generate pydantic --black $(METADATA_MATERIALIZED_YAML) > $(METADATA_MODELS_PY)
	linkml generate pydantic $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML) > $(INGESTION_CONFIG_MODELS_PY)
	linkml generate json-schema $(INGESTION_CONFIG_MODELS_MATERIALIZED_YAML) > $(INGESTION_CONFIG_JSON_SCHEMA)
	cd ingestion_config && ln -sf $(INGESTION_CONFIG_VERSION) latest && cd ..

# To build-ingestion-config for the non-default version, run `make build-ingestion-config INGESTION_CONFIG_VERSION=v2.0.0 CORE_VERSION=v2.0.0`
.PHONY: build-metadata-files
build-metadata-files:
	python3 schema.py materialize $(METADATA_YAML) $(COMMON_YAML) $(METADATA_MATERIALIZED_YAML)
	python3 schema.py materialize $(METADATA_FILES_MODELS_YAML) $(COMMON_YAML) $(METADATA_FILES_MODELS_MATERIALIZED_YAML)

	linkml generate pydantic --black $(METADATA_MATERIALIZED_YAML) > $(METADATA_MODELS_PY)
	linkml generate pydantic $(METADATA_FILES_MODELS_MATERIALIZED_YAML) > $(METADATA_FILES_MODELS_PY)
	linkml generate json-schema $(METADATA_FILES_MODELS_MATERIALIZED_YAML) > $(METADATA_FILES_JSON_SCHEMA)
	cd ingestion_config && ln -sf $(METADATA_FILES_VERSION) latest && cd ..

.PHONY: build-dca-metadata
build-dca-metadata: clean-dca-metadata
	mkdir -p $(dir $(DCA_METADATA_JSON_SCHEMA)) $(dir $(DCA_METADATA_INGESTION_COPY))
	# end the file with a single newline, as pre-commit's end-of-file-fixer requires
	linkml generate json-schema $(DCA_METADATA_YAML) \
		| python3 -c "import sys; sys.stdout.write(sys.stdin.read().rstrip() + chr(10))" > $(DCA_METADATA_JSON_SCHEMA)
	cp $(DCA_METADATA_JSON_SCHEMA) $(DCA_METADATA_INGESTION_COPY)

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

.PHONY: validate-changed-configs-with-network
validate-changed-configs-with-network:
	python $(VALIDATE_CONFIGS) $(CHANGED_FILES) --network-validation --verbose
