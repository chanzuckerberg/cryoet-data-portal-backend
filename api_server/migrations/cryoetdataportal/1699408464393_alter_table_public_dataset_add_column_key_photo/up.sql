alter table "public"."datasets" add column "key_photo_url" varchar null;
comment on column "public"."datasets"."key_photo_url" is
E'URL for the dataset preview image.';

alter table "public"."datasets" add column "key_photo_thumbnail_url" varchar null;
comment on column "public"."datasets"."key_photo_thumbnail_url" is
E'URL for the thumbnail of preview image.';
