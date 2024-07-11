

# Slot: file_format

URI: [cdp-meta:file_format](metadatafile_format)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationSourceFile](AnnotationSourceFile.md) | File and sourcing data for an annotation |  no  |
| [AnnotationOrientedPointFile](AnnotationOrientedPointFile.md) | File and sourcing data for an oriented point annotation |  no  |
| [AnnotationSegmentationMaskFile](AnnotationSegmentationMaskFile.md) | File and sourcing data for a segmentation mask annotation |  no  |
| [AnnotationInstanceSegmentationFile](AnnotationInstanceSegmentationFile.md) | File and sourcing data for an instance segmentation annotation |  no  |
| [AnnotationPointFile](AnnotationPointFile.md) | File and sourcing data for a point annotation |  no  |
| [AnnotationSemanticSegmentationMaskFile](AnnotationSemanticSegmentationMaskFile.md) | File and sourcing data for a semantic segmentation mask annotation |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:file_format |
| native | cdp-meta:file_format |




## LinkML Source

<details>
```yaml
name: file_format
alias: file_format
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
