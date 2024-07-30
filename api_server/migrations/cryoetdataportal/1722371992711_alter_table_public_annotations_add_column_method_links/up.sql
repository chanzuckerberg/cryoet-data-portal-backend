alter table "public"."annotations" add column "method_links" text null;
comment on column "public"."annotations"."method_links" is
E'Provides links that generates information on the method used for generating annotation';
