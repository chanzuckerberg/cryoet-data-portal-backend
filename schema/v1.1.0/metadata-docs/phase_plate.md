

# Slot: phase_plate


_Phase plate configuration_



URI: [cdp-meta:phase_plate](metadataphase_plate)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MicroscopeOpticalSetup](MicroscopeOpticalSetup.md) | The optical setup of the microscope used to collect the tilt series |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:phase_plate |
| native | cdp-meta:phase_plate |
| exact | cdp-common:tiltseries_microscope_phase_plate |




## LinkML Source

<details>
```yaml
name: phase_plate
description: Phase plate configuration
from_schema: metadata
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
