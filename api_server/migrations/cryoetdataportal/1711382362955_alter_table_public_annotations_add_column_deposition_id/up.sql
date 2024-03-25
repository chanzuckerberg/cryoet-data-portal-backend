alter table "public"."annotations" add column "deposition_id" integer null;
comment on column "public"."annotations"."deposition_id" is E'id of the associated deposition.';
