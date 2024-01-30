alter table "public"."tomogram_authors" drop constraint "tomogram_authors_pkey";
alter table "public"."tomogram_authors" drop constraint "tomogram_authors_tomogram_id_fkey";
alter table "public"."tomogram_authors" drop constraint "tomogram_authors_tomogram_id_name_key";

DROP TABLE "public"."tomogram_authors";
