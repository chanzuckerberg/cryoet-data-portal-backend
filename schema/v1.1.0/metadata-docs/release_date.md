

# Slot: release_date


_The date a data item was received by the cryoET data portal._



URI: [cdp-meta:release_date](metadatarelease_date)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modifie... |  yes  |







## Properties

* Range: [Date](Date.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:release_date |
| native | cdp-meta:release_date |




## LinkML Source

<details>
```yaml
name: release_date
description: The date a data item was received by the cryoET data portal.
from_schema: metadata
rank: 1000
alias: release_date
owner: DateStamp
domain_of:
- DateStamp
range: date
required: true
recommended: true
inlined: true
inlined_as_list: true

```
</details>