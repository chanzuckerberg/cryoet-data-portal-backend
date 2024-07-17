

# Slot: last_modified_date


_The date a piece of data was last modified on the cryoET data portal._



URI: [cdp-meta:last_modified_date](metadatalast_modified_date)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modifie... |  no  |







## Properties

* Range: [Date](Date.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:last_modified_date |
| native | cdp-meta:last_modified_date |
| exact | cdp-common:last_modified_date |




## LinkML Source

<details>
```yaml
name: last_modified_date
description: The date a piece of data was last modified on the cryoET data portal.
from_schema: metadata
exact_mappings:
- cdp-common:last_modified_date
rank: 1000
alias: last_modified_date
owner: DateStamp
domain_of:
- DateStamp
range: date
required: true
inlined: true
inlined_as_list: true

```
</details>
