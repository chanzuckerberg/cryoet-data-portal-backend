alter table "public"."tomograms" add column "affine_transformation_matrix" numeric[4][4]
 null;
comment on column "public"."tomograms"."affine_transformation_matrix" is
E'The flip or rotation transformation of this author submitted tomogram is indicated here'
