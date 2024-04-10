import csv
from dataclasses import asdict, dataclass

import click
import numpy as np
from scipy.io import loadmat

from common.fs import FileSystemApi


@dataclass
class CtfParameters:
    spherical_aberration: float  # mm
    amplitude_contrast: float


@dataclass
class Defocus:
    defocus_1: float  # micron
    defocus_2: float  # micron
    defocus_angle: float  # degrees


@dataclass
class TomomanData:
    """Dataclass for Tomoman data"""

    root_dir: str
    stack_dir: str
    frame_dir: str
    mdoc_name: str
    tomo_num: int
    collected_tilts: list[float]  # degrees, in order of acquisition
    frame_names: list[str]  # in order of acquisition
    n_frames: int
    pixelsize: float  # Angstrom
    image_size: tuple[int, int]  # Pixels
    voltage: float  # V
    cumulative_exposure_time: list[float]
    dose: list[float]  # e/A^2, cumulative, ordered by acquisition, before exclusion
    target_defocus: float  # micron
    gainref: str
    defects_file: str
    rotate_gain: float
    flip_gain: float
    raw_stack_name: str
    mirror_stack: bool
    skip: bool
    frames_aligned: bool
    frame_alignment_algorithm: str
    stack_name: str
    clean_stack: bool
    removed_tilts: list[float]  # degrees
    rawtlt: list[float]  # degrees, ordered low to high
    max_tilt: float  # degrees (after removal)
    min_tilt: float  # degrees (after removal)
    tilt_axis_angle: float  # degrees
    dose_filtered: bool
    dose_filtered_stack_name: str
    dose_filter_algorithm: str
    imod_preprocessed: bool
    stack_aligned: bool
    alignment_stack: str
    alignment_software: str
    ctf_determined: bool
    ctf_parameters: CtfParameters
    ctf_determination_algorithm: str
    determined_defocii: Defocus
    tomo_recons: bool
    tomo_recons_algorithm: str
    metadata: dict[any, any]

    @classmethod
    def from_record(cls, record: np.ndarray):
        root_dir = str(record["root_dir"][0])
        stack_dir = str(record["stack_dir"][0])
        frame_dir = str(record["frame_dir"][0])
        mdoc_name = str(record["frame_dir"][0])
        tomo_num = int(record["tomo_num"][0][0])
        collected_tilts = [float(it[0]) for it in record["collected_tilts"].tolist()]
        frame_names = [str(n[0][0]) for n in record["frame_names"]]
        n_frames = int(record["n_frames"][0][0])
        pixelsize = float(record["pixelsize"][0][0])
        image_size = (int(record["image_size"][0][0]), int(record["image_size"][0][1]))
        voltage = float(record["voltage"][0][0]) * 1000
        cumulative_exposure_time = [float(it[0]) for it in record["cumulative_exposure_time"]]
        dose = [float(it[0]) for it in record["dose"]]
        target_defocus = float(record["target_defocus"][0][0])
        gainref = str(record["gainref"][0])
        defects_file = str(record["defects_file"][0]) if record["defects_file"].size > 0 else ""
        rotate_gain = float(record["rotate_gain"][0][0])
        flip_gain = float(record["flip_gain"][0][0])
        raw_stack_name = str(record["raw_stack_name"][0])
        mirror_stack = str(record["mirror_stack"][0]) == "y"
        skip = record["skip"][0][0] != 0
        frames_aligned = record["frames_aligned"][0][0] != 0
        frame_alignment_algorithm = str(record["frame_alignment_algorithm"][0])
        stack_name = str(record["stack_name"][0])
        clean_stack = record["clean_stack"][0][0] != 0
        removed_tilts = [float(it[0]) for it in record["removed_tilts"]]
        rawtlt = [float(it[0]) for it in record["rawtlt"]]
        max_tilt = float(record["max_tilt"][0][0])
        min_tilt = float(record["min_tilt"][0][0])
        tilt_axis_angle = float(record["tilt_axis_angle"][0][0])
        dose_filtered = record["dose_filtered"][0][0] != 0
        dose_filtered_stack_name = str(record["dose_filtered_stack_name"][0])
        dose_filter_algorithm = str(record["dose_filter_algorithm"][0])
        imod_preprocessed = record["imod_preprocessed"][0][0] != 0
        stack_aligned = record["stack_aligned"][0][0] != 0
        alignment_stack = str(record["alignment_stack"][0])
        alignment_software = str(record["alignment_software"][0])
        ctf_determined = record["ctf_determined"][0][0] != 0
        ctf_parameters = CtfParameters(
            float(record["ctf_parameters"][0][0][0][0][0]),
            float(record["ctf_parameters"][0][0][1][0][0]),  # lol
        )
        ctf_determination_algorithm = str(record["ctf_determination_algorithm"][0])
        determined_defocii = Defocus(
            float(record["determined_defocii"][0][0]),
            float(record["determined_defocii"][0][1]),
            float(record["determined_defocii"][0][2]),
        )
        tomo_recons = record["tomo_recons"][0][0] != 0
        tomo_recons_algorithm = str(record["tomo_recons_algorithm"])
        metadata = {}

        return cls(
            root_dir,
            stack_dir,
            frame_dir,
            mdoc_name,
            tomo_num,
            collected_tilts,
            frame_names,
            n_frames,
            pixelsize,
            image_size,
            voltage,
            cumulative_exposure_time,
            dose,
            target_defocus,
            gainref,
            defects_file,
            rotate_gain,
            flip_gain,
            raw_stack_name,
            mirror_stack,
            skip,
            frames_aligned,
            frame_alignment_algorithm,
            stack_name,
            clean_stack,
            removed_tilts,
            rawtlt,
            max_tilt,
            min_tilt,
            tilt_axis_angle,
            dose_filtered,
            dose_filtered_stack_name,
            dose_filter_algorithm,
            imod_preprocessed,
            stack_aligned,
            alignment_stack,
            alignment_software,
            ctf_determined,
            ctf_parameters,
            ctf_determination_algorithm,
            determined_defocii,
            tomo_recons,
            tomo_recons_algorithm,
            metadata,
        )


