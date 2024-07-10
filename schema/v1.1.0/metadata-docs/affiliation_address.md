

# Slot: affiliation_address


_The address of the author's affiliation._



URI: [cdp-meta:affiliation_address](metadataaffiliation_address)



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
| self | cdp-meta:affiliation_address |
| native | cdp-meta:affiliation_address |
| exact | cdp-common:author_affiliation_address |




## LinkML Source

<details>
```yaml
name: affiliation_address
description: The address of the author's affiliation.
from_schema: metadata
exact_mappings:
- cdp-common:author_affiliation_address
rank: 1000
alias: affiliation_address
owner: Author
domain_of:
- Author
range: string
inlined: true
inlined_as_list: true

```
</details>
