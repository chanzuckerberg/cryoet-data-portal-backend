

# Slot: snapshot


_Path to the dataset preview image relative to the dataset directory root._



URI: [cdp-meta:snapshot](metadatasnapshot)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PicturePath](PicturePath.md) | A set of paths to representative images of a piece of data |  no  |







## Properties

* Range: [URLorS3URI](URLorS3URI.md)

* Recommended: True

* Regex pattern: `^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$`





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
description: Path to the dataset preview image relative to the dataset directory root.
from_schema: metadata
exact_mappings:
- cdp-common:snapshot
rank: 1000
alias: snapshot
owner: PicturePath
domain_of:
- PicturePath
range: URLorS3URI
recommended: true
inlined: true
inlined_as_list: true
pattern: ^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$

```
</details>