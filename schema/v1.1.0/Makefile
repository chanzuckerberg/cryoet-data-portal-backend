.DEFAULT_GOAL := build

.PHONY: clean
clean:
	rm -rf metadata-docs
	rm -rf metadata_materialized.yaml
	rm -rf dataset_config_materialized.yaml
	rm -rf metadata_models.py
	rm -rf dataset_config_models.py

.PHONY: build
build:
	python schema.py materialize metadata.yaml common.yaml metadata_materialized.yaml
	python schema.py materialize dataset_config.yaml common.yaml dataset_config_materialized.yaml
	gen-doc -d metadata-docs --no-mergeimports --hierarchical-class-view --stacktrace metadata_materialized.yaml
	gen-pydantic --pydantic-version 2 --black metadata_materialized.yaml > metadata_models.py
	gen-pydantic --pydantic-version 2 --black dataset_config_materialized.yaml > dataset_config_models.py
	gen-json-schema dataset_config_materialized.yaml > dataset_config_models.schema.json

.PHONY: validate-configs
validate-configs:
	python dataset_config_validate.py

.PHONY: validate-configs-with-network
validate-configs-with-network:
	python dataset_config_validate.py --network-validation
