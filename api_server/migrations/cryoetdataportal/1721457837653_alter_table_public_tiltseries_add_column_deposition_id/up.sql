ALTER TABLE "public"."tiltseries" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE INDEX "tiltseries_deposition_id" ON "public"."tiltseries" USING btree ("deposition_id");
