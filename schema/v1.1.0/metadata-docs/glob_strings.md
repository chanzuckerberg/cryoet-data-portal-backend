

# Slot: glob_strings

URI: [cdp-meta:glob_strings](metadataglob_strings)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationPointFile](AnnotationPointFile.md) | File and sourcing data for a point annotation |  no  |
| [AnnotationInstanceSegmentationFile](AnnotationInstanceSegmentationFile.md) | File and sourcing data for an instance segmentation annotation |  no  |
| [AnnotationSemanticSegmentationMaskFile](AnnotationSemanticSegmentationMaskFile.md) | File and sourcing data for a semantic segmentation mask annotation |  no  |
| [AnnotationSegmentationMaskFile](AnnotationSegmentationMaskFile.md) | File and sourcing data for a segmentation mask annotation |  no  |
| [AnnotationOrientedPointFile](AnnotationOrientedPointFile.md) | File and sourcing data for an oriented point annotation |  no  |
| [AnnotationSourceFile](AnnotationSourceFile.md) | File and sourcing data for an annotation |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:glob_strings |
| native | cdp-meta:glob_strings |




## LinkML Source

<details>
```yaml
name: glob_strings
alias: glob_strings
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
