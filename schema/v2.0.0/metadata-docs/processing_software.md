

# Slot: processing_software


_Processing software used to derive the tomogram_



URI: [cdp-meta:processing_software](metadataprocessing_software)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [String](String.md)

* Recommended: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:processing_software |
| native | cdp-meta:processing_software |
| exact | cdp-common:tomogram_processing_software |




## LinkML Source

<details>
```yaml
name: processing_software
description: Processing software used to derive the tomogram
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_processing_software
rank: 1000
alias: processing_software
owner: Tomogram
domain_of:
- Tomogram
range: string
recommended: true
inlined: true
inlined_as_list: true

```
</details>
