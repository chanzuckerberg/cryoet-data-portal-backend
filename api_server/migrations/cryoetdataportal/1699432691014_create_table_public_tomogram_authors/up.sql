CREATE TABLE "public"."tomogram_authors" (
    id serial NOT NULL,
    tomogram_id integer NOT NULL,
    author_list_order integer NOT NULL,
    name character varying NOT NULL,
    orcid character varying,
    corresponding_author_status boolean,
    primary_author_status boolean,
    email character varying,
    affiliation_name character varying,
    affiliation_address character varying,
    affiliation_identifier character varying
);

COMMENT ON TABLE public.tomogram_authors IS 'Authors for a tomogram';
COMMENT ON COLUMN public.tomogram_authors.id IS 'Numeric identifier for this tomogram author (this may change!)';
COMMENT ON COLUMN public.tomogram_authors.author_list_order IS 'The order in which the author appears in the publication';
COMMENT ON COLUMN public.tomogram_authors.tomogram_id IS 'Reference to the tomogram this author contributed to';
COMMENT ON COLUMN public.tomogram_authors.name IS 'Full name of an tomogram author (e.g. Jane Doe).';
COMMENT ON COLUMN public.tomogram_authors.orcid IS 'A unique, persistent identifier for researchers, provided by ORCID.';
COMMENT ON COLUMN public.tomogram_authors.corresponding_author_status IS 'Indicating whether an author is the corresponding author (YES or NO)';
COMMENT ON COLUMN public.tomogram_authors.primary_author_status IS 'Indicating whether an author is the main person creating the tomogram (YES or NO)';
COMMENT ON COLUMN public.tomogram_authors.email IS 'Email address for this author';
COMMENT ON COLUMN public.tomogram_authors.affiliation_name IS 'Name of the institution an annotator is affiliated with. Sometimes, one annotator may have multiple affiliations.';
COMMENT ON COLUMN public.tomogram_authors.affiliation_address IS 'Address of the institution an annotator is affiliated with.';
COMMENT ON COLUMN public.tomogram_authors.affiliation_identifier IS 'A unique identifier assigned to the affiliated institution by The Research Organization Registry (ROR).';

alter table "public"."tomogram_authors"
    add constraint "tomogram_authors_pkey"
    primary key ("id");

alter table "public"."tomogram_authors"
  add constraint "tomogram_authors_tomogram_id_fkey"
  foreign key ("tomogram_id")
  references "public"."tomograms"
  ("id") on update restrict on delete restrict;

alter table "public"."tomogram_authors"
    add constraint "tomogram_authors_tomogram_id_name_key"
    unique ("tomogram_id", "name");
