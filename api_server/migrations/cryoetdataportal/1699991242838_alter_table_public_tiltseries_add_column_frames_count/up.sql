alter table "public"."tiltseries" add column "frames_count" integer null default '0';
comment on column "public"."tiltseries"."frames_count" is
E'Number of frames associated to the tilt series';
