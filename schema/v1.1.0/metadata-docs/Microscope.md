

# Class: Microscope


_The microscope used to collect the tilt series._





URI: [cdp-meta:Microscope](metadataMicroscope)






```mermaid
 classDiagram
    class Microscope
    click Microscope href "../Microscope"
      Microscope : manufacturer




    Microscope --> "1" MicroscopeManufacturerEnum : manufacturer
    click MicroscopeManufacturerEnum href "../MicroscopeManufacturerEnum"


      Microscope : model


```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [manufacturer](manufacturer.md) | 1 <br/> [MicroscopeManufacturerEnum](MicroscopeManufacturerEnum.md) | Name of the microscope manufacturer | direct |
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
    range: microscope_manufacturer_enum
    required: true
    inlined: true
    inlined_as_list: true
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
    range: microscope_manufacturer_enum
    required: true
    inlined: true
    inlined_as_list: true
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
