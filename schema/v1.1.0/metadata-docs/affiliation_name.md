

# Slot: affiliation_name


_The name of the author's affiliation._



URI: [cdp-meta:affiliation_name](metadataaffiliation_name)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Author](Author.md) | Author of a scientific data entity |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:affiliation_name |
| native | cdp-meta:affiliation_name |
| exact | cdp-common:author_affiliation_name |




## LinkML Source

<details>
```yaml
name: affiliation_name
description: The name of the author's affiliation.
from_schema: metadata
exact_mappings:
- cdp-common:author_affiliation_name
rank: 1000
alias: affiliation_name
owner: Author
domain_of:
- Author
range: string
inlined: true
inlined_as_list: true

```
</details>