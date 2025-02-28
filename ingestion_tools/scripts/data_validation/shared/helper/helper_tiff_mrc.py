import warnings

import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter


def helper_tiff_mrc_consistent(headers: dict[str, list[tifffile.TiffPage]| MrcInterpreter]):
    """Check that the dimensions (MRC & TIFF) and pixel spacings (MRC) between MRC and/or TIFF files are consistent."""
    errors = []
    dimensions = None
    pixel_spacing = None

    if not headers:
        pytest.skip("No headers to check")

    for filename, header_entity in headers.items():
        if isinstance(header_entity, list) and isinstance(header_entity[0], tifffile.TiffPage):
            curr_dimensions = header_entity[0].shape
            if not all(page.shape == curr_dimensions for page in header_entity):
                errors.append(f"Not all pages have the same dimensions {filename}")

            if dimensions is None:
                dimensions = curr_dimensions
            elif curr_dimensions != dimensions:
                errors.append(
                    f"Dimensions do not match: {curr_dimensions} != {dimensions}, {filename}",
                )
        elif isinstance(header_entity, MrcInterpreter):
            header = header_entity.header
            if dimensions is None:
                dimensions = (header.nx, header.ny)
            elif (header.nx, header.ny) != dimensions:
                errors.append(
                    f"Dimensions do not match: ({header.nx}, {header.ny}) != {dimensions}, {filename}",
                )
            if pixel_spacing is None:
                pixel_spacing = header_entity.voxel_size["x"]
            elif abs(header_entity.voxel_size["x"] - pixel_spacing) > 0.001:
                errors.append(
                    f"Pixel spacing do not match: {header_entity.voxel_size['x']} != {pixel_spacing}, {filename}",
                )

            if abs(header_entity.voxel_size["x"] - header_entity.voxel_size["y"]) > 0.001:
                errors.append(f"Y and X pixel spacings do not match: {header_entity.voxel_size}, {filename}")
        else:
            warnings.warn(f"Unsupported type: {type(header)}, {filename}", stacklevel=2)

    assert not errors, "\n".join(errors)
