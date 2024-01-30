alter table "public"."annotations" add column "is_curator_recommended" boolean
 null default 'false';
comment on column "public"."annotations"."is_curator_recommended" is
E'Data curator’s subjective choice as the best annotation of the same annotation object ID';
