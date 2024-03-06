# Enum: SampleTypeEnum




_Type of sample imaged in a CryoET study._



URI: [SampleTypeEnum](SampleTypeEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| cell | None | Tomographic data of whole cells or cell sections |
| tissue | None | Tomographic data of tissue sections |
| organism | None | Tomographic data of sections through multicellular organisms |
| organelle | None | Tomographic data of purified organelles |
| virus | None | Tomographic data of purified viruses or VLPs |
| in_vitro | None | Tomographic data of in vitro reconstituted systems or mixtures of proteins |
| in_silico | None | Simulated tomographic data |
| other | None | Other type of sample |




## Slots

| Name | Description |
| ---  | --- |
| [sample_type](sample_type.md) | Type of sample imaged in a CryoET study |






## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: sample_type_enum
description: Type of sample imaged in a CryoET study.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
rank: 1000
permissible_values:
  cell:
    text: cell
    description: Tomographic data of whole cells or cell sections.
  tissue:
    text: tissue
    description: Tomographic data of tissue sections.
  organism:
    text: organism
    description: Tomographic data of sections through multicellular organisms.
  organelle:
    text: organelle
    description: Tomographic data of purified organelles.
  virus:
    text: virus
    description: Tomographic data of purified viruses or VLPs.
  in_vitro:
    text: in_vitro
    description: Tomographic data of in vitro reconstituted systems or mixtures of
      proteins.
  in_silico:
    text: in_silico
    description: Simulated tomographic data.
  other:
    text: other
    description: Other type of sample.

```
</details>
