

# Slot: annotation_method


_Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)_



URI: [cdp-meta:annotation_method](metadataannotation_method)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |







## Properties

* Range: [String](String.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:annotation_method |
| native | cdp-meta:annotation_method |
| exact | cdp-common:annotation_method |




## LinkML Source

<details>
```yaml
name: annotation_method
description: Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled
  Learning, template matching)
from_schema: metadata
exact_mappings:
- cdp-common:annotation_method
rank: 1000
alias: annotation_method
owner: Annotation
domain_of:
- Annotation
range: string
required: true
inlined: true
inlined_as_list: true

```
</details>
