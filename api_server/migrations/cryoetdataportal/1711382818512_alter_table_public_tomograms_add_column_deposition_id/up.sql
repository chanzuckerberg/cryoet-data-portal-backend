alter table "public"."tomograms" add column "deposition_id" integer null;
comment on column "public"."tomograms"."deposition_id" is E'id of the associated deposition.';
