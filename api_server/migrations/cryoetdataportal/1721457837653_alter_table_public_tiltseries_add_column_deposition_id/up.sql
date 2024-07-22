ALTER TABLE "public"."tiltseries" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE INDEX "tiltseries_deposition_id" ON "public"."tiltseries" USING btree ("deposition_id");

ALTER TABLE "public"."tiltseries" ADD COLUMN "updated_at" timestamptz NOT NULL DEFAULT now();
COMMENT ON COLUMN public.depositions.updated_at IS 'The last time this db record was modified';
ALTER TABLE "public"."tiltseries" ADD COLUMN "metadata_last_updated_at" timestamptz NULL;
COMMENT ON COLUMN public.depositions.metadata_last_updated_at IS 'The last time this s3 metadata was modified';
