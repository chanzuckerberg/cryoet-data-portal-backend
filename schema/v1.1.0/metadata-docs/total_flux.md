

# Slot: total_flux


_Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series_



URI: [cdp-meta:total_flux](metadatatotal_flux)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Float](Float.md)

* Required: True

* Minimum Value: 0





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:total_flux |
| native | cdp-meta:total_flux |
| exact | cdp-common:tiltseries_total_flux |




## LinkML Source

<details>
```yaml
name: total_flux
description: Number of Electrons reaching the specimen in a square Angstrom area for
  the entire tilt series
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_total_flux
rank: 1000
alias: total_flux
owner: TiltSeries
domain_of:
- TiltSeries
range: float
required: true
inlined: true
inlined_as_list: true
minimum_value: 0
unit:
  symbol: e^-/Å^2
  descriptive_name: electrons per square Angstrom

```
</details>
