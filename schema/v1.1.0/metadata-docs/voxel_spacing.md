

# Slot: voxel_spacing


_Voxel spacing equal in all three axes in angstroms_



URI: [cdp-meta:voxel_spacing](metadatavoxel_spacing)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md)&nbsp;or&nbsp;<br />[FloatFormattedString](FloatFormattedString.md)

* Minimum Value: 0

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:voxel_spacing |
| native | cdp-meta:voxel_spacing |




## LinkML Source

<details>
```yaml
name: voxel_spacing
description: Voxel spacing equal in all three axes in angstroms
from_schema: metadata
rank: 1000
alias: voxel_spacing
owner: Tomogram
domain_of:
- Tomogram
range: string
inlined: true
inlined_as_list: true
minimum_value: 0.001
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
unit:
  symbol: Å/voxel
  descriptive_name: Angstroms per voxel
any_of:
- range: float
  minimum_value: 0.001
- range: FloatFormattedString

```
</details>
