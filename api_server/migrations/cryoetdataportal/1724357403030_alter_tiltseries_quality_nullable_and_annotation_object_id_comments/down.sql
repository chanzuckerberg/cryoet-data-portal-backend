comment on column "public"."annotations"."object_id" is E'Gene Ontology Cellular Component identifier for the annotation object';
alter table "public"."tiltseries"."tiltseries_quality" alter column "annotation_object_id" set not null;
