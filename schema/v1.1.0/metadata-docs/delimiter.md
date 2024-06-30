

# Slot: delimiter


_The delimiter used in a oriented point annotation file._



URI: [cdp-meta:delimiter](metadatadelimiter)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationPointFile](AnnotationPointFile.md) | File and sourcing data for a point annotation |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: delimiter
description: The delimiter used in a oriented point annotation file.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_source_file_point_delimiter
rank: 1000
alias: delimiter
owner: AnnotationPointFile
domain_of:
- AnnotationPointFile
range: string
inlined: true
inlined_as_list: true

```
</details>