alter table "public"."annotation_files" drop constraint "annotation_files_shape_type_annotation_id_format_key";
alter table "public"."annotation_files" add constraint "annotation_files_shape_type_annotation_id_key" unique ("shape_type", "annotation_id");
