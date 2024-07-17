

# Slot: tilting_scheme


_The order of stage tilting during acquisition of the data_



URI: [cdp-meta:tilting_scheme](metadatatilting_scheme)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:tilting_scheme |
| native | cdp-meta:tilting_scheme |
| exact | cdp-common:tiltseries_tilting_scheme |




## LinkML Source

<details>
```yaml
name: tilting_scheme
description: The order of stage tilting during acquisition of the data
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_tilting_scheme
rank: 1000
alias: tilting_scheme
owner: TiltSeries
domain_of:
- TiltSeries
range: string
required: true
inlined: true
inlined_as_list: true

```
</details>