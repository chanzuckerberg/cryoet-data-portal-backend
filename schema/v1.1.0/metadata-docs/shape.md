

# Slot: shape


_Describe whether this is a Point, OrientedPoint, or SegmentationMask file_



URI: [cdp-meta:shape](metadatashape)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationFile](AnnotationFile.md) | Metadata describing a file containing an annotation |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: shape
description: Describe whether this is a Point, OrientedPoint, or SegmentationMask
  file
from_schema: metadata
exact_mappings:
- cdp-common:annotation_file_shape_type
rank: 1000
alias: shape
owner: AnnotationFile
domain_of:
- AnnotationFile
range: string
inlined: true
inlined_as_list: true

```
</details>