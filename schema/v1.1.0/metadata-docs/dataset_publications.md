

# Slot: dataset_publications


_Comma-separated list of DOIs for publications associated with the dataset._



URI: [cdp-meta:dataset_publications](metadatadataset_publications)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CrossReferences](CrossReferences.md) | A set of cross-references to other databases and publications |  no  |







## Properties

* Range: [DOILIST](DOILIST.md)

* Recommended: True

* Regex pattern: `(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:dataset_publications |
| native | cdp-meta:dataset_publications |




## LinkML Source

<details>
```yaml
name: dataset_publications
description: Comma-separated list of DOIs for publications associated with the dataset.
from_schema: metadata
rank: 1000
alias: dataset_publications
owner: CrossReferences
domain_of:
- CrossReferences
range: DOI_LIST
recommended: true
inlined: true
inlined_as_list: true
pattern: (^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)

```
</details>