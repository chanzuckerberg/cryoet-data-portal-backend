alter table "public"."tiltseries" add column "pixel_spacing" numeric null;
comment on column "public"."tiltseries"."pixel_spacing" is E'Pixel spacing equal in both axes in angstrom';
