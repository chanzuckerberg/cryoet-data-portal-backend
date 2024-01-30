CREATE  INDEX "annotation_files_unique_key" on
  "public"."annotation_files" using btree ("annotation_id", "format", "shape_type");
