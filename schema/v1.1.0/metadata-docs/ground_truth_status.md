

# Slot: ground_truth_status


_Whether an annotation is considered ground truth, as determined by the annotator._



URI: [cdp-meta:ground_truth_status](metadataground_truth_status)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |







## Properties

* Range: [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




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
alias: ground_truth_status
owner: Annotation
domain_of:
- Annotation
range: boolean
inlined: true
inlined_as_list: true

```
</details>