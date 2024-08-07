
DROP INDEX IF EXISTS "public"."tiltseries_deposition_id";
ALTER TABLE "public"."tiltseries" DROP COLUMN "deposition_id" INTEGER NULL;

DROP INDEX IF EXISTS "public"."dataset_deposition_id";
ALTER TABLE "public"."datasets" DROP COLUMN "deposition_id";

DROP TABLE "public"."deposition_authors" cascade;

DROP INDEX IF EXISTS "public"."depositions_type";
DROP TABLE "public"."depositions" cascade;
