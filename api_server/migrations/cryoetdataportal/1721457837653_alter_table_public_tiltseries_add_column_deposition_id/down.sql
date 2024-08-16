DROP INDEX IF EXISTS "public"."tiltseries_deposition_id";
ALTER TABLE "public"."tiltseries" DROP COLUMN "deposition_id" INTEGER NULL;
