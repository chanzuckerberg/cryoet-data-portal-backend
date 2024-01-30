alter table "public"."dataset_authors" add column "author_list_order" integer
 null;
COMMENT ON COLUMN public.dataset_authors.author_list_order IS
'The order in which the author appears in the publication';
