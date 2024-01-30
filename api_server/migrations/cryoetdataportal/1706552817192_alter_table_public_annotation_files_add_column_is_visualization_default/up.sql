alter table "public"."annotation_files" add column "is_visualization_default" boolean
 null default 'false';
comment on column "public"."annotation_files"."is_visualization_default" is
E'Data curator’s subjective choice of default annotation to display in visualization for an object';
