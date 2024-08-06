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
    PRIMARY KEY ("id") , UNIQUE ("id")
);

COMMENT ON TABLE "public"."depositions" IS E'Deposition metadata';
COMMENT ON COLUMN public.depositions.id IS 'Numeric identifier for this depositions';
COMMENT ON COLUMN public.depositions.title IS 'Title for the deposition';
COMMENT ON COLUMN public.depositions.description IS 'Description for the deposition';
COMMENT ON COLUMN public.depositions.release_date IS 'The date the deposition was released';
COMMENT ON COLUMN public.depositions.last_modified_date IS 'The date the deposition was last modified';
COMMENT ON COLUMN public.depositions.deposition_date IS 'The date the deposition was deposited';
COMMENT ON COLUMN public.depositions.related_database_entries IS 'The related database entries to this deposition';
COMMENT ON COLUMN public.depositions.deposition_publications IS 'The publications related to this deposition';
COMMENT ON COLUMN public.depositions.deposition_types IS 'The types of data submitted as a part of this deposition';
COMMENT ON COLUMN public.depositions.s3_prefix IS 'The S3 public bucket path where data about this deposition is contained';
COMMENT ON COLUMN public.depositions.https_prefix IS 'The https directory path where data about this deposition is contained';

CREATE  INDEX "depositions_type" on "public"."depositions" using btree ("deposition_types");
