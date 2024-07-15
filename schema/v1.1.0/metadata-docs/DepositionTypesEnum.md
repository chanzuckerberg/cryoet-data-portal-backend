# Enum: DepositionTypesEnum




_Types of data a deposition has_



URI: [DepositionTypesEnum](DepositionTypesEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| annotation | None | The deposition comprises of new annotations for existing datasets |
| datasets | None | The deposition comprises of new dataset(s) |
| tomograms | None | The deposition comprises of new tomograms for existing datasets |









## Identifier and Mapping Information







### Schema Source


* from schema: metadata






## LinkML Source

<details>
```yaml
name: deposition_types_enum
description: Types of data a deposition has
from_schema: metadata
rank: 1000
permissible_values:
  annotation:
    text: annotation
    description: The deposition comprises of new annotations for existing datasets
  datasets:
    text: datasets
    description: The deposition comprises of new dataset(s).
  tomograms:
    text: tomograms
    description: The deposition comprises of new tomograms for existing datasets

```
</details>
