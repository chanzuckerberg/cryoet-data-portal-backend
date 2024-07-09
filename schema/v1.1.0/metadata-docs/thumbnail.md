

# Slot: thumbnail


_A placeholder for any type of data._



URI: [cdp-meta:thumbnail](metadatathumbnail)



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
| self | cdp-meta:thumbnail |
| native | cdp-meta:thumbnail |
| exact | cdp-common:thumbnail |




## LinkML Source

<details>
```yaml
name: thumbnail
description: A placeholder for any type of data.
from_schema: metadata
exact_mappings:
- cdp-common:thumbnail
rank: 1000
alias: thumbnail
owner: PicturePath
domain_of:
- PicturePath
range: Any
required: true
inlined: true
inlined_as_list: true

```
</details>