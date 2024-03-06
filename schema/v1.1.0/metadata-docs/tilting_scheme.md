# Slot: tilting_scheme


_The order of stage tilting during acquisition of the data_



URI: [cdp-meta:tilting_scheme](https://cryoetdataportal.czscience.com/schema/metadata/tilting_scheme)



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
name: tilting_scheme
description: The order of stage tilting during acquisition of the data
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
exact_mappings:
- cdp-common:tiltseries_tilting_scheme
rank: 1000
alias: tilting_scheme
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true

```
</details>