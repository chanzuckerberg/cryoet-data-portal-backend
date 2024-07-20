ALTER TABLE "public"."datasets" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE  INDEX "dataset_deposition_id" on "public"."datasets" using btree ("deposition_id");

ALTER TABLE "public"."datasets" ADD COLUMN "db_last_modified_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.depositions.db_last_modified_at IS 'The last time this db record was modified';
ALTER TABLE "public"."datasets" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.depositions.s3_last_modified_at IS 'The last time this s3 metadata was modified';