@dataclass
class PortalOutput:
    run_name: str
    annotation_micrograph_name: str
    frame_gain_reference: str
    tilt_series_min_tilt: float
    tilt_series_max_tilt: float
    tilt_series_tilt_axis_angle: float
    tilt_series_total_flux: float

    @classmethod
    def from_tomoman(cls, record: TomomanData):
        # collected_tilts has all acquired tilts in acquisition order before excluding tilts
        # rawtlt has all remaining tilts, ordered low to high after excluding bad tilts
        # need to find the index into dose (cumulative dose) of the angle that was last acquired to find total flux
        # step backward through collected_tilts to find the last acquired tilt remaining in rawtlt
        last_tilt = record.collected_tilts[-1]
        for tilt in reversed(record.collected_tilts):
            if tilt in record.rawtlt:
                last_tilt = tilt
                break

        idx = record.collected_tilts.index(last_tilt)
        tilt_series_total_flux = record.dose[idx]

        return cls(
            run_name=record.stack_dir.replace(record.root_dir, "").strip("/"),
            frame_gain_reference=record.gainref.replace(record.root_dir, "").strip("/"),
            annotation_micrograph_name=str(record.tomo_num),
            tilt_series_min_tilt=record.min_tilt,
            tilt_series_max_tilt=record.max_tilt,
            tilt_series_tilt_axis_angle=record.tilt_axis_angle,
            tilt_series_total_flux=tilt_series_total_flux,
        )


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.argument("tomoman_file", required=True, type=str)
@click.argument("output_file", required=True, type=str)
@click.pass_context
def convert(ctx, tomoman_file: str, output_file: str):
    fs = FileSystemApi.get_fs_api(mode="s3", force_overwrite=True)
    local_file = fs.localreadable(tomoman_file)

    records = loadmat(local_file)["tomolist"][0]
    data = [TomomanData.from_record(record) for record in records]

    with fs.open(output_file, "w") as f:
        head = asdict(PortalOutput.from_tomoman(data[0])).keys()
        writer = csv.DictWriter(f, fieldnames=head, delimiter="\t")
        writer.writeheader()

        for d in data:
            writer.writerow(asdict(PortalOutput.from_tomoman(d)))


if __name__ == "__main__":
    cli()
