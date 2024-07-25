

# Slot: state


_Molecule state annotated (e.g. open, closed)_



URI: [cdp-meta:state](metadatastate)



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




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:state |
| native | cdp-meta:state |
| exact | cdp-common:annotation_object_state |




## LinkML Source

<details>
```yaml
name: state
description: Molecule state annotated (e.g. open, closed)
from_schema: metadata
exact_mappings:
- cdp-common:annotation_object_state
rank: 1000
alias: state
owner: AnnotationObject
domain_of:
- AnnotationObject
range: string
inlined: true
inlined_as_list: true

```
</details>