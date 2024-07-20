alter table "public"."annotation_authors" drop column "updated_at";
alter table "public"."annotation_authors" drop column "s3_last_modified_at";

alter table "public"."annotation_files" drop column "updated_at";
alter table "public"."annotation_files" drop column "s3_last_modified_at";

alter table "public"."annotations" drop column "updated_at";
alter table "public"."annotations" drop column "s3_last_modified_at";

alter table "public"."dataset_authors" drop column "updated_at";
alter table "public"."dataset_authors" drop column "s3_last_modified_at";

alter table "public"."dataset_funding" drop column "updated_at";
alter table "public"."dataset_funding" drop column "s3_last_modified_at";

alter table "public"."runs" drop column "updated_at";
alter table "public"."runs" drop column "s3_last_modified_at";

alter table "public"."tomogram_authors" drop column "updated_at";
alter table "public"."tomogram_authors" drop column "s3_last_modified_at";

alter table "public"."tomogram_voxel_spacings" drop column "updated_at";

alter table "public"."tomograms" drop column "updated_at";
alter table "public"."tomograms" drop column "s3_last_modified_at";
