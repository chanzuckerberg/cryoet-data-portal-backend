comment on column "public"."annotations"."object_id" is E'Gene Ontology Cellular Component identifier or UniProtKB accession for the annotation object.';
alter table "public"."tiltseries_quality" alter column "annotation_object_id" drop not null;
