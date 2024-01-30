alter table "public"."tomograms" add column "type" text null;

alter table "public"."tomograms"
  add constraint "tomograms_type_fkey"
  foreign key ("type")
  references "public"."tomogram_type"
  ("value") on update restrict on delete restrict;
