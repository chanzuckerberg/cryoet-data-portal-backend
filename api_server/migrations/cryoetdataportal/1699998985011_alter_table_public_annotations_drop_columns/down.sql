alter table "public"."annotations" add column "annotation_format" varchar;
alter table "public"."annotations" add column "https_annotations_path" varchar;
alter table "public"."annotations" add column "s3_annotations_path" varchar;
alter table "public"."annotations" add column "shape_type" varchar;
