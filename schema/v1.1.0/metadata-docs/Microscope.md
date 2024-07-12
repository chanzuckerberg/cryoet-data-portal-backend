

# Class: Microscope


_The microscope used to collect the tilt series._





URI: [cdp-meta:Microscope](metadataMicroscope)






```mermaid
 classDiagram
    class Microscope
    click Microscope href "../Microscope"
      Microscope : additional_info

      Microscope : manufacturer

      Microscope : model


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
| [TiltSeries](TiltSeries.md) | [microscope](microscope.md) | range | [Microscope](Microscope.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:Microscope |
| native | cdp-meta:Microscope |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Microscope
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
    owner: Microscope
    domain_of:
    - Microscope
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
    owner: Microscope
    domain_of:
    - Camera
    - Microscope
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
    owner: Microscope
    domain_of:
    - Camera
    - Microscope
    range: string
    required: true
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: Microscope
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
    owner: Microscope
    domain_of:
    - Microscope
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
    owner: Microscope
    domain_of:
    - Camera
    - Microscope
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
    owner: Microscope
    domain_of:
    - Camera
    - Microscope
    range: string
    required: true
    inlined: true
    inlined_as_list: true

```
</details>
