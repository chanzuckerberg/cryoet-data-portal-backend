

# Slot: dates

URI: [cdp-meta:dates](metadatadates)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DateStampedEntity](DateStampedEntity.md) | An entity with associated deposition, release and last modified dates |  no  |
| [Deposition](Deposition.md) | Metadata describing a deposition |  no  |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |
| [Dataset](Dataset.md) | High-level description of a cryoET dataset |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:dates |
| native | cdp-meta:dates |




## LinkML Source

<details>
```yaml
name: dates
alias: dates
domain_of:
- DateStampedEntity
- Dataset
- Deposition
- Annotation
range: string

```
</details>
