

# Slot: spherical_aberration_constant


_Spherical Aberration Constant of the objective lens in millimeters_



URI: [cdp-meta:spherical_aberration_constant](metadataspherical_aberration_constant)



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
| self | cdp-meta:spherical_aberration_constant |
| native | cdp-meta:spherical_aberration_constant |




## LinkML Source

<details>
```yaml
name: spherical_aberration_constant
description: Spherical Aberration Constant of the objective lens in millimeters
from_schema: metadata
rank: 1000
alias: spherical_aberration_constant
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true
minimum_value: 0
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
unit:
  symbol: mm
  descriptive_name: millimeters
any_of:
- range: float
  minimum_value: 0
- range: FloatFormattedString

```
</details>