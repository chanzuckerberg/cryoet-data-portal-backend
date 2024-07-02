

# Slot: acceleration_voltage


_Electron Microscope Accelerator voltage in volts_



URI: [cdp-meta:acceleration_voltage](metadataacceleration_voltage)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Integer](Integer.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:acceleration_voltage |
| native | cdp-meta:acceleration_voltage |
| exact | cdp-common:tiltseries_acceleration_voltage |




## LinkML Source

<details>
```yaml
name: acceleration_voltage
description: Electron Microscope Accelerator voltage in volts
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_acceleration_voltage
rank: 1000
alias: acceleration_voltage
owner: TiltSeries
domain_of:
- TiltSeries
range: integer
inlined: true
inlined_as_list: true

```
</details>