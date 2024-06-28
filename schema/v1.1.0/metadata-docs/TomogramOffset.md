

# Class: TomogramOffset


_The offset of a tomogram in voxels in each dimension relative to the canonical tomogram._





URI: [cdp-meta:TomogramOffset](metadataTomogramOffset)






```mermaid
 classDiagram
    class TomogramOffset
    click TomogramOffset href "../TomogramOffset"
      TomogramOffset : x
        
          
    
    
    TomogramOffset --> "0..1" Integer : x
    click Integer href "../Integer"

        
      TomogramOffset : y
        
          
    
    
    TomogramOffset --> "0..1" Integer : y
    click Integer href "../Integer"

        
      TomogramOffset : z
        
          
    
    
    TomogramOffset --> "0..1" Integer : z
    click Integer href "../Integer"

        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [x](x.md) | 0..1 <br/> [xsd:integer](http://www.w3.org/2001/XMLSchema#integer) |  | direct |
| [y](y.md) | 0..1 <br/> [xsd:integer](http://www.w3.org/2001/XMLSchema#integer) |  | direct |
| [z](z.md) | 0..1 <br/> [xsd:integer](http://www.w3.org/2001/XMLSchema#integer) |  | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Tomogram](Tomogram.md) | [offset](offset.md) | range | [TomogramOffset](TomogramOffset.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:TomogramOffset |
| native | cdp-meta:TomogramOffset |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: TomogramOffset
description: The offset of a tomogram in voxels in each dimension relative to the
  canonical tomogram.
from_schema: metadata
attributes:
  x:
    name: x
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_offset_x
    alias: x
    owner: TomogramOffset
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  y:
    name: y
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_offset_y
    alias: y
    owner: TomogramOffset
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  z:
    name: z
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_offset_z
    alias: z
    owner: TomogramOffset
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
name: TomogramOffset
description: The offset of a tomogram in voxels in each dimension relative to the
  canonical tomogram.
from_schema: metadata
attributes:
  x:
    name: x
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_offset_x
    alias: x
    owner: TomogramOffset
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  y:
    name: y
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_offset_y
    alias: y
    owner: TomogramOffset
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true
  z:
    name: z
    from_schema: metadata
    exact_mappings:
    - cdp-common:tomogram_offset_z
    alias: z
    owner: TomogramOffset
    domain_of:
    - TomogramSize
    - TomogramOffset
    range: integer
    inlined: true
    inlined_as_list: true

```
</details>