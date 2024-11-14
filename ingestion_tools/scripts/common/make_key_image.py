import logging
from typing import Any, Iterable, Literal, Optional

import dask
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import skimage
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger("key-image-maker")
logger.setLevel(logging.ERROR)

BinningType = Literal[1, 2, 4]
AnnotationType = list[dict[str, Any]]


class KeyPointAnnotation(BaseModel):
    color: str
    data: list[dict[str, Any]]


class KeyMaskAnnotation(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    color: str
    data: dask.array


def project_slab(
    volume: dask.array,
    projection_depth: int,
    normalize: bool = True,
    binarize: bool = False,
) -> np.ndarray[np.float32]:
    """Project a slab of the given volume along the z-axis.

    Parameters
    ----------
    volume : array
        Volume to project.
    projection_depth : int
        Depth of the projection to slice from the center of the volume.
    normalize : bool, optional
        Whether to normalize the projection.
    binarize : bool, optional
        Whether to binarize the projection.

    Returns
    -------
    projection : array of float32
        Projected slab.
    """
    z_center = volume.shape[0] // 2

    z_min = z_center - projection_depth // 2
    z_max = z_min + projection_depth
    z_slice = np.asarray(volume[z_min:z_max, :, :])

    # generate enhanced center slice
    projection = np.sum(z_slice, axis=0)

    if normalize:
        delta = projection.std()
        mean = projection.mean()
        v_min = mean - 3 * delta
        v_max = mean + 3 * delta

        projection[projection < v_min] = v_min
        projection[projection > v_max] = v_max
        projection = 255 * (projection - v_min) / (v_max - v_min)

    if binarize:
        projection = (projection > 0).astype(np.float32)

    return projection, z_min, z_max


def generate_preview(
    tomogram: dask.array,
    point_annotations: Iterable[KeyPointAnnotation] = None,
    mask_annotations: Iterable[KeyMaskAnnotation] = None,
    *,
    projection_depth: int,
    binning_factor: BinningType = 1,
    point_alpha: float = 0.8,
    mask_alpha: float = 0.1,
) -> np.ndarray[np.uint8]:
    """Generate a preview image of the given tomogram and annotations.

    Parameters
    ----------
    tomogram : dask.array
        Tomogram to slice from.
    point_annotations : Iterable[KeyPointAnnotation], optional
        Point annotations to render.
    mask_annotations : Iterable[KeyMaskAnnotation], optional
        Mask annotations to render.
    projection_depth : int, kw-only
        Depth of the projection to slice from the center of the tomogram.
    binning_factor : {1, 2, 4}, kw-only
        If a binning factor was applied to the given tomogram, the annotations will be scaled down accordingly.
    point_alpha : float, optional
        Alpha value for point annotations.
    mask_alpha : float, optional
        Alpha value for mask annotations.
    cmap : str, optional, kw-only
        MatPlotLib colormap to use.

    Returns
    -------
    preview : np.ndarray[np.uint8]
        Generated preview image.
    """
    if point_annotations is None:
        point_annotations = []

    if mask_annotations is None:
        mask_annotations = []

    projection, z_min, z_max = project_slab(tomogram, projection_depth, normalize=True, binarize=False)

    # marker size should take up at most 5% of the canvas
    marker_size = tomogram.shape[-1] / 10

    # draw initial canvas and slice
    px = 1 / plt.rcParams["figure.dpi"]  # pixel in inches
    tomo_h, tomo_w = tomogram.shape[1:]
    fig, ax = plt.subplots(
        figsize=(tomo_w * px, tomo_h * px),
    )
    ax.imshow(projection, cmap="gray", zorder=0)

    plot_z = 1

    for annotation in mask_annotations:
        cmap = mpl.colors.ListedColormap(["#000000", annotation.color], "binary", N=2)

        mask_projection, _, _ = project_slab(annotation.data, projection_depth, normalize=False, binarize=True)

        ax.imshow(mask_projection, cmap=cmap, alpha=mask_projection * mask_alpha, zorder=plot_z)
        plot_z += 1

    for annotation in point_annotations:
        for item in annotation.data:
            if (location := item.get("location")) is None:
                logger.error("location missing for entry %s", item)
                continue
            try:
                x, y, z = location["x"], location["y"], location["z"]
            except KeyError:
                logger.error(
                    "incorrect format for point location %s",
                    location,
                )
                continue

            if z_min <= z / binning_factor <= z_max:
                # don't bother adding points behind the visible z slice
                plt.scatter(
                    x / binning_factor,
                    y / binning_factor,
                    s=marker_size,
                    c=annotation.color,
                    alpha=point_alpha,
                    marker="o",
                    edgecolors="white",
                    linewidths=marker_size / 100,
                    zorder=plot_z + z,
                )

        plot_z += 1

    # remove the ticks and labels
    ax.set_axis_off()

    # remove top whitespace
    ax.set_anchor("N")

    # render everything
    fig.tight_layout()
    fig.canvas.draw()
    bbox = ax.get_position()

    # convert to numpy array
    data = np.array(fig.canvas.renderer.buffer_rgba())
    factor = round(data.shape[1] / tomo_w)

    # remove whitespace
    y0 = int(bbox.y0 * tomo_h * factor) - 1
    y1 = int(bbox.y1 * tomo_h * factor) - 1
    x0 = int(bbox.x0 * tomo_w * factor) + 1
    x1 = int(bbox.x1 * tomo_w * factor) + 1
    data = data[y0:y1, x0:x1]

    return (data[..., :3]).astype(np.uint8)


def process_key_image(
    image: np.ndarray[np.uint8],
    *,
    aspect_ratio: Optional[str] = "4:3",
    width: Optional[int] = None,
    rotate: bool = False,
) -> np.ndarray[np.uint8]:
    """

    Parameters
    ----------
    image : array of uint8
        Key image to process.
    aspect_ratio : str, optional, kw-only
        Aspect ratio of the image to generate. If ``None``, will not crop the image.
    width : int, optional, kw-only
        Width of the image to generate. If ``None``, will not resample the image.
    rotate : bool, optional, kw-only
        Whether to swap width with height to better match the given aspect ratio.
    """
    if aspect_ratio is not None:
        w_ratio, h_ratio = (int(x) for x in aspect_ratio.split(":"))
        if rotate and image.shape[h_ratio > w_ratio] > image.shape[w_ratio > h_ratio]:
            # longer side does not align with larger aspect ratio side
            # if w_ratio == h_ratio, will never run
            image = np.rot90(image)

        factor = min(image.shape[:2]) // w_ratio
        w = factor * w_ratio
        h = factor * h_ratio
        # offset to crop around center of image
        w_off = (image.shape[1] - w) // 2
        h_off = (image.shape[0] - h) // 2
        image = image[h_off : h_off + h, w_off : w_off + w]

    # resize image
    if width is not None:
        height = image.shape[0] * (width / image.shape[1])
        image = skimage.transform.resize(
            image,
            (height, width),
            anti_aliasing=True,
            preserve_range=True,
        ).astype(np.uint8)

    return image
