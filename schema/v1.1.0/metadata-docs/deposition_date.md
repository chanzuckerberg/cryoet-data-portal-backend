# Slot: deposition_date


_The date a data item was received by the cryoET data portal._



URI: [cdp-meta:deposition_date](metadatadeposition_date)



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
name: deposition_date
description: The date a data item was received by the cryoET data portal.
from_schema: metadata
exact_mappings:
- cdp-common:deposition_date
rank: 1000
alias: deposition_date
owner: DateStamp
domain_of:
- DateStamp
range: date
required: true
inlined: true
inlined_as_list: true

```
</details>
