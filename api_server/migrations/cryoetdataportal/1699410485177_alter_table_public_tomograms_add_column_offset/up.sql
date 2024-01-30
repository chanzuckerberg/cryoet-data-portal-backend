alter table "public"."tomograms" add column "offset_x" integer
 not null default '0';
comment on column "public"."tomograms"."offset_x" is
E'x offset data relative to the canonical tomogram in pixels';

alter table "public"."tomograms" add column "offset_y" integer
 not null default '0';
comment on column "public"."tomograms"."offset_y" is
E'y offset data relative to the canonical tomogram in pixels';


alter table "public"."tomograms" add column "offset_z" integer
 not null default '0';
comment on column "public"."tomograms"."offset_z" is
E'z offset data relative to the canonical tomogram in pixels';
