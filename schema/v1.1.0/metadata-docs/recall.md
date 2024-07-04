

# Slot: recall


_Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly_



URI: [cdp-meta:recall](metadatarecall)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationConfidence](AnnotationConfidence.md) | Metadata describing the confidence of an annotation |  no  |







## Properties

* Range: [Float](Float.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:recall |
| native | cdp-meta:recall |
| exact | cdp-common:annotation_confidence_recall |




## LinkML Source

<details>
```yaml
name: recall
description: Describe the confidence level of the annotation. Recall is defined as
  the % of true positives being annotated correctly
from_schema: metadata
exact_mappings:
- cdp-common:annotation_confidence_recall
rank: 1000
alias: recall
owner: AnnotationConfidence
domain_of:
- AnnotationConfidence
range: float
inlined: true
inlined_as_list: true
unit:
  symbol: '%'
  descriptive_name: percentage

```
</details>