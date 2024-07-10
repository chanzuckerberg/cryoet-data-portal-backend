

# Slot: ORCID


_A unique, persistent identifier for researchers, provided by ORCID._



URI: [cdp-meta:ORCID](metadataORCID)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Author](Author.md) | Author of a scientific data entity |  no  |







## Properties

* Range: [String](String.md)

* Recommended: True

* Regex pattern: `[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:ORCID |
| native | cdp-meta:ORCID |
| exact | cdp-common:orcid |




## LinkML Source

<details>
```yaml
name: ORCID
description: A unique, persistent identifier for researchers, provided by ORCID.
from_schema: metadata
exact_mappings:
- cdp-common:orcid
rank: 1000
alias: ORCID
owner: Author
domain_of:
- Author
range: string
recommended: true
inlined: true
inlined_as_list: true
pattern: '[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$'

```
</details>
