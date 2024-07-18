# Enum: DepositionTypesEnum




_Types of data a deposition has_



URI: [DepositionTypesEnum](DepositionTypesEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| annotation | None | The deposition comprises of new annotations for existing datasets |
| dataset | None | The deposition comprises of new dataset(s) |
| tomogram | None | The deposition comprises of new tomograms for existing datasets |




## Slots

| Name | Description |
| ---  | --- |
| [deposition_types](deposition_types.md) | Type of data in the deposition (e |






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
  dataset:
    text: dataset
    description: The deposition comprises of new dataset(s).
  tomogram:
    text: tomogram
    description: The deposition comprises of new tomograms for existing datasets

```
</details>
