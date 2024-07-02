

# Slot: reconstruction_method


_Describe reconstruction method (Weighted back-projection, SART, SIRT)_



URI: [cdp-meta:reconstruction_method](metadatareconstruction_method)



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
| self | cdp-meta:reconstruction_method |
| native | cdp-meta:reconstruction_method |
| exact | cdp-common:tomogram_reconstruction_method |




## LinkML Source

<details>
```yaml
name: reconstruction_method
description: Describe reconstruction method (Weighted back-projection, SART, SIRT)
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_reconstruction_method
rank: 1000
alias: reconstruction_method
owner: Tomogram
domain_of:
- Tomogram
range: string
inlined: true
inlined_as_list: true

```
</details>