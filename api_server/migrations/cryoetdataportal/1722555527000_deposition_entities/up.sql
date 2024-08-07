
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

CREATE TABLE "public"."deposition_authors" (
    "id" serial NOT NULL,
    "name" varchar NOT NULL,
    "orcid" varchar,
    "corresponding_author_status" boolean DEFAULT false,
    "email" varchar,
    "affiliation_name" varchar,
    "affiliation_address" varchar,
    "affiliation_identifier" varchar,
    "deposition_id" integer NOT NULL,
    "primary_author_status" boolean DEFAULT false,
    "author_list_order" integer NOT NULL,
    PRIMARY KEY ("id") ,
    FOREIGN KEY ("deposition_id") REFERENCES "public"."depositions"("id") ON UPDATE restrict ON DELETE restrict,
    UNIQUE ("id")
);

COMMENT ON TABLE "public"."deposition_authors" IS E'Authors for a deposition';
COMMENT ON COLUMN public.deposition_authors.id IS 'Numeric identifier for this deposition author (this may change!)';
COMMENT ON COLUMN public.deposition_authors.author_list_order IS 'The order in which the author appears in the publication';
COMMENT ON COLUMN public.deposition_authors.deposition_id IS 'Reference to the deposition this author contributed to';
COMMENT ON COLUMN public.deposition_authors.name IS 'Full name of a deposition author (e.g. Jane Doe).';
COMMENT ON COLUMN public.deposition_authors.orcid IS 'A unique, persistent identifier for researchers, provided by ORCID.';
COMMENT ON COLUMN public.deposition_authors.corresponding_author_status IS 'Indicates whether an author is the corresponding author';
COMMENT ON COLUMN public.deposition_authors.primary_author_status IS 'Indicates whether an author is the main person creating the deposition';
COMMENT ON COLUMN public.deposition_authors.email IS 'Email address for this author';
COMMENT ON COLUMN public.deposition_authors.affiliation_name IS 'Name of the institution an author is affiliated with.';
COMMENT ON COLUMN public.deposition_authors.affiliation_address IS 'Address of the institution an author is affiliated with.';
COMMENT ON COLUMN public.deposition_authors.affiliation_identifier IS 'A unique identifier assigned to the affiliated institution by The Research Organization Registry (ROR).';

ALTER TABLE "public"."datasets" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE  INDEX "dataset_deposition_id" on "public"."datasets" using btree ("deposition_id");

COMMENT ON COLUMN public.datasets.deposition_id IS 'Reference to the deposition this dataset is associated with';

ALTER TABLE "public"."tiltseries" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE INDEX "tiltseries_deposition_id" ON "public"."tiltseries" USING btree ("deposition_id");

COMMENT ON COLUMN public.tiltseries.deposition_id IS 'Reference to the deposition this tiltseries is associated with';
