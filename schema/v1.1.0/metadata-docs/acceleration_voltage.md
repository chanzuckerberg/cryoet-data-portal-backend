# Slot: acceleration_voltage


_Electron Microscope Accelerator voltage in volts_



URI: [cdp-meta:acceleration_voltage](metadataacceleration_voltage)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Float](Float.md)

* Required: True

* Minimum Value: 20000





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




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
range: float
required: true
inlined: true
inlined_as_list: true
minimum_value: 20000
unit:
  symbol: V
  descriptive_name: volts

```
</details>