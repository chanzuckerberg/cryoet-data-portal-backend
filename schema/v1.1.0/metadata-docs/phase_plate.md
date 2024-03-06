# Slot: phase_plate


_Phase plate configuration_



URI: [cdp-meta:phase_plate](https://cryoetdataportal.czscience.com/schema/metadata/phase_plate)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[MicroscopeOpticalSetup](MicroscopeOpticalSetup.md) | The optical setup of the microscope used to collect the tilt series |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: phase_plate
description: Phase plate configuration
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
exact_mappings:
- cdp-common:tiltseries_microscope_phase_plate
rank: 1000
alias: phase_plate
owner: MicroscopeOpticalSetup
domain_of:
- MicroscopeOpticalSetup
range: string
inlined: true
inlined_as_list: true

```
</details>