

# Slot: grant_id


_Grant identifier provided by the funding agency_



URI: [cdp-meta:grant_id](metadatagrant_id)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Funding](Funding.md) | A funding source for a scientific data entity (base for JSON and DB represent... |  no  |







## Properties

* Range: [String](String.md)

* Recommended: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:grant_id |
| native | cdp-meta:grant_id |
| exact | cdp-common:funding_grant_id |




## LinkML Source

<details>
```yaml
name: grant_id
description: Grant identifier provided by the funding agency
from_schema: metadata
exact_mappings:
- cdp-common:funding_grant_id
rank: 1000
alias: grant_id
owner: Funding
domain_of:
- Funding
range: string
recommended: true
inlined: true
inlined_as_list: true

```
</details>
