# Slot: microscope_additional_info


_Other microscope optical setup information, in addition to energy filter, phase plate and image corrector_



URI: [cdp-meta:microscope_additional_info](https://cryoetdataportal.czscience.com/schema/metadata/microscope_additional_info)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: microscope_additional_info
description: Other microscope optical setup information, in addition to energy filter,
  phase plate and image corrector
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
exact_mappings:
- cdp-common:tiltseries_microscope_additional_info
rank: 1000
alias: microscope_additional_info
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true

```
</details>