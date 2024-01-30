alter table "public"."annotation_authors" add column "author_list_order" integer
 null;
COMMENT ON COLUMN public.annotation_authors.author_list_order IS
'The order in which the author appears in the publication';
