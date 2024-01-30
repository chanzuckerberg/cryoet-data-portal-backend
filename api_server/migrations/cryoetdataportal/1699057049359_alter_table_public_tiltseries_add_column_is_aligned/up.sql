alter table "public"."tiltseries" add column "is_aligned" boolean not null default 'false';
comment on column "public"."tiltseries"."is_aligned" is E'Tilt series is aligned';
