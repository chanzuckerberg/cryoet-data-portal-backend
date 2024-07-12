# Slot: tilt_series_quality


_Author assessment of tilt series quality within the dataset (1-5, 5 is best)_



URI: [cdp-meta:tilt_series_quality](metadatatilt_series_quality)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Integer](Integer.md)

* Required: True

* Minimum Value: 1

* Maximum Value: 5





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: tilt_series_quality
description: Author assessment of tilt series quality within the dataset (1-5, 5 is
  best)
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_tilt_series_quality
rank: 1000
alias: tilt_series_quality
owner: TiltSeries
domain_of:
- TiltSeries
range: integer
required: true
inlined: true
inlined_as_list: true
minimum_value: 1
maximum_value: 5

```
</details>
