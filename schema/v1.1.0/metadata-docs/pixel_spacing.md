

# Slot: pixel_spacing


_Pixel spacing for the tilt series_



URI: [cdp-meta:pixel_spacing](metadatapixel_spacing)



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
| self | cdp-meta:pixel_spacing |
| native | cdp-meta:pixel_spacing |
| exact | cdp-common:tiltseries_pixel_spacing |




## LinkML Source

<details>
```yaml
name: pixel_spacing
description: Pixel spacing for the tilt series
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_pixel_spacing
rank: 1000
alias: pixel_spacing
owner: TiltSeries
domain_of:
- TiltSeries
range: float
required: true
inlined: true
inlined_as_list: true
minimum_value: 0
unit:
  symbol: Å/px
  descriptive_name: Angstroms per pixel

```
</details>