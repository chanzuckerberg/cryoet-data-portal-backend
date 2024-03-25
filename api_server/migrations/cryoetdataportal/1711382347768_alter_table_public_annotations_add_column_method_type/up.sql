alter table "public"."annotations" add column "method_type" varchar null;
comment on column "public"."annotations"."method_type" is
E'Provides information on the method type used for generating annotation';
