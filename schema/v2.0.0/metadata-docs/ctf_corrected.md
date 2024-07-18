

# Slot: ctf_corrected


_Whether this tomogram is CTF corrected_



URI: [cdp-meta:ctf_corrected](metadatactf_corrected)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [Boolean](Boolean.md)

* Recommended: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:ctf_corrected |
| native | cdp-meta:ctf_corrected |
| exact | cdp-common:tomogram_ctf_corrected |




## LinkML Source

<details>
```yaml
name: ctf_corrected
description: Whether this tomogram is CTF corrected
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_ctf_corrected
rank: 1000
alias: ctf_corrected
owner: Tomogram
domain_of:
- Tomogram
range: boolean
recommended: true
inlined: true
inlined_as_list: true

```
</details>
