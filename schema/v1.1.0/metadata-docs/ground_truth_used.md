

# Slot: ground_truth_used


_Annotation filename used as ground truth for precision and recall_



URI: [cdp-meta:ground_truth_used](metadataground_truth_used)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationConfidence](AnnotationConfidence.md) | Metadata describing the confidence of an annotation |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:ground_truth_used |
| native | cdp-meta:ground_truth_used |
| exact | cdp-common:annotation_ground_truth_used |




## LinkML Source

<details>
```yaml
name: ground_truth_used
description: Annotation filename used as ground truth for precision and recall
from_schema: metadata
exact_mappings:
- cdp-common:annotation_ground_truth_used
rank: 1000
alias: ground_truth_used
owner: AnnotationConfidence
domain_of:
- AnnotationConfidence
range: string
inlined: true
inlined_as_list: true

```
</details>
