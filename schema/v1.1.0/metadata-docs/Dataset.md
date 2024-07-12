# Class: Dataset


_High-level description of a cryoET dataset._





URI: [cdp-meta:Dataset](metadataDataset)




```mermaid
 classDiagram
    class Dataset
      DatestampedEntity <|-- Dataset
      AuthoredEntity <|-- Dataset
      FundedEntity <|-- Dataset
      CrossReferencedEntity <|-- Dataset
      ExperimentalMetadata <|-- Dataset

      Dataset : authors

          Dataset --> Author : authors

      Dataset : cell_component

          Dataset --> CellComponent : cell_component

      Dataset : cell_strain

          Dataset --> CellStrain : cell_strain

      Dataset : cell_type

          Dataset --> CellType : cell_type

      Dataset : cross_references

          Dataset --> CrossReferences : cross_references

      Dataset : dataset_description

      Dataset : dataset_identifier

      Dataset : dataset_title

      Dataset : dates

          Dataset --> DateStamp : dates

      Dataset : funding

          Dataset --> FundingDetails : funding

      Dataset : grid_preparation

      Dataset : organism

          Dataset --> OrganismDetails : organism

      Dataset : other_setup

      Dataset : sample_preparation

      Dataset : sample_type

          Dataset --> sample_type_enum : sample_type

      Dataset : tissue

          Dataset --> TissueDetails : tissue


```





