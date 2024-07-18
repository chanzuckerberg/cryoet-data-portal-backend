

# Slot: ground_truth_status


_Whether an annotation is considered ground truth, as determined by the annotator._



URI: [cdp-meta:ground_truth_status](metadataground_truth_status)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |







## Properties

* Range: [Boolean](Boolean.md)

* Recommended: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:ground_truth_status |
| native | cdp-meta:ground_truth_status |
| exact | cdp-common:annotation_ground_truth_status |




## LinkML Source

<details>
```yaml
name: ground_truth_status
description: Whether an annotation is considered ground truth, as determined by the
  annotator.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_ground_truth_status
rank: 1000
ifabsent: 'False'
alias: ground_truth_status
owner: Annotation
domain_of:
- Annotation
range: boolean
recommended: true
inlined: true
inlined_as_list: true

```
</details>
