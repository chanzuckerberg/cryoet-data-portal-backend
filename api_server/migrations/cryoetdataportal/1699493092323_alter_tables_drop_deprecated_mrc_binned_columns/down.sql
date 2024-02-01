alter table "public"."tomograms" add column "https_mrc_scale1" varchar null;
comment on column "public"."tomograms"."https_mrc_scale1" is
E'https path to this tomogram in MRC format (downscaled to 50%)';

alter table "public"."tomograms" add column "https_mrc_scale2" varchar null;
comment on column "public"."tomograms"."https_mrc_scale2" is
E'https path to this tomogram in MRC format (downscaled to 25%)';

alter table "public"."tomograms" add column "s3_mrc_scale1" varchar null;
comment on column "public"."tomograms"."s3_mrc_scale1" is
E's3 path to this tomogram in MRC format (downscaled to 50%)';

alter table "public"."tomograms" add column "s3_mrc_scale2" varchar null;
comment on column "public"."tomograms"."s3_mrc_scale2" is
E's3 path to this tomogram in MRC format (downscaled to 25%)';

alter table "public"."tiltseries" add column "https_mrc_bin2" varchar null;
comment on column "public"."tiltseries"."https_mrc_bin2" is
E'https path to this tiltseries in MRC format (downscaled to 50%)';

alter table "public"."tiltseries" add column "https_mrc_bin4" varchar null;
comment on column "public"."tiltseries"."https_mrc_bin4" is
E'https path to this tiltseries in MRC format (downscaled to 25%)';

alter table "public"."tiltseries" add column "s3_mrc_bin2" varchar null;
comment on column "public"."tiltseries"."s3_mrc_bin2" is
E's3 path to this tiltseries in MRC format (downscaled to 50%)';

alter table "public"."tiltseries" add column "s3_mrc_bin4" varchar null;
comment on column "public"."tiltseries"."s3_mrc_bin4" is
E's3 path to this tiltseries in MRC format (downscaled to 25%)';
