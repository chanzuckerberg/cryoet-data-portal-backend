DROP INDEX IF EXISTS "public"."dataset_deposition_id";
ALTER TABLE "public"."datasets" DROP COLUMN "deposition_id";
ALTER TABLE "public"."datasets" DROP COLUMN "updated_at";
ALTER TABLE "public"."datasets" DROP COLUMN "s3_last_modified_at";
