

# Slot: related_empiar_entry


_If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier_



URI: [cdp-meta:related_empiar_entry](metadatarelated_empiar_entry)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:related_empiar_entry |
| native | cdp-meta:related_empiar_entry |
| exact | cdp-common:tiltseries_related_empiar_entry |




## LinkML Source

<details>
```yaml
name: related_empiar_entry
description: If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_related_empiar_entry
rank: 1000
alias: related_empiar_entry
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true

```
</details>
