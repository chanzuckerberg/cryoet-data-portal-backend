

# Slot: precision


_Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive_



URI: [cdp-meta:precision](metadataprecision)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationConfidence](AnnotationConfidence.md) | Metadata describing the confidence of an annotation |  no  |







## Properties

* Range: [Float](Float.md)

* Minimum Value: 0

* Maximum Value: 100





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:precision |
| native | cdp-meta:precision |
| exact | cdp-common:annotation_confidence_precision |




## LinkML Source

<details>
```yaml
name: precision
description: Describe the confidence level of the annotation. Precision is defined
  as the % of annotation objects being true positive
from_schema: metadata
exact_mappings:
- cdp-common:annotation_confidence_precision
rank: 1000
alias: precision
owner: AnnotationConfidence
domain_of:
- AnnotationConfidence
range: float
inlined: true
inlined_as_list: true
minimum_value: 0
maximum_value: 100
unit:
  symbol: '%'
  descriptive_name: percentage

```
</details>