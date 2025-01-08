# Finders

The finders components help the ingestion tool locate the items in the source location.
- They rely on the `sources` section of an entity's configuration.
- They return a list of the items found in the source location, which are each treated as a separate instance of the entity to be processed.

## Finder Factory

The `FinderFactory` class is responsible for creating the finders based on the configuration provided. They also handle the outcome of the finders and help in creating the instances of the entity to be processed.

The factory are configured using the `finder_factory` attribute specified for the importer.

The most commonly used finder factory is `DefaultFinderFactory`.

Some of the importers like the `AnnotationImporter`, `AlignmentImporter`, and `VoxelSpacingImporter` use a custom finder factory to handle the specific requirements of the importer.

<!-- TODO: Add more details about the finder factories -->

## Finders
The finders are the components that handle the logic of finding the items in the specified location.
Some of the commonly used finders are explained below.

### 1. source_glob
This is one of the most commonly used finders. It is used for entities such as tomograms, frames, tiltseries, etc.

- Allows you to specify a single glob pattern regex to find match in the source.
- Allows more filtering like optional regex match against file paths

**Example:**
```yaml
- sources:
    - source_glob:
        list_glob: ".*.mrc"
        match_regex: ".*"
        name_regex: "(.*)"
```

### 2. source_multi_glob
This is used when multiple different types of files can be related to an entity.
- Allows you to specify multiple glob pattern regex to find match in the source.
- No additional filtering is supported at the moment.

**Example:**
For example, in the case of alignments, you may have both `.xf` and `.tlt` files.:
```yaml
- sources:
    - source_glob:
        list_glob:
          - metadata/{run_name}.xf
          - metadata/{run_name}.tlt
```

### 3. destination_glob
This is used in depositions that require a reference to an existing entity in the destination.

- Allows you to specify a single glob pattern regex to find match in the destination.
- Allows more filtering like optional regex match against file paths

**Example:**
```yaml
- sources:
    - destination_glob:
        list_glob: '{run_output_path}/Reconstructions/VoxelSpacing*'
        match_regex: .*
        name_regex: VoxelSpacing(.*)
```

### 4. literal
This is used for entities like dataset or deposition that require only primitive values as input.

- Allows you to specify a value or a list of values as the output of the finders.

**Example:**
```yaml
- sources:
    - literal:
      value:
      - '10000'
```
