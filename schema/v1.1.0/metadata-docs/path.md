# Slot: path


_Path to the annotation file relative to the dataset root._



URI: [cdp-meta:path](metadatapath)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[AnnotationFile](AnnotationFile.md) | Metadata describing a file containing an annotation |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: path
description: Path to the annotation file relative to the dataset root.
from_schema: metadata
exact_mappings:
- cdp-common:annotation_file_path
rank: 1000
alias: path
owner: AnnotationFile
domain_of:
- AnnotationFile
range: string
inlined: true
inlined_as_list: true

```
</details>