## Inheritance
* **Dataset** [ [DatestampedEntity](DatestampedEntity.md) [AuthoredEntity](AuthoredEntity.md) [FundedEntity](FundedEntity.md) [CrossReferencedEntity](CrossReferencedEntity.md) [ExperimentalMetadata](ExperimentalMetadata.md)]



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [dataset_identifier](dataset_identifier.md) | 1..1 <br/> [Integer](Integer.md) | An identifier for a CryoET dataset, assigned by the Data Portal | direct |
| [dataset_title](dataset_title.md) | 1..1 <br/> [String](String.md) | Title of a CryoET dataset | direct |
| [dataset_description](dataset_description.md) | 1..1 <br/> [String](String.md) | A short description of a CryoET dataset, similar to an abstract for a journal... | direct |
| [dates](dates.md) | 1..1 <br/> [DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modifie... | direct |
| [authors](authors.md) | 1..* <br/> [Author](Author.md) | Author of a scientific data entity | direct |
| [funding](funding.md) | 0..* _recommended_ <br/> [FundingDetails](FundingDetails.md) | A funding source for a scientific data entity (base for JSON and DB represent... | direct |
| [cross_references](cross_references.md) | 0..1 <br/> [CrossReferences](CrossReferences.md) | A set of cross-references to other databases and publications | direct |
| [sample_type](sample_type.md) | 1..1 <br/> [SampleTypeEnum](SampleTypeEnum.md) | Type of sample imaged in a CryoET study | direct |
| [sample_preparation](sample_preparation.md) | 0..1 _recommended_ <br/> [String](String.md) | Describes how the sample was prepared | direct |
| [grid_preparation](grid_preparation.md) | 0..1 _recommended_ <br/> [String](String.md) | Describes Cryo-ET grid preparation | direct |
| [other_setup](other_setup.md) | 0..1 _recommended_ <br/> [String](String.md) | Describes other setup not covered by sample preparation or grid preparation t... | direct |
| [organism](organism.md) | 0..1 <br/> [OrganismDetails](OrganismDetails.md) | The species from which the sample was derived | direct |
| [tissue](tissue.md) | 0..1 <br/> [TissueDetails](TissueDetails.md) | The type of tissue from which the sample was derived | direct |
| [cell_type](cell_type.md) | 0..1 <br/> [CellType](CellType.md) | The cell type from which the sample was derived | direct |
| [cell_strain](cell_strain.md) | 0..1 <br/> [CellStrain](CellStrain.md) | The strain or cell line from which the sample was derived | direct |
| [cell_component](cell_component.md) | 0..1 <br/> [CellComponent](CellComponent.md) | The cellular component from which the sample was derived | direct |









## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:Dataset |
| native | cdp-meta:Dataset |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Dataset
description: High-level description of a cryoET dataset.
from_schema: metadata
mixins:
- DatestampedEntity
- AuthoredEntity
- FundedEntity
- CrossReferencedEntity
- ExperimentalMetadata
attributes:
  dataset_identifier:
    name: dataset_identifier
    description: An identifier for a CryoET dataset, assigned by the Data Portal.
      Used to identify the dataset as the directory name in data tree.
    from_schema: metadata
    exact_mappings:
    - cdp-common:dataset_identifier
    rank: 1000
    alias: dataset_identifier
    owner: Dataset
    domain_of:
    - Dataset
    range: integer
    required: true
    inlined: true
    inlined_as_list: true
  dataset_title:
    name: dataset_title
    description: Title of a CryoET dataset.
    from_schema: metadata
    exact_mappings:
    - cdp-common:dataset_title
    rank: 1000
    alias: dataset_title
    owner: Dataset
    domain_of:
    - Dataset
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  dataset_description:
    name: dataset_description
    description: A short description of a CryoET dataset, similar to an abstract for
      a journal article or dataset.
    from_schema: metadata
    exact_mappings:
    - cdp-common:dataset_description
    rank: 1000
    alias: dataset_description
    owner: Dataset
    domain_of:
    - Dataset
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  dates:
    name: dates
    description: A set of dates at which a data item was deposited, published and
      last modified.
    from_schema: metadata
    alias: dates
    owner: Dataset
    domain_of:
    - DatestampedEntity
    - Dataset
    - Annotation
    range: DateStamp
    required: true
    inlined: true
    inlined_as_list: true
  authors:
    name: authors
    description: Author of a scientific data entity.
    from_schema: metadata
    multivalued: true
    list_elements_ordered: true
    alias: authors
    owner: Dataset
    domain_of:
    - AuthoredEntity
    - Dataset
    - Tomogram
    - Annotation
    range: Author
    required: true
    inlined: true
    inlined_as_list: true
  funding:
    name: funding
    description: A funding source for a scientific data entity (base for JSON and
      DB representation).
    from_schema: metadata
    multivalued: true
    list_elements_ordered: true
    alias: funding
    owner: Dataset
    domain_of:
    - FundedEntity
    - Dataset
    range: FundingDetails
    recommended: true
    inlined: true
    inlined_as_list: true
  cross_references:
    name: cross_references
    description: A set of cross-references to other databases and publications.
    from_schema: metadata
    alias: cross_references
    owner: Dataset
    domain_of:
    - CrossReferencedEntity
    - Dataset
    range: CrossReferences
    inlined: true
    inlined_as_list: true
  sample_type:
    name: sample_type
    description: Type of sample imaged in a CryoET study.
    from_schema: metadata
    exact_mappings:
    - cdp-common:preparation_sample_type
    alias: sample_type
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: sample_type_enum
    required: true
    inlined: true
    inlined_as_list: true
  sample_preparation:
    name: sample_preparation
    description: Describes how the sample was prepared.
    from_schema: metadata
    exact_mappings:
    - cdp-common:sample_preparation
    alias: sample_preparation
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  grid_preparation:
    name: grid_preparation
    description: Describes Cryo-ET grid preparation.
    from_schema: metadata
    exact_mappings:
    - cdp-common:grid_preparation
    alias: grid_preparation
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  other_setup:
    name: other_setup
    description: Describes other setup not covered by sample preparation or grid preparation
      that may make this dataset unique in the same publication.
    from_schema: metadata
    exact_mappings:
    - cdp-common:preparation_other_setup
    alias: other_setup
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  organism:
    name: organism
    description: The species from which the sample was derived.
    from_schema: metadata
    alias: organism
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: OrganismDetails
    inlined: true
    inlined_as_list: true
  tissue:
    name: tissue
    description: The type of tissue from which the sample was derived.
    from_schema: metadata
    alias: tissue
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: TissueDetails
    inlined: true
    inlined_as_list: true
  cell_type:
    name: cell_type
    description: The cell type from which the sample was derived.
    from_schema: metadata
    alias: cell_type
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: CellType
    inlined: true
    inlined_as_list: true
  cell_strain:
    name: cell_strain
    description: The strain or cell line from which the sample was derived.
    from_schema: metadata
    alias: cell_strain
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: CellStrain
    inlined: true
    inlined_as_list: true
  cell_component:
    name: cell_component
    description: The cellular component from which the sample was derived.
    from_schema: metadata
    alias: cell_component
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: CellComponent
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: Dataset
description: High-level description of a cryoET dataset.
from_schema: metadata
mixins:
- DatestampedEntity
- AuthoredEntity
- FundedEntity
- CrossReferencedEntity
- ExperimentalMetadata
attributes:
  dataset_identifier:
    name: dataset_identifier
    description: An identifier for a CryoET dataset, assigned by the Data Portal.
      Used to identify the dataset as the directory name in data tree.
    from_schema: metadata
    exact_mappings:
    - cdp-common:dataset_identifier
    rank: 1000
    alias: dataset_identifier
    owner: Dataset
    domain_of:
    - Dataset
    range: integer
    required: true
    inlined: true
    inlined_as_list: true
  dataset_title:
    name: dataset_title
    description: Title of a CryoET dataset.
    from_schema: metadata
    exact_mappings:
    - cdp-common:dataset_title
    rank: 1000
    alias: dataset_title
    owner: Dataset
    domain_of:
    - Dataset
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  dataset_description:
    name: dataset_description
    description: A short description of a CryoET dataset, similar to an abstract for
      a journal article or dataset.
    from_schema: metadata
    exact_mappings:
    - cdp-common:dataset_description
    rank: 1000
    alias: dataset_description
    owner: Dataset
    domain_of:
    - Dataset
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  dates:
    name: dates
    description: A set of dates at which a data item was deposited, published and
      last modified.
    from_schema: metadata
    alias: dates
    owner: Dataset
    domain_of:
    - DatestampedEntity
    - Dataset
    - Annotation
    range: DateStamp
    required: true
    inlined: true
    inlined_as_list: true
  authors:
    name: authors
    description: Author of a scientific data entity.
    from_schema: metadata
    multivalued: true
    list_elements_ordered: true
    alias: authors
    owner: Dataset
    domain_of:
    - AuthoredEntity
    - Dataset
    - Tomogram
    - Annotation
    range: Author
    required: true
    inlined: true
    inlined_as_list: true
  funding:
    name: funding
    description: A funding source for a scientific data entity (base for JSON and
      DB representation).
    from_schema: metadata
    multivalued: true
    list_elements_ordered: true
    alias: funding
    owner: Dataset
    domain_of:
    - FundedEntity
    - Dataset
    range: FundingDetails
    recommended: true
    inlined: true
    inlined_as_list: true
  cross_references:
    name: cross_references
    description: A set of cross-references to other databases and publications.
    from_schema: metadata
    alias: cross_references
    owner: Dataset
    domain_of:
    - CrossReferencedEntity
    - Dataset
    range: CrossReferences
    inlined: true
    inlined_as_list: true
  sample_type:
    name: sample_type
    description: Type of sample imaged in a CryoET study.
    from_schema: metadata
    exact_mappings:
    - cdp-common:preparation_sample_type
    alias: sample_type
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: sample_type_enum
    required: true
    inlined: true
    inlined_as_list: true
  sample_preparation:
    name: sample_preparation
    description: Describes how the sample was prepared.
    from_schema: metadata
    exact_mappings:
    - cdp-common:sample_preparation
    alias: sample_preparation
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  grid_preparation:
    name: grid_preparation
    description: Describes Cryo-ET grid preparation.
    from_schema: metadata
    exact_mappings:
    - cdp-common:grid_preparation
    alias: grid_preparation
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  other_setup:
    name: other_setup
    description: Describes other setup not covered by sample preparation or grid preparation
      that may make this dataset unique in the same publication.
    from_schema: metadata
    exact_mappings:
    - cdp-common:preparation_other_setup
    alias: other_setup
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  organism:
    name: organism
    description: The species from which the sample was derived.
    from_schema: metadata
    alias: organism
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: OrganismDetails
    inlined: true
    inlined_as_list: true
  tissue:
    name: tissue
    description: The type of tissue from which the sample was derived.
    from_schema: metadata
    alias: tissue
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: TissueDetails
    inlined: true
    inlined_as_list: true
  cell_type:
    name: cell_type
    description: The cell type from which the sample was derived.
    from_schema: metadata
    alias: cell_type
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: CellType
    inlined: true
    inlined_as_list: true
  cell_strain:
    name: cell_strain
    description: The strain or cell line from which the sample was derived.
    from_schema: metadata
    alias: cell_strain
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: CellStrain
    inlined: true
    inlined_as_list: true
  cell_component:
    name: cell_component
    description: The cellular component from which the sample was derived.
    from_schema: metadata
    alias: cell_component
    owner: Dataset
    domain_of:
    - ExperimentalMetadata
    - Dataset
    range: CellComponent
    inlined: true
    inlined_as_list: true

```
</details>
