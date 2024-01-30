alter table "public"."tiltseries" add column "aligned_tiltseries_binning" integer
 null;
COMMENT ON COLUMN public.tiltseries.aligned_tiltseries_binning IS
E'The binning factor between the unaligned tilt series and the aligned tiltseries.';
