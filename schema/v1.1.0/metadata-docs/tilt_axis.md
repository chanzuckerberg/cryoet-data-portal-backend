# Slot: tilt_axis


_Rotation angle in degrees_



URI: [cdp-meta:tilt_axis](metadatatilt_axis)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)

* Required: True

* Minimum Value: -360

* Maximum Value: 360

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




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
range: string
required: true
inlined: true
inlined_as_list: true
minimum_value: -360
maximum_value: 360
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
unit:
  symbol: °
  descriptive_name: degrees
any_of:
- range: float
  minimum_value: -360
  maximum_value: 360
- range: FloatFormattedString

```
</details>