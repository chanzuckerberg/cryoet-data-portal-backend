

# Slot: link_type


_Type of link (e.g. model, sourcecode, documentation)_



URI: [cdp-meta:link_type](metadatalink_type)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationMethodLinks](AnnotationMethodLinks.md) | A set of links to models, sourcecode, documentation, etc referenced by annota... |  no  |







## Properties

* Range: [AnnotationMethodLinkTypeEnum](AnnotationMethodLinkTypeEnum.md)

* Required: True

* Regex pattern: `(^documentation$)|(^models_weights$)|(^other$)|(^source_code$)|(^website$)`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:link_type |
| native | cdp-meta:link_type |




## LinkML Source

<details>
```yaml
name: link_type
description: Type of link (e.g. model, sourcecode, documentation)
from_schema: metadata
rank: 1000
alias: link_type
owner: AnnotationMethodLinks
domain_of:
- AnnotationMethodLinks
range: annotation_method_link_type_enum
required: true
inlined: true
inlined_as_list: true
pattern: (^documentation$)|(^models_weights$)|(^other$)|(^source_code$)|(^website$)

```
</details>