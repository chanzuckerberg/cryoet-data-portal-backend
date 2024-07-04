

# Slot: tomogram_version


_Version of tomogram_



URI: [cdp-meta:tomogram_version](metadatatomogram_version)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [VersionString](VersionString.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:tomogram_version |
| native | cdp-meta:tomogram_version |
| exact | cdp-common:tomogram_version |




## LinkML Source

<details>
```yaml
name: tomogram_version
description: Version of tomogram
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_version
rank: 1000
alias: tomogram_version
owner: Tomogram
domain_of:
- Tomogram
range: VersionString
required: true
inlined: true
inlined_as_list: true

```
</details>