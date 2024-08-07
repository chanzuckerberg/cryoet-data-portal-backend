DROP INDEX IF EXISTS "public"."dataset_deposition_id";
ALTER TABLE "public"."datasets" DROP COLUMN "deposition_id";
