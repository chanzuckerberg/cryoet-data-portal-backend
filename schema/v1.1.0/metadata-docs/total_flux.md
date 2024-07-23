# Slot: total_flux


_Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series_



URI: [cdp-meta:total_flux](metadatatotal_flux)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)

* Required: True

* Minimum Value: 0

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




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
range: string
required: true
inlined: true
inlined_as_list: true
minimum_value: 0
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
unit:
  symbol: e^-/Å^2
  descriptive_name: electrons per square Angstrom
any_of:
- range: float
  minimum_value: 0
- range: FloatFormattedString

```
</details>