

# Slot: columns


_The columns used in a point annotation file._



URI: [cdp-meta:columns](metadatacolumns)



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
name: columns
description: The columns used in a point annotation file.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_source_file_point_columns
rank: 1000
alias: columns
owner: AnnotationPointFile
domain_of:
- AnnotationPointFile
range: string
inlined: true
inlined_as_list: true

```
</details>