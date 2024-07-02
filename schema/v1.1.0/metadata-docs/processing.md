

# Slot: processing


_Describe additional processing used to derive the tomogram_



URI: [cdp-meta:processing](metadataprocessing)



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
| self | cdp-meta:processing |
| native | cdp-meta:processing |
| exact | cdp-common:tomogram_processing |




## LinkML Source

<details>
```yaml
name: processing
description: Describe additional processing used to derive the tomogram
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_processing
rank: 1000
alias: processing
owner: Tomogram
domain_of:
- Tomogram
range: string
inlined: true
inlined_as_list: true

```
</details>