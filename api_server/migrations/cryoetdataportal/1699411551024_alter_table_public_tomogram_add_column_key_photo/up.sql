alter table "public"."tomograms" add column "key_photo_url" varchar null;
comment on column "public"."tomograms"."key_photo_url" is
E'URL for the key photo';

alter table "public"."tomograms" add column "key_photo_thumbnail_url" varchar null;
comment on column "public"."tomograms"."key_photo_thumbnail_url" is
E'URL for the thumbnail of key photo';
