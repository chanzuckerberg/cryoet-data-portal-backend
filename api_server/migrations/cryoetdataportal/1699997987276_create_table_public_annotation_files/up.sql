CREATE TABLE "public"."annotation_files" (
    "id" serial NOT NULL,
    "annotation_id" integer NOT NULL,
    "shape_type" varchar NOT NULL,
    "format" varchar NOT NULL,
    "https_path" varchar NOT NULL,
    "s3_path" varchar NOT NULL,
    PRIMARY KEY ("id") ,
    UNIQUE ("annotation_id", "shape_type"),
    FOREIGN KEY ("annotation_id") REFERENCES "public"."annotations"("id")
        ON UPDATE restrict
        ON DELETE restrict
);
COMMENT ON TABLE "public"."annotation_files" IS
E'Information about associated files for a given annotation';

comment on column "public"."annotation_files"."s3_path" is
E's3 path of the annotation file';
comment on column "public"."annotation_files"."https_path" is
E'https path of the annotation file';
comment on column "public"."annotation_files"."shape_type" is
E'The type of the annotation';
comment on column "public"."annotation_files"."format" is
E'Format of the annotation object file';
