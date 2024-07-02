

# Slot: method_type


_Classification of the annotation method based on supervision._



URI: [cdp-meta:method_type](metadatamethod_type)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |







## Properties

* Range: [AnnotationMethodTypeEnum](AnnotationMethodTypeEnum.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:method_type |
| native | cdp-meta:method_type |
| exact | cdp-common:annotation_method_type |




## LinkML Source

<details>
```yaml
name: method_type
description: Classification of the annotation method based on supervision.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_method_type
rank: 1000
alias: method_type
owner: Annotation
domain_of:
- Annotation
range: annotation_method_type_enum
inlined: true
inlined_as_list: true

```
</details>