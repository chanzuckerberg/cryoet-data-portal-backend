alter table "public"."tomograms" drop column "https_mrc_scale1" cascade;
alter table "public"."tomograms" drop column "https_mrc_scale2" cascade;
alter table "public"."tomograms" drop column "s3_mrc_scale1" cascade;
alter table "public"."tomograms" drop column "s3_mrc_scale2" cascade;

alter table "public"."tiltseries" drop column "s3_mrc_bin2" cascade;
alter table "public"."tiltseries" drop column "s3_mrc_bin4" cascade;
alter table "public"."tiltseries" drop column "https_mrc_bin2" cascade;
alter table "public"."tiltseries" drop column "https_mrc_bin4" cascade;
