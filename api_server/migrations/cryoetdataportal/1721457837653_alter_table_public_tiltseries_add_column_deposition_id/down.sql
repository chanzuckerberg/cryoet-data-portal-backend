DROP INDEX IF EXISTS "public"."tiltseries_deposition_id";
ALTER TABLE "public"."tiltseries" DROP COLUMN "deposition_id" INTEGER NULL;


ALTER TABLE "public"."tiltseries" DROP COLUMN "updated_at";
ALTER TABLE "public"."tiltseries" DROP COLUMN "metadata_last_updated_at";
