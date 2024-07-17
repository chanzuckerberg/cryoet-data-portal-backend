

# Slot: aligned_tiltseries_binning


_Binning factor of the aligned tilt series_



URI: [cdp-meta:aligned_tiltseries_binning](metadataaligned_tiltseries_binning)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md)&nbsp;or&nbsp;<br />[FloatFormattedString](FloatFormattedString.md)

* Minimum Value: 0

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:aligned_tiltseries_binning |
| native | cdp-meta:aligned_tiltseries_binning |
| exact | cdp-common:tiltseries_aligned_tiltseries_binning |




## LinkML Source

<details>
```yaml
name: aligned_tiltseries_binning
description: Binning factor of the aligned tilt series
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_aligned_tiltseries_binning
rank: 1000
ifabsent: float(1)
alias: aligned_tiltseries_binning
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true
minimum_value: 0
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
any_of:
- range: float
  minimum_value: 0
- range: FloatFormattedString

```
</details>