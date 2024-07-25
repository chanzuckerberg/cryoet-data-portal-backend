# Enum: TomogramProcessingEnum




_Tomogram processing method_



URI: [TomogramProcessingEnum](TomogramProcessingEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| denoised | None | Tomogram was denoised |
| filtered | None | Tomogram was filtered |
| raw | None | Tomogram was not processed |




## Slots

| Name | Description |
| ---  | --- |
| [processing](processing.md) | Describe additional processing used to derive the tomogram |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata






## LinkML Source

<details>
```yaml
name: tomogram_processing_enum
description: Tomogram processing method
from_schema: metadata
rank: 1000
permissible_values:
  denoised:
    text: denoised
    description: Tomogram was denoised
  filtered:
    text: filtered
    description: Tomogram was filtered
  raw:
    text: raw
    description: Tomogram was not processed

```
</details>
