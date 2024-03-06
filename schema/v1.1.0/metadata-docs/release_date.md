# Slot: release_date


_The date a data item was received by the cryoET data portal._



URI: [cdp-meta:release_date](https://cryoetdataportal.czscience.com/schema/metadata/release_date)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modifie... |  yes  |







## Properties

* Range: [xsd:date](http://www.w3.org/2001/XMLSchema#date)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: release_date
description: The date a data item was received by the cryoET data portal.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
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