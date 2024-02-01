alter table "public"."tomograms" add column "neuroglancer_config" varchar null;
comment on column "public"."tomograms"."neuroglancer_config" is
E'the compact json of neuroglancer config';
