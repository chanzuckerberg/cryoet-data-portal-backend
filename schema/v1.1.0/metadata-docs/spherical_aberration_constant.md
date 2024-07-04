

# Slot: spherical_aberration_constant


_Spherical Aberration Constant of the objective lens in millimeters_



URI: [cdp-meta:spherical_aberration_constant](metadataspherical_aberration_constant)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Float](Float.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:spherical_aberration_constant |
| native | cdp-meta:spherical_aberration_constant |
| exact | cdp-common:tiltseries_spherical_aberration_constant |




## LinkML Source

<details>
```yaml
name: spherical_aberration_constant
description: Spherical Aberration Constant of the objective lens in millimeters
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_spherical_aberration_constant
rank: 1000
alias: spherical_aberration_constant
owner: TiltSeries
domain_of:
- TiltSeries
range: float
required: true
inlined: true
inlined_as_list: true

```
</details>