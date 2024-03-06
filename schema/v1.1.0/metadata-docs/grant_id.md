# Slot: grant_id


_Grant identifier provided by the funding agency_



URI: [cdp-meta:grant_id](https://cryoetdataportal.czscience.com/schema/metadata/grant_id)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Funding](Funding.md) | A funding source for a scientific data entity (base for JSON and DB represent... |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: grant_id
description: Grant identifier provided by the funding agency
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
exact_mappings:
- cdp-common:funding_grant_id
rank: 1000
alias: grant_id
owner: Funding
domain_of:
- Funding
range: string
inlined: true
inlined_as_list: true

```
</details>