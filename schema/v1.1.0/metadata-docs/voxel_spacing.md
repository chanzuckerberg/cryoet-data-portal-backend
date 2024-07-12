# Slot: voxel_spacing


_Voxel spacing equal in all three axes in angstroms_



URI: [cdp-meta:voxel_spacing](metadatavoxel_spacing)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [Float](Float.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: voxel_spacing
description: Voxel spacing equal in all three axes in angstroms
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_voxel_spacing
rank: 1000
alias: voxel_spacing
owner: Tomogram
domain_of:
- Tomogram
range: float
required: true
inlined: true
inlined_as_list: true
unit:
  symbol: Å/voxel
  descriptive_name: Angstroms per voxel

```
</details>
