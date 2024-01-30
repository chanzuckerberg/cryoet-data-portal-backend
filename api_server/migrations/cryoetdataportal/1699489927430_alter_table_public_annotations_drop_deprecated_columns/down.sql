alter table "public"."annotations" add column "object_weight" numeric null;
comment on column "public"."annotations"."object_weight" is
E'Molecular weight of the annotation object, in Dalton';

alter table "public"."annotations" add column "object_width" numeric null;
comment on column "public"."annotations"."object_width" is
E'Average width of the annotation object in Angstroms; applicable if the object shape is line';

alter table "public"."annotations" add column "object_diameter" numeric null;
comment on column "public"."annotations"."object_diameter" is
E'Diameter of the annotation object in Angstrom; applicable if the object shape is point or vector';
