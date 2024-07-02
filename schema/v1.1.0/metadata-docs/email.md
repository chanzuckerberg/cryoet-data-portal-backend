

# Slot: email


_The email address of the author._



URI: [cdp-meta:email](metadataemail)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Author](Author.md) | Author of a scientific data entity |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: email
description: The email address of the author.
from_schema: metadata
exact_mappings:
- cdp-common:author_email
rank: 1000
alias: email
owner: Author
domain_of:
- Author
range: string
inlined: true
inlined_as_list: true

```
</details>