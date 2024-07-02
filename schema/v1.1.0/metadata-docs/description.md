

# Slot: description


_A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state._



URI: [cdp-meta:description](metadatadescription)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AnnotationObject](AnnotationObject.md) | Metadata describing the object being annotated |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: description
description: A textual description of the annotation object, can be a longer description
  to include additional information not covered by the Annotation object name and
  state.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_object_description
rank: 1000
alias: description
owner: AnnotationObject
domain_of:
- AnnotationObject
range: string
inlined: true
inlined_as_list: true

```
</details>