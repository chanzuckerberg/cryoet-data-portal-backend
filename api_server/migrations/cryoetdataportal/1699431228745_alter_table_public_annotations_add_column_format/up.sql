alter table "public"."annotations" add column "annotation_format" varchar null;
comment on column "public"."annotations"."annotation_format" is
E'Format of the annotation object data file';
