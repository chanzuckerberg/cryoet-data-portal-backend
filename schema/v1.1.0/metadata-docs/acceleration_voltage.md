# Slot: acceleration_voltage


_Electron Microscope Accelerator voltage in volts_



URI: [cdp-meta:acceleration_voltage](https://cryoetdataportal.czscience.com/schema/metadata/acceleration_voltage)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: acceleration_voltage
description: Electron Microscope Accelerator voltage in volts
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
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