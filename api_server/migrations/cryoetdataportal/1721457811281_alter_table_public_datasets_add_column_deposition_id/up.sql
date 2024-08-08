ALTER TABLE "public"."datasets" ADD COLUMN "deposition_id" INTEGER NULL;
CREATE  INDEX "dataset_deposition_id" on "public"."datasets" using btree ("deposition_id");

COMMENT ON COLUMN public.datasets.deposition_id IS 'Reference to the deposition this dataset is associated with';
