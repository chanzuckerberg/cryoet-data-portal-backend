ALTER TABLE "public"."tiltseries" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE INDEX "tiltseries_deposition_id" ON "public"."tiltseries" USING btree ("deposition_id");

ALTER TABLE "public"."tiltseries" ADD COLUMN "db_last_modified_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.depositions.db_last_modified_at IS 'The last time this db record was modified';
ALTER TABLE "public"."tiltseries" ADD COLUMN "s3_last_modified_at" timestamptz NULL;
COMMENT ON COLUMN public.depositions.s3_last_modified_at IS 'The last time this s3 metadata was modified';
