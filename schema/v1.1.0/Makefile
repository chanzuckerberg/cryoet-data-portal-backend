.DEFAULT_GOAL := build

.PHONY: clean
clean:
	rm -rf metadata-docs
	rm -rf metadata_materialized.yaml
	rm -rf metadata_models.py

.PHONY: build
build:
	python3 schema.py materialize metadata.yaml common.yaml metadata_materialized.yaml
	gen-doc -d metadata-docs --no-mergeimports  --hierarchical-class-view --stacktrace metadata_materialized.yaml
	gen-pydantic --pydantic-version 2 metadata_materialized.yaml > metadata_models.py
	black -l 88 metadata_models.py
