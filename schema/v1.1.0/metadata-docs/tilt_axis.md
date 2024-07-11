

# Slot: tilt_axis


_Rotation angle in degrees_



URI: [cdp-meta:tilt_axis](metadatatilt_axis)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Float](Float.md)

* Required: True

* Minimum Value: -360

* Maximum Value: 360





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:tilt_axis |
| native | cdp-meta:tilt_axis |
| exact | cdp-common:tiltseries_tilt_axis |




## LinkML Source

<details>
```yaml
name: tilt_axis
description: Rotation angle in degrees
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_tilt_axis
rank: 1000
alias: tilt_axis
owner: TiltSeries
domain_of:
- TiltSeries
range: float
required: true
inlined: true
inlined_as_list: true
minimum_value: -360
maximum_value: 360
unit:
  symbol: °
  descriptive_name: degrees

```
</details>
