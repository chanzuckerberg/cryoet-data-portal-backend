

# Slot: tilt_axis


_Rotation angle in degrees_



URI: [cdp-meta:tilt_axis](metadatatilt_axis)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Any](Any.md)&nbsp;or&nbsp;<br />[Float](Float.md)&nbsp;or&nbsp;<br />[FloatFormattedString](FloatFormattedString.md)

* Minimum Value: -360

* Maximum Value: 360

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:tilt_axis |
| native | cdp-meta:tilt_axis |




## LinkML Source

<details>
```yaml
name: tilt_axis
description: Rotation angle in degrees
from_schema: metadata
rank: 1000
alias: tilt_axis
owner: TiltSeries
domain_of:
- TiltSeries
range: Any
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
