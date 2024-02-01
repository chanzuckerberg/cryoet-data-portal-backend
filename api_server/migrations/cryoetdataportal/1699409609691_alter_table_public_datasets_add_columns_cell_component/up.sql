alter table "public"."datasets" add column "cell_component_name" varchar null;
comment on column "public"."datasets"."cell_component_name" is
E'Name of the cellular component';

alter table "public"."datasets" add column "cell_component_id" varchar null;
comment on column "public"."datasets"."cell_component_id" is
E'If this dataset only focuses on a specific part of a cell, include the subset here';
