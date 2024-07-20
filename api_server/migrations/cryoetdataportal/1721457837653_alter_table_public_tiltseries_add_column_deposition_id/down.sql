DROP INDEX IF EXISTS "public"."tiltseries_deposition_id";
ALTER TABLE "public"."tiltseries" DROP COLUMN "deposition_id" INTEGER NULL;


ALTER TABLE "public"."tiltseries" DROP COLUMN "db_last_modified_at";
ALTER TABLE "public"."tiltseries" DROP COLUMN "s3_last_modified_at";
