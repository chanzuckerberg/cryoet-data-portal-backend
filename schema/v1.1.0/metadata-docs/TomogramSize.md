

# Class: TomogramSize


_The size of a tomogram in voxels in each dimension._





URI: [cdp-meta:TomogramSize](metadataTomogramSize)






```mermaid
 classDiagram
    class TomogramSize
    click TomogramSize href "../TomogramSize"
      TomogramSize : x
        
      TomogramSize : y
        
      TomogramSize : z
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [x](x.md) | 0..1 <br/> [Integer](Integer.md) | Number of pixels in the 3D data fast axis | direct |
| [y](y.md) | 0..1 <br/> [Integer](Integer.md) | Number of pixels in the 3D data medium axis | direct |
| [z](z.md) | 0..1 <br/> [Integer](Integer.md) | Number of pixels in the 3D data slow axis | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Tomogram](Tomogram.md) | [size](size.md) | range | [TomogramSize](TomogramSize.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:TomogramSize |
| native | cdp-meta:TomogramSize |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: TomogramSize
description: The size of a tomogram in voxels in each dimension.
from_schema: metadata
attributes:
  x:
    name: x
    description: Number of pixels in the 3D data fast axis
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_size_x
    rank: 1000
    alias: x
    owner: TomogramSize
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  y:
    name: y
    description: Number of pixels in the 3D data medium axis
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_size_y
    rank: 1000
    alias: y
    owner: TomogramSize
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  z:
    name: z
    description: Number of pixels in the 3D data slow axis.  This is the image projection
      direction at zero stage tilt
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_size_z
    rank: 1000
    alias: z
    owner: TomogramSize
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: TomogramSize
description: The size of a tomogram in voxels in each dimension.
from_schema: metadata
attributes:
  x:
    name: x
    description: Number of pixels in the 3D data fast axis
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_size_x
    rank: 1000
    alias: x
    owner: TomogramSize
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  y:
    name: y
    description: Number of pixels in the 3D data medium axis
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_size_y
    rank: 1000
    alias: y
    owner: TomogramSize
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  z:
    name: z
    description: Number of pixels in the 3D data slow axis.  This is the image projection
      direction at zero stage tilt
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_size_z
    rank: 1000
    alias: z
    owner: TomogramSize
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true

```
</details>