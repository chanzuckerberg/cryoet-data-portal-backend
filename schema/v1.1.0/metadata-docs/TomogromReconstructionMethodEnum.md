# Enum: TomogromReconstructionMethodEnum




_Tomogram reconstruction method_



URI: [TomogromReconstructionMethodEnum](TomogromReconstructionMethodEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| SART | None | Simultaneous Algebraic Reconstruction Technique |
| FOURIER SPACE | None | Fourier space reconstruction |
| SIRT | None | Simultaneous Iterative Reconstruction Technique |
| WBP | None | Weighted Back-Projection |
| UNKNOWN | None | Unknown reconstruction method |




## Slots

| Name | Description |
| ---  | --- |
| [reconstruction_method](reconstruction_method.md) | Describe reconstruction method (Weighted back-projection, SART, SIRT) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata






## LinkML Source

<details>
```yaml
name: tomogrom_reconstruction_method_enum
description: Tomogram reconstruction method
from_schema: metadata
rank: 1000
permissible_values:
  SART:
    text: SART
    description: Simultaneous Algebraic Reconstruction Technique
  FOURIER SPACE:
    text: FOURIER SPACE
    description: Fourier space reconstruction
  SIRT:
    text: SIRT
    description: Simultaneous Iterative Reconstruction Technique
  WBP:
    text: WBP
    description: Weighted Back-Projection
  UNKNOWN:
    text: UNKNOWN
    description: Unknown reconstruction method

```
</details>
