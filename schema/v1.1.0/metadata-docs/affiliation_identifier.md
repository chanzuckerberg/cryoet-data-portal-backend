

# Slot: affiliation_identifier


_A Research Organization Registry (ROR) identifier._



URI: [cdp-meta:affiliation_identifier](metadataaffiliation_identifier)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Author](Author.md) | Author of a scientific data entity |  no  |







## Properties

* Range: [String](String.md)

* Recommended: True

* Regex pattern: `^0[a-hj-km-np-tv-z|0-9]{6}[0-9]{2}$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:affiliation_identifier |
| native | cdp-meta:affiliation_identifier |
| exact | cdp-common:affiliation_identifier |




## LinkML Source

<details>
```yaml
name: affiliation_identifier
description: A Research Organization Registry (ROR) identifier.
from_schema: metadata
exact_mappings:
- cdp-common:affiliation_identifier
rank: 1000
alias: affiliation_identifier
owner: Author
domain_of:
- Author
range: string
recommended: true
inlined: true
inlined_as_list: true
pattern: ^0[a-hj-km-np-tv-z|0-9]{6}[0-9]{2}$

```
</details>
