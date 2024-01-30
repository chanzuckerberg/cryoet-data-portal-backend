CREATE TABLE "public"."tomogram_type" (
    "value" text NOT NULL, "description" text,
    PRIMARY KEY ("value")
);
COMMENT ON TABLE "public"."tomogram_type" IS E'The type of tomograms';

INSERT INTO "public"."tomogram_type"("value", "description")
VALUES (E'CANONICAL', E''), (E'UNKOWN', E'');
