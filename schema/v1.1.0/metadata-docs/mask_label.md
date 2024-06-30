

# Slot: mask_label


_The mask label for a semantic segmentation mask annotation file._



URI: [cdp-meta:mask_label](metadatamask_label)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationSemanticSegmentationMaskFile](AnnotationSemanticSegmentationMaskFile.md) | File and sourcing data for a semantic segmentation mask annotation |  no  |







## Properties

* Range: [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: mask_label
description: The mask label for a semantic segmentation mask annotation file.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_source_file_semantic_segmentation_mask_label
rank: 1000
alias: mask_label
owner: AnnotationSemanticSegmentationMaskFile
domain_of:
- AnnotationSemanticSegmentationMaskFile
range: integer
inlined: true
inlined_as_list: true

```
</details>