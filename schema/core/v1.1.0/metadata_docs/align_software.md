

# Slot: align_software


_Software used for alignment_



URI: [cdp-meta:align_software](metadataalign_software)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:align_software |
| native | cdp-meta:align_software |
| exact | cdp-common:tomogram_align_software |




## LinkML Source

<details>
```yaml
name: align_software
description: Software used for alignment
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_align_software
rank: 1000
alias: align_software
owner: Tomogram
domain_of:
- Tomogram
range: string
inlined: true
inlined_as_list: true

```
</details>
