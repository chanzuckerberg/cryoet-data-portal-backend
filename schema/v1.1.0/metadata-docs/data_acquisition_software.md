

# Slot: data_acquisition_software


_Software used to collect data_



URI: [cdp-meta:data_acquisition_software](metadatadata_acquisition_software)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:data_acquisition_software |
| native | cdp-meta:data_acquisition_software |
| exact | cdp-common:tiltseries_data_acquisition_software |




## LinkML Source

<details>
```yaml
name: data_acquisition_software
description: Software used to collect data
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_data_acquisition_software
rank: 1000
alias: data_acquisition_software
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true

```
</details>