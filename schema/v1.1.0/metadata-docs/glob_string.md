

# Slot: glob_string

URI: [cdp-meta:glob_string](metadataglob_string)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationOrientedPointFile](AnnotationOrientedPointFile.md) | File and sourcing data for an oriented point annotation |  no  |
| [AnnotationSourceFile](AnnotationSourceFile.md) | File and sourcing data for an annotation |  no  |
| [AnnotationSegmentationMaskFile](AnnotationSegmentationMaskFile.md) | File and sourcing data for a segmentation mask annotation |  no  |
| [AnnotationPointFile](AnnotationPointFile.md) | File and sourcing data for a point annotation |  no  |
| [AnnotationSemanticSegmentationMaskFile](AnnotationSemanticSegmentationMaskFile.md) | File and sourcing data for a semantic segmentation mask annotation |  no  |
| [AnnotationInstanceSegmentationFile](AnnotationInstanceSegmentationFile.md) | File and sourcing data for an instance segmentation annotation |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:glob_string |
| native | cdp-meta:glob_string |




## LinkML Source

<details>
```yaml
name: glob_string
alias: glob_string
domain_of:
- AnnotationSourceFile
- AnnotationOrientedPointFile
- AnnotationInstanceSegmentationFile
- AnnotationPointFile
- AnnotationSegmentationMaskFile
- AnnotationSemanticSegmentationMaskFile
range: string

```
</details>
