

# Slot: snapshot


_A placeholder for any type of data._



URI: [cdp-meta:snapshot](metadatasnapshot)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PicturePath](PicturePath.md) | A set of paths to representative images of a piece of data |  no  |







## Properties

* Range: [Any](Any.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:snapshot |
| native | cdp-meta:snapshot |
| exact | cdp-common:snapshot |




## LinkML Source

<details>
```yaml
name: snapshot
description: A placeholder for any type of data.
from_schema: metadata
exact_mappings:
- cdp-common:snapshot
rank: 1000
alias: snapshot
owner: PicturePath
domain_of:
- PicturePath
range: Any
required: true
inlined: true
inlined_as_list: true

```
</details>
