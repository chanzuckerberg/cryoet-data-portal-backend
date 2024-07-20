ALTER TABLE "public"."annotation_authors" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.annotation_authors.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."annotation_authors" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.annotation_authors.s3_last_modified_at IS 'The last time this s3 metadata was modified';

ALTER TABLE "public"."annotation_files" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.annotation_files.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."annotation_files" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.annotation_files.s3_last_modified_at IS 'The last time this s3 metadata was modified';

ALTER TABLE "public"."annotations" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.annotations.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."annotations" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.annotations.s3_last_modified_at IS 'The last time this s3 metadata was modified';

ALTER TABLE "public"."dataset_authors" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.dataset_authors.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."dataset_authors" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.dataset_authors.s3_last_modified_at IS 'The last time this s3 metadata was modified';

ALTER TABLE "public"."dataset_funding" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.dataset_funding.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."dataset_funding" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.dataset_funding.s3_last_modified_at IS 'The last time this s3 metadata was modified';

ALTER TABLE "public"."runs" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.runs.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."runs" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.runs.s3_last_modified_at IS 'The last time this s3 metadata was modified';

ALTER TABLE "public"."tomogram_authors" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.tomogram_authors.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."tomogram_authors" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.tomogram_authors.s3_last_modified_at IS 'The last time this s3 metadata was modified';

ALTER TABLE "public"."tomogram_voxel_spacings" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.tomogram_voxel_spacings.updated_at IS 'The last time this db record was modified';

ALTER TABLE "public"."tomograms" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.tomograms.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."tomograms" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.tomograms.s3_last_modified_at IS 'The last time this s3 metadata was modified';
