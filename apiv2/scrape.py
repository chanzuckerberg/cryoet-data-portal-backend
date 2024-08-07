import json

import cryoet_data_portal as cdp

from database import models
from platformics.database.connect import init_sync_db

# cleanup:
# delete from tomogram_author ; delete from dataset_author ; delete from annotation_author ; delete from dataset_funding ; delete from annotation_file; delete from annotation; delete from tomogram; delete from tomogram_voxel_spacing; delete from tiltseries; delete from run; delete from dataset;


def add(session, model, item, parents):
    item_dict = item.to_dict()

    if model == models.Tiltseries:
        item_dict.pop("frames_count")
        item_dict.pop("https_alignment_file")
        item_dict.pop("s3_alignment_file")
    if model == models.AnnotationAuthor and not item_dict.get("author_list_order"):
        # TODO, super hacky!
        item_dict["author_list_order"] = 1
    if model == models.Annotation:
        del item_dict["tomogram_voxel_spacing_id"]
    if "deposition_id" in item_dict:  # Temporary hack
        del item_dict["deposition_id"]
    if "affine_transformation_matrix" in item_dict:
        item_dict["affine_transformation_matrix"] = json.dumps(item_dict["affine_transformation_matrix"])
    if "type" in item_dict:
        item_dict["tomogram_type"] = item_dict["type"]
        del item_dict["type"]
    if "dataset_publications" in item_dict:
        item_dict["publications"] = item_dict.pop("dataset_publications")
    if "primary_annotator_status" in item_dict:
        item_dict["primary_author_status"] = item_dict.pop("primary_annotator_status") or False
    if "corresponding_annotator_status" in item_dict:
        item_dict["corresponding_author_status"] = item_dict.pop("corresponding_annotator_status") or False
    if "reconstruction_method" in item_dict:
        item_dict["is_standardized"] = item_dict.get("is_standardized") or False
    if "reconstruction_method" in item_dict:
        if "weighted" in item_dict["reconstruction_method"].lower():
            item_dict["reconstruction_method"] = "WBP"
        elif "iterative" in item_dict["reconstruction_method"].lower():
            item_dict["reconstruction_method"] = "SIRT"
        elif "algebraic" in item_dict["reconstruction_method"].lower():
            item_dict["reconstruction_method"] = "SART"
        elif "fourier" in item_dict["reconstruction_method"].lower():
            item_dict["reconstruction_method"] = "Fourier Space"
        else:
            print(f"Error: could not map reconstruction method {item_dict['reconstruction_method']}")
            item_dict["reconstruction_method"] = None

    for parentkey, parentid in parents.items():
        item_dict[parentkey] = parentid

    item = model(**item_dict)
    session.add(item)
    session.flush()
    return item


def do_import():
    annotation = models.Annotation
    client = cdp.Client()
    db = init_sync_db("postgresql+psycopg://postgres:password_postgres@platformics-db:5432/platformics")
    with db.session() as session:
        for dataset in cdp.Dataset.find(client):
            print(dataset)
            ds = add(session, models.Dataset, dataset, {})
            for dsauthor in cdp.DatasetAuthor.find(client, [cdp.DatasetAuthor.dataset_id == dataset.id]):
                dsa = add(session, models.DatasetAuthor, dsauthor, {"dataset_id": ds.id})
            for dsfunding in cdp.DatasetFunding.find(client, [cdp.DatasetFunding.dataset_id == dataset.id]):
                dsf = add(session, models.DatasetFunding, dsfunding, {"dataset_id": ds.id})
            for run in cdp.Run.find(client, [cdp.Run.dataset_id == dataset.id]):
                r = add(session, models.Run, run, {"dataset_id": ds.id})
                for vs in cdp.TomogramVoxelSpacing.find(client, [cdp.TomogramVoxelSpacing.run_id == run.id]):
                    v = add(session, models.TomogramVoxelSpacing, vs, {"run_id": r.id})
                    for tomo in cdp.Tomogram.find(client, [cdp.Tomogram.tomogram_voxel_spacing_id == vs.id]):
                        t = add(session, models.Tomogram, tomo, {"tomogram_voxel_spacing_id": v.id})
                        for tomoauthor in cdp.TomogramAuthor.find(client, [cdp.TomogramAuthor.tomogram_id == tomo.id]):
                            ta = add(session, models.TomogramAuthor, tomoauthor, {"tomogram_id": t.id})
                    for anno in cdp.Annotation.find(client, [cdp.Annotation.tomogram_voxel_spacing_id == vs.id]):
                        a = add(session, models.Annotation, anno, {"run_id": r.id})
                        # TODO this needs a bit of work.
                        # for annofile in cdp.AnnotationFile.find(client, [cdp.AnnotationFile.annotation_id == anno.id]):
                        #     af = add(session, models.AnnotationFile, annofile, {"annotation_id": a.id})
                        for annoauthor in cdp.AnnotationAuthor.find(
                            client,
                            [cdp.AnnotationAuthor.annotation_id == anno.id],
                        ):
                            aa = add(session, models.AnnotationAuthor, annoauthor, {"annotation_id": a.id})
                for tiltseries in cdp.TiltSeries.find(client, [cdp.TiltSeries.run_id == run.id]):
                    ts = add(session, models.Tiltseries, tiltseries, {"run_id": r.id})
                print(f"run {dataset.id}/{run.name} done")
                session.commit()
            print(f"dataset {dataset.id} done")
            session.commit()
        print("done")
        session.commit()
    return annotation


if __name__ == "__main__":
    do_import()
