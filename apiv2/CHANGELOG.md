# Changelog

## [1.8.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.7.0...apiv2-v1.8.0) (2025-01-17)


### Features

* Add file size ([#418](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/418)) ([3760c15](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/3760c150d5c4762073821932133d046f07c373c2))
* Add file size to schema ([#401](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/401)) ([fc98398](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/fc98398745797c2e7fb9db32086b88194529c32b))


### Reverts

* Add file size to schema ([#401](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/401)) ([#417](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/417)) ([15a6d92](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/15a6d921c4e4b66e7ffa679db4093e768a3ad93d))

## [1.7.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.6.0...apiv2-v1.7.0) (2025-01-14)


### Features

* support filtering on related aggregates ([#394](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/394)) ([8885ab7](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/8885ab734a8f753ddaaf3b4f08f780f3b08f7ac4))


### Bug Fixes

* Don't replace spaces with underscores for reconstruction software. ([#402](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/402)) ([e253f1f](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/e253f1fa2e31c0e7909933dd2b88ead3d3708a87))
* Fix for spurious test failures. ([#410](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/410)) ([fedd776](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/fedd77611f15f8c2dd33bd1b1e57108f7d5f8456))
* fix response handling for grouping by related fields  ([#409](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/409)) ([7ef1563](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/7ef1563367b1a7499834537cb09fe85ab3fa4c76))
* scrape script overwriting existing data ([709e8a0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/709e8a006b542abe824edc394281059dda29a757))
* scrape script overwriting existing v2 data ([#390](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/390)) ([709e8a0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/709e8a006b542abe824edc394281059dda29a757))
* support __typename fields in gql queries ([#397](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/397)) ([6ea76ea](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/6ea76eab06864914ce16cbbd81da844f13e172e2))

## [1.6.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.5.0...apiv2-v1.6.0) (2024-12-17)


### Features

* Support for Per Section Alignment Parameters DB Import ([#369](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/369)) ([ce2643c](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/ce2643cadf643a18455405996d2856753a0ccbed))
* Support grouping aggregate results by 1:many relationships ([#376](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/376)) ([db82957](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/db82957625a4eab20e4fa02fa9790b90539336ae))


### Bug Fixes

* Adding is_visualization_default field to tomo ingestion ([#350](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/350)) ([a65209f](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/a65209fd2bf3ba80589be5cdc7f709930bb251fd))
* Make sure we support multiple grants for a given funding agency. ([#357](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/357)) ([b4441ea](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/b4441eafc1f0081378f3bc3fc2c214784abf8e99))
* remove tiltseries_id check from alignment importer ([#374](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/374)) ([1a3a50c](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/1a3a50c0bbcd31489a1426b132cf1c48edb23294))
* Support running v2 db import via batch job. ([#356](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/356)) ([a832d2f](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/a832d2f541c6413ad295b5386eaf9c76675490fb))

## [1.5.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.4.0...apiv2-v1.5.0) (2024-11-06)


### Features

* Expand the Tomgram importer hash function to include processing software ([#340](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/340)) ([3a92596](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/3a92596e94293f3026547939422ac6cf0440ff04))
* update apiv2 db ingestion to support new s3 schema ([#324](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/324)) ([02441de](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/02441dea0c008ac476bb0e993fb01c8331cd8f8b))


### Bug Fixes

* fixes for db ingestion ([#334](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/334)) ([d142394](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/d1423949f534667fc6131eb29729c040461cc16d))
* fixes for filtering on related fields. ([#343](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/343)) ([9cf033a](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/9cf033ab930a7a11e971eac65efcbf6644a0b935))
* Only read one alignment per run from the V1 api into the V2 api ([#341](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/341)) ([3a7cacf](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/3a7cacf03fae251a401088143719e7d201f1545e))

## [1.4.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.3.0...apiv2-v1.4.0) (2024-10-16)


### Features

* add frame & gain ingestion to db import ([#308](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/308)) ([7a167d6](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/7a167d651bb5b89425695adc7eb0e427979c5aae))
* Support scraping deposition_types and annotation_method_links ([#305](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/305)) ([740cd4c](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/740cd4c1418f9852d927347fb5b05212e1e2369f))

## [1.3.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.2.0...apiv2-v1.3.0) (2024-10-08)


### Features

* Align v1 and v2 schemas better ([#277](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/277)) ([2286dac](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/2286dacd613c7ef29a157e6151cf8fb886c8a5da))
* support importing s3 files into the v2 database ([#275](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/275)) ([f04e5f3](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/f04e5f3df2482f8d8a630628cd8154f3e487a998))
* track gain and mdoc files alongside runs ([#280](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/280)) ([483eee8](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/483eee815a94903898e70c0d776af82e91440782))


### Bug Fixes

* add is_standardized back temporarily ([#304](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/304)) ([dfe9a8b](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/dfe9a8bc409b7f011349992f0bd1923f4a9f4289))
* Date fields on tomograms are net-new so they need to be nullable. ([#301](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/301)) ([cf8d2e0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/cf8d2e0b97da7f0fb7a4ef28319e75f83ea1a9d1))
* keep both `tomogram.is_canonical` and `tomogram.is_portal_standard` ([#303](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/303)) ([c65e2f6](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/c65e2f66244453f32c5f76f0e672171b199c0f3a))
* make sure bool comparators don't require int input. ([#278](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/278)) ([991d9fa](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/991d9fadfe622268083d39628be3a0ea8eb456e3))
* Make sure we're using DB connection pools properly. ([#285](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/285)) ([169f8d8](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/169f8d8429c452954f9e3f69acfb9542c9ac1335))
* schema changes to support synthetic datasets. ([#282](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/282)) ([dfa24c0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/dfa24c0e4d65287edb98b5fb0fd677f42b89dad7))
* support filtering entities by related object id's ([#296](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/296)) ([6879a79](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/6879a7930e9b44d5be1b94c64545e710c883e1e5))
* Update sync script to sync missing fields. ([#281](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/281)) ([c4b7f81](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/c4b7f8169765e668cfd05962443e66730fdc92c7))
* use is_standardized rather than is_canonical ([dfe9a8b](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/dfe9a8bc409b7f011349992f0bd1923f4a9f4289))
* workaround for docker compose bugs. ([#295](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/295)) ([78daec3](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/78daec360edaf6aad763dbd3f63f99098683dd2a))

## [1.2.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.1.0...apiv2-v1.2.0) (2024-09-11)


### Features

* add CORS middleware to apiv2 ([#267](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/267)) ([db08a59](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/db08a590476ea532c69e2a757425173f3b3b6941))

## [1.1.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.0.0...apiv2-v1.1.0) (2024-09-10)


### Features

* add docs for release ([#265](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/265)) ([cb4af79](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/cb4af7956737e225a9429684ca6202ac24f60781))

## 1.0.0 (2024-09-06)


### Bug Fixes

* more ci fixes. ([#247](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/247)) ([771671d](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/771671da21c22d3600b8b7c88ac8c0b1bc3ce3b1))
* Update scrape tool to handle alignments and depositions. ([#240](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/240)) ([571943f](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/571943f1ed68b3e62b2f70a91f8de38925d2fd92))
* use supported github workflows. ([#242](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/242)) ([4f5fcee](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/4f5fcee7546c6bd77ad8dfe8346ac29be18f637d))
