# Slot: aligned_tiltseries_binning


_Binning factor of the aligned tilt series_



URI: [cdp-meta:aligned_tiltseries_binning](metadataaligned_tiltseries_binning)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Integer](Integer.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: aligned_tiltseries_binning
description: Binning factor of the aligned tilt series
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_aligned_tiltseries_binning
rank: 1000
ifabsent: int(1)
alias: aligned_tiltseries_binning
owner: TiltSeries
domain_of:
- TiltSeries
range: integer
inlined: true
inlined_as_list: true

```
</details>
