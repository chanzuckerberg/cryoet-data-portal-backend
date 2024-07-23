# Slot: release_date


_The date a data item was received by the cryoET data portal._



URI: [cdp-meta:release_date](metadatarelease_date)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modifie... |  no  |







## Properties

* Range: [Date](Date.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: release_date
description: The date a data item was received by the cryoET data portal.
from_schema: metadata
exact_mappings:
- cdp-common:release_date
rank: 1000
alias: release_date
owner: DateStamp
domain_of:
- DateStamp
range: date
required: true
inlined: true
inlined_as_list: true

```
</details>