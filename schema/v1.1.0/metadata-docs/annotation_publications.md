

# Slot: annotation_publications


_DOIs for publications that describe the dataset. Use a comma to separate multiple DOIs._



URI: [cdp-meta:annotation_publications](metadataannotation_publications)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: annotation_publications
description: DOIs for publications that describe the dataset. Use a comma to separate
  multiple DOIs.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_publication
rank: 1000
alias: annotation_publications
owner: Annotation
domain_of:
- Annotation
range: string
inlined: true
inlined_as_list: true

```
</details>