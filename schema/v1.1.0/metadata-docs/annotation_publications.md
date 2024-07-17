

# Slot: annotation_publications


_List of publication IDs (EMPIAR, EMDB, DOI) that describe this annotation method. Comma separated._



URI: [cdp-meta:annotation_publications](metadataannotation_publications)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |







## Properties

* Range: [EMPIAREMDBDOILIST](EMPIAREMDBDOILIST.md)

* Regex pattern: `^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+))*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:annotation_publications |
| native | cdp-meta:annotation_publications |
| exact | cdp-common:annotation_publications |




## LinkML Source

<details>
```yaml
name: annotation_publications
description: List of publication IDs (EMPIAR, EMDB, DOI) that describe this annotation
  method. Comma separated.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_publications
rank: 1000
alias: annotation_publications
owner: Annotation
domain_of:
- Annotation
range: EMPIAR_EMDB_DOI_LIST
inlined: true
inlined_as_list: true
pattern: ^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+))*$

```
</details>