

# Slot: thumbnail


_Path to the thumbnail of preview image relative to the dataset directory root._



URI: [cdp-meta:thumbnail](metadatathumbnail)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PicturePath](PicturePath.md) | A set of paths to representative images of a piece of data |  no  |







## Properties

* Range: [URLorS3URI](URLorS3URI.md)

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
description: Path to the thumbnail of preview image relative to the dataset directory
  root.
from_schema: metadata
exact_mappings:
- cdp-common:thumbnail
rank: 1000
alias: thumbnail
owner: PicturePath
domain_of:
- PicturePath
range: URLorS3URI
required: true
inlined: true
inlined_as_list: true

```
</details>