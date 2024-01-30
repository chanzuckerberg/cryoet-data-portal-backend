alter table "public"."annotations" drop column "annotation_format" cascade;
alter table "public"."annotations" drop column "https_annotations_path" cascade;
alter table "public"."annotations" drop column "s3_annotations_path" cascade;
alter table "public"."annotations" drop column "shape_type" cascade;
