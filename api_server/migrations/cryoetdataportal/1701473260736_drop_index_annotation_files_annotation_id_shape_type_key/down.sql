CREATE  INDEX "annotation_files_annotation_id_shape_type_key" on
  "public"."annotation_files" using btree ("annotation_id", "shape_type");
