

# Class: MicroscopeDetails


_The microscope used to collect the tilt series._





URI: [cdp-meta:MicroscopeDetails](metadataMicroscopeDetails)






```mermaid
 classDiagram
    class MicroscopeDetails
    click MicroscopeDetails href "../MicroscopeDetails"
      MicroscopeDetails : additional_info

      MicroscopeDetails : manufacturer

      MicroscopeDetails : model


```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [additional_info](additional_info.md) | 0..1 <br/> [String](String.md) | Other microscope optical setup information, in addition to energy filter, pha... | direct |
| [manufacturer](manufacturer.md) | 1 <br/> [String](String.md)&nbsp;or&nbsp;<br />[StringFormattedString](StringFormattedString.md)&nbsp;or&nbsp;<br />[MicroscopeManufacturerEnum](MicroscopeManufacturerEnum.md) | Name of the microscope manufacturer | direct |
| [model](model.md) | 1 <br/> [String](String.md) | Microscope model name | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [TiltSeries](TiltSeries.md) | [microscope](microscope.md) | range | [MicroscopeDetails](MicroscopeDetails.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:MicroscopeDetails |
| native | cdp-meta:MicroscopeDetails |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: MicroscopeDetails
description: The microscope used to collect the tilt series.
from_schema: metadata
attributes:
  additional_info:
    name: additional_info
    description: Other microscope optical setup information, in addition to energy
      filter, phase plate and image corrector
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_additional_info
    rank: 1000
    alias: additional_info
    owner: MicroscopeDetails
    domain_of:
    - MicroscopeDetails
    range: string
    inlined: true
    inlined_as_list: true
  manufacturer:
    name: manufacturer
    description: Name of the microscope manufacturer
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_manufacturer
    alias: manufacturer
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    required: true
    inlined: true
    inlined_as_list: true
    pattern: (^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^FEI$)|(^TFS$)|(^JEOL$)
    any_of:
    - range: StringFormattedString
    - range: microscope_manufacturer_enum
  model:
    name: model
    description: Microscope model name
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_model
    alias: model
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    range: string
    required: true
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: MicroscopeDetails
description: The microscope used to collect the tilt series.
from_schema: metadata
attributes:
  additional_info:
    name: additional_info
    description: Other microscope optical setup information, in addition to energy
      filter, phase plate and image corrector
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_additional_info
    rank: 1000
    alias: additional_info
    owner: MicroscopeDetails
    domain_of:
    - MicroscopeDetails
    range: string
    inlined: true
    inlined_as_list: true
  manufacturer:
    name: manufacturer
    description: Name of the microscope manufacturer
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_manufacturer
    alias: manufacturer
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    range: string
    required: true
    inlined: true
    inlined_as_list: true
    pattern: (^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^FEI$)|(^TFS$)|(^JEOL$)
    any_of:
    - range: StringFormattedString
    - range: microscope_manufacturer_enum
  model:
    name: model
    description: Microscope model name
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_model
    alias: model
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    range: string
    required: true
    inlined: true
    inlined_as_list: true

```
</details>
