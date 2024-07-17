

# Slot: funding_agency_name


_The name of the funding source._



URI: [cdp-meta:funding_agency_name](metadatafunding_agency_name)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [FundingDetails](FundingDetails.md) | A funding source for a scientific data entity (base for JSON and DB represent... |  no  |







## Properties

* Range: [String](String.md)

* Recommended: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:funding_agency_name |
| native | cdp-meta:funding_agency_name |
| exact | cdp-common:funding_agency_name |




## LinkML Source

<details>
```yaml
name: funding_agency_name
description: The name of the funding source.
from_schema: metadata
exact_mappings:
- cdp-common:funding_agency_name
rank: 1000
alias: funding_agency_name
owner: FundingDetails
domain_of:
- FundingDetails
range: string
recommended: true
inlined: true
inlined_as_list: true

```
</details>