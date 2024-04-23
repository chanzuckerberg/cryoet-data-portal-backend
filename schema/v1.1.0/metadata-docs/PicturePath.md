# Class: PicturePath


_A set of paths to representative images of a piece of data._





URI: [cdp-meta:PicturePath](metadataPicturePath)




```mermaid
 classDiagram
    class PicturePath
      PicturePath : snapshot

          PicturePath --> string : snapshot

      PicturePath : thumbnail

          PicturePath --> string : thumbnail


```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [snapshot](snapshot.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | Path to the dataset preview image relative to the dataset directory root | direct |
| [thumbnail](thumbnail.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | Path to the thumbnail of preview image relative to the dataset directory root | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [PicturedEntity](PicturedEntity.md) | [key_photos](key_photos.md) | range | [PicturePath](PicturePath.md) |
| [Dataset](Dataset.md) | [key_photos](key_photos.md) | range | [PicturePath](PicturePath.md) |
| [Tomogram](Tomogram.md) | [key_photos](key_photos.md) | range | [PicturePath](PicturePath.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:PicturePath |
| native | cdp-meta:PicturePath |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: PicturePath
description: A set of paths to representative images of a piece of data.
from_schema: metadata
attributes:
  snapshot:
    name: snapshot
    description: Path to the dataset preview image relative to the dataset directory
      root.
    from_schema: metadata
    rank: 1000
    alias: snapshot
    owner: PicturePath
    domain_of:
    - PicturePath
    range: string
    inlined: true
    inlined_as_list: true
  thumbnail:
    name: thumbnail
    description: Path to the thumbnail of preview image relative to the dataset directory
      root.
    from_schema: metadata
    rank: 1000
    alias: thumbnail
    owner: PicturePath
    domain_of:
    - PicturePath
    range: string
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: PicturePath
description: A set of paths to representative images of a piece of data.
from_schema: metadata
attributes:
  snapshot:
    name: snapshot
    description: Path to the dataset preview image relative to the dataset directory
      root.
    from_schema: metadata
    rank: 1000
    alias: snapshot
    owner: PicturePath
    domain_of:
    - PicturePath
    range: string
    inlined: true
    inlined_as_list: true
  thumbnail:
    name: thumbnail
    description: Path to the thumbnail of preview image relative to the dataset directory
      root.
    from_schema: metadata
    rank: 1000
    alias: thumbnail
    owner: PicturePath
    domain_of:
    - PicturePath
    range: string
    inlined: true
    inlined_as_list: true

```
</details>
