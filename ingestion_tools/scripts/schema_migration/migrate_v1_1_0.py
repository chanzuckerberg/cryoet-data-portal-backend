from typing import Union

import numpy as np


def rawtilts_to_collection_metadata(config: dict) -> None:
    if "rawtilts" not in config:
        return

    list_globs = []
    for i in config["rawtilts"]:
        if "sources" not in i:
            continue
        old_source = i["sources"][0]["source_multi_glob"]["list_globs"]
        list_globs.extend(s for s in old_source if s.endswith(".mdoc"))
        for source in list_globs:
            old_source.remove(source)
    if list_globs:
        if "collection_metadata" not in config:
            config["collection_metadata"] = [{"sources": [{"source_multi_glob": {"list_globs": []}}]}]
        config["collection_metadata"][0]["sources"][0]["source_multi_glob"]["list_globs"].extend(list_globs)


def rawtilts_to_alignments(data: dict) -> None:
    list_globs = []
    format_dict = {
        "IMOD": [],
        "ARETOMO3": [],
    }

    imod_ext = [".tlt", ".xf", ".com", ".xtilt"]
    aretomo3_ext = [".aln", ".txt", ".csv"]
    extensions = imod_ext + aretomo3_ext

    def valid_file(file):
        return any(file.endswith(ext) for ext in extensions)

    def get_format(file):
        if any(file.endswith(ext) for ext in imod_ext):
            format_dict["IMOD"].append(file)
        elif any(file.endswith(ext) for ext in aretomo3_ext):
            format_dict["ARETOMO3"].append(file)

    if len(data.get("tomograms", [])) > 1 or len(data.get("rawtilts", [])) > 1:
        raise ValueError("More than one tomogram or rawtilt")

    if "rawtilts" not in data:
        return

    for rawtilt in data["rawtilts"]:
        if "sources" not in rawtilt:
            continue
        old_source = rawtilt["sources"][0]["source_multi_glob"]["list_globs"]
        list_globs.extend(s for s in old_source if valid_file(s))
        for source in list_globs:
            old_source.remove(source)
            get_format(source)

    if not list_globs:
        return

    if "alignments" not in data:
        data["alignments"] = []
    for key, files in format_dict.items():
        if not files:
            continue
        # check if there is an alignment with the key in the metadata.format
        alignment = [a for a in data.get("alignments", []) if a["metadata"]["format"] == key]
        if alignment:
            alignment = alignment.pop()
            alignment["sources"][0]["source_multi_glob"]["list_globs"].extend(files)
        else:
            alignment = {"metadata": {"format": key}, "sources": [{"source_multi_glob": {"list_globs": files}}]}
            data["alignments"].append(alignment)

        if "tomograms" not in data:
            continue

        for tomo in data["tomograms"]:
            if "metadata" not in tomo:
                continue
            affine_transformation_matrix = tomo["metadata"].get("affine_transformation_matrix")
            if affine_transformation_matrix and np.allclose(affine_transformation_matrix, np.eye(4)):
                # skip if is an idenity matrix
                continue
            if affine_transformation_matrix:
                alignment["metadata"]["affine_transformation_matrix"] = affine_transformation_matrix


def update_alignment_metadata(data: dict) -> None:
    if "tomograms" not in data or "alignments" not in data:
        return
    for alignment in data["alignments"]:
        for tomo in data["tomograms"]:
            if "metadata" not in tomo:
                continue
            tomo_metadata = tomo["metadata"]
            fiducial_alignment_status = tomo_metadata.get("fiducial_alignment_status", "NON_FIDUCIAL")
            reconstruction_software = (tomo_metadata.get("reconstruction_software") or "").lower()
            if fiducial_alignment_status == "FIDUCIAL":
                alignment["metadata"]["method_type"] = "fiducial_based"
            elif "aretomo" in reconstruction_software:  # aretomo3 software name can contain version
                alignment["metadata"]["method_type"] = "projection_matching"
            elif "imod" in reconstruction_software:
                alignment["metadata"]["method_type"] = "patch_tracking"


def update_tomogram_metadata(config: dict) -> None:
    tomograms = config.get("tomograms")
    if not tomograms:
        return

    for tomogram in tomograms:
        metadata = tomogram.get("metadata")
        if not metadata:
            continue
        metadata["is_visualization_default"] = True
        if not metadata.get("dates"):
            dates = config["depositions"][0]["metadata"]["dates"]
            metadata["dates"] = dates
        affine_transformation_matrix = metadata.get("affine_transformation_matrix", None)
        if not affine_transformation_matrix:
            metadata["affine_transformation_matrix"] = np.eye(4, dtype=int).tolist()


def update_annotation_sources(config: dict) -> None:
    annotations = config.get("annotations")
    if not annotations:
        return
    for annotation in annotations:
        sources = annotation.get("sources")
        if not sources:
            continue


def remove_empty_fields(config: Union[list, dict]) -> None:
    remove_key = []
    exclude_keys = ["annotations"]
    if isinstance(config, list):
        for i in config:
            if not isinstance(i, (list, dict)):
                continue
            remove_empty_fields(i)
            if len(i) == 0:
                remove_key.append(i)
        if remove_key:
            for key in remove_key:
                config.remove(key)
    elif isinstance(config, dict):
        for key, value in config.items():
            if not isinstance(value, (list, dict)):
                continue
            remove_empty_fields(value)
            if len(value) == 0:
                remove_key.append(key)
        if not remove_key:
            return
        for key in remove_key:
            if key in exclude_keys:
                continue
            config.pop(key)


def check_deposition(config: dict) -> bool:
    if "depositions" in config:
        return True
    raise ValueError("depositions is not in the config")


def upgrade(config: dict) -> dict:
    rawtilts_to_collection_metadata(config)
    rawtilts_to_alignments(config)
    update_alignment_metadata(config)
    update_tomogram_metadata(config)
    check_deposition(config)
    update_annotation_sources(config)
    remove_empty_fields(config)
    config["version"] = "1.1.0"
    return config
