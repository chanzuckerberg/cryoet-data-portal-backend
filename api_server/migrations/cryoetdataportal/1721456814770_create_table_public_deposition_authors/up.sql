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
