# Slot: voxel_spacing


_Voxel spacing equal in all three axes in angstroms_



URI: [cdp-meta:voxel_spacing](https://cryoetdataportal.czscience.com/schema/metadata/voxel_spacing)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [xsd:float](http://www.w3.org/2001/XMLSchema#float)





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: voxel_spacing
description: Voxel spacing equal in all three axes in angstroms
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
exact_mappings:
- cdp-common:tomogram_voxel_spacing
rank: 1000
alias: voxel_spacing
owner: Tomogram
domain_of:
- Tomogram
range: float
inlined: true
inlined_as_list: true

```
</details>