CREATE TABLE "public"."depositions" (
    "id" serial NOT NULL,
    "title" varchar NOT NULL,
    "description" varchar NOT NULL,
    "deposition_date" date NOT NULL,
    "release_date" date NOT NULL,
    "last_modified_date" date NOT NULL,
    "related_database_entries" varchar,
    "deposition_publications" varchar,
    "deposition_types" varchar NOT NULL,
    "s3_prefix" varchar,
    "https_prefix" varchar,
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    "metadata_last_updated_at" timestamptz,
    "global_id" varchar NOT NULL,
    PRIMARY KEY ("id") , UNIQUE ("id"), UNIQUE ("global_id")
);

COMMENT ON TABLE "public"."depositions" IS E'Deposition metadata';
COMMENT ON COLUMN public.depositions.id IS 'Numeric identifier for this depositions';
COMMENT ON COLUMN public.depositions.title IS 'Title for the deposition';
COMMENT ON COLUMN public.depositions.description IS 'Description for the deposition';
COMMENT ON COLUMN public.depositions.release_date IS 'The date the deposition was released';
COMMENT ON COLUMN public.depositions.last_modified_date IS 'The date the deposition was last modified';
COMMENT ON COLUMN public.depositions.deposition_date IS 'The date the deposition was deposited';
COMMENT ON COLUMN public.depositions.deposition_publications IS 'The publications related to this deposition';
COMMENT ON COLUMN public.depositions.related_database_entries IS 'The related database entries to this deposition';
COMMENT ON COLUMN public.depositions.s3_prefix IS 'The S3 public bucket path where data about this deposition is contained';
COMMENT ON COLUMN public.depositions.https_prefix IS 'The https directory path where data about this deposition is contained';
COMMENT ON COLUMN public.depositions.updated_at IS 'The last time this db record was modified';
COMMENT ON COLUMN public.depositions.metadata_last_updated_at IS 'The last time this s3 metadata was modified';
COMMENT ON COLUMN public.depositions.global_id IS 'The global_id associated with this deposition';

CREATE  INDEX "depositions_type" on "public"."depositions" using btree ("deposition_types");
