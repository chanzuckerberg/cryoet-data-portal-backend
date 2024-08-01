

# Slot: delimiter


_The delimiter used in a point annotation file._



URI: [cdp-meta:delimiter](metadatadelimiter)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationPointFile](AnnotationPointFile.md) | File and sourcing data for a point annotation |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:delimiter |
| native | cdp-meta:delimiter |
| exact | cdp-common:annotation_source_file_delimiter |




## LinkML Source

<details>
```yaml
name: delimiter
description: The delimiter used in a point annotation file.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_source_file_delimiter
rank: 1000
ifabsent: string(,)
alias: delimiter
owner: AnnotationPointFile
domain_of:
- AnnotationPointFile
range: string
inlined: true
inlined_as_list: true

```
</details>