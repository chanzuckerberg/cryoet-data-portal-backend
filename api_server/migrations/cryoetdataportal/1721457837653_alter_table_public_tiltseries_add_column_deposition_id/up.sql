ALTER TABLE "public"."tiltseries" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE INDEX "tiltseries_deposition_id" ON "public"."tiltseries" USING btree ("deposition_id");

COMMENT ON COLUMN public.tiltseries.deposition_id IS 'Reference to the deposition this tiltseries is associated with';
