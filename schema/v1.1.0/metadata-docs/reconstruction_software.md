

# Slot: reconstruction_software


_Name of software used for reconstruction_



URI: [cdp-meta:reconstruction_software](metadatareconstruction_software)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [String](String.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:reconstruction_software |
| native | cdp-meta:reconstruction_software |
| exact | cdp-common:tomogram_reconstruction_software |




## LinkML Source

<details>
```yaml
name: reconstruction_software
description: Name of software used for reconstruction
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_reconstruction_software
rank: 1000
alias: reconstruction_software
owner: Tomogram
domain_of:
- Tomogram
range: string
required: true
inlined: true
inlined_as_list: true

```
</details>