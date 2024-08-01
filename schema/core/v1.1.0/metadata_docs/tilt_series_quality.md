

# Slot: tilt_series_quality


_Author assessment of tilt series quality within the dataset (1-5, 5 is best)_



URI: [cdp-meta:tilt_series_quality](metadatatilt_series_quality)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[Integer](Integer.md)&nbsp;or&nbsp;<br />[IntegerFormattedString](IntegerFormattedString.md)

* Minimum Value: 1

* Maximum Value: 5

* Regex pattern: `^int[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:tilt_series_quality |
| native | cdp-meta:tilt_series_quality |




## LinkML Source

<details>
```yaml
name: tilt_series_quality
description: Author assessment of tilt series quality within the dataset (1-5, 5 is
  best)
from_schema: metadata
rank: 1000
alias: tilt_series_quality
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true
minimum_value: 1
maximum_value: 5
pattern: ^int[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
any_of:
- range: integer
  minimum_value: 1
  maximum_value: 5
- range: IntegerFormattedString

```
</details>
