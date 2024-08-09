alter table "public"."depositions" add column "key_photo_url" varchar null;
comment on column "public"."depositions"."key_photo_url" is E'URL for the deposition preview image.';

alter table "public"."depositions" add column "key_photo_thumbnail_url" varchar null;
comment on column "public"."depositions"."key_photo_thumbnail_url" is E'URL for the deposition thumbnail image.';
