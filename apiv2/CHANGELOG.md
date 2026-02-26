# Changelog

## [1.15.1](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.15.0...apiv2-v1.15.1) (2026-02-26)


### Bug Fixes

* update Dockerfile and dependencies for frontend GH Action (python client tests) Docker env ([#594](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/594)) ([2ad4846](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/2ad48466785f97dd748a235f061383f33633d411))

## [1.15.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.14.1...apiv2-v1.15.0) (2026-01-23)


### Features

* add support for uberon/chebi ontologies for annotation_object_id; update outdated ontology id fields in apiv2 schema ([#586](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/586)) ([a26a6d3](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/a26a6d3d84c0f02497a8b43860424604dcc31b87))

## [1.14.1](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.14.0...apiv2-v1.14.1) (2026-01-23)


### Bug Fixes

* update linkml package version, bugfix api codegen, bugfix ingestion validation ([#585](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/585)) ([c972d59](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/c972d596c10bfa430e820008372b59598a339e3c))

## [1.14.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.13.2...apiv2-v1.14.0) (2025-11-26)


### Features

* add ingestion config (10453) for EMPIAR 12794 - isolated synaptic vesicles from mouse brain ([#538](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/538)) ([584fc12](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/584fc123e1ecbac4557cefbc299231b6f646548b))


### Bug Fixes

* neuroglancer config ingestion & db import (fixes staging tomogram viewer)  ([#545](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/545)) ([dee5844](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/dee584432dc596e94323ea2e79f4e8b582145317))

## [1.13.2](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.13.1...apiv2-v1.13.2) (2025-10-30)


### Bug Fixes

* Populate frame file_size field correctly during import ([#539](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/539)) ([dc7abf7](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/dc7abf7fc42ecb9228f5350f9a04bb0170261aa3))

## [1.13.1](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.13.0...apiv2-v1.13.1) (2025-09-11)


### Bug Fixes

* address High priority alerts ([#533](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/533)) ([9259803](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/925980386de17ee426959dcf24bf54304e4e48ed))
* Critical dependabot alert for h11 ([#530](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/530)) ([046f462](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/046f462b13b5494ea00008085c5597484428b790))

## [1.13.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.12.0...apiv2-v1.13.0) (2025-08-19)


### Features

* Add IdentifiedObject data model ([#510](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/510)) ([4a025d9](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/4a025d9df87832a74ac65a31f6613f9a127e02a2))

## [1.12.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.11.0...apiv2-v1.12.0) (2025-07-24)


### Features

* Empty commit ([#525](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/525)) ([159b642](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/159b64215058e1f348ad700de09c14cfe78809fe))


### Bug Fixes

* Add better handling for value error exceptions from pagination. ([#475](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/475)) ([a46df89](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/a46df8985fe081147484fdf2310d3efe0aca88c9))
* adding back schema diagram ([#473](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/473)) ([725f037](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/725f0376aaa73a5f96d56bc6cfb0ced11f503383))
* Update APIv2 runner to privileged ([#507](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/507)) ([6a6b7ed](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/6a6b7edaead52be21179b9830f549133a0ebbbca))

## [1.11.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.10.0...apiv2-v1.11.0) (2025-03-20)


### Features

* add PerSectionParameters table to apiv2 ([#461](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/461)) ([2f4fc90](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/2f4fc90f8e44cbb08e9a1738a3d87780badb76cc))
* Adding additional tomogram processings ([#466](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/466)) ([c4e8a47](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/c4e8a47445634c35f2986eda6f6b925ba82d2d44))
* Update DB ingestion for FramesAcquisitionFile, and Frames ([#451](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/451)) ([c8c40dd](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/c8c40dd56b1ac0bc60dd98a2026c2f5a75ba5ab7))

## [1.10.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.9.1...apiv2-v1.10.0) (2025-02-26)


### Features

* add tag and kaggle id to importers ([#453](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/453)) ([2969bcc](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/2969bcc9e902824b236eb2def6c470d5b00ef11b))

## [1.9.1](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.9.0...apiv2-v1.9.1) (2025-02-14)


### Bug Fixes

* path_filter formatting ([#447](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/447)) ([c545765](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/c54576577361eac52534be176a931f2d25a5f507))
* update argus docker build ([#448](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/448)) ([6d8f116](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/6d8f116deae27ba680b38e9291e690be218869b4))
* update docker build ([#446](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/446)) ([203a49e](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/203a49e1eb06901f8b16b0c0f6e64cfe1e3fe2cd))
* update staging/prod builder ([#444](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/444)) ([a7fdf4f](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/a7fdf4fd83082e88b88eb9c14c7558a42b23bb74))

## [1.9.0](https://github.com/chanzuckerberg/cryoet-data-portal-backend/compare/apiv2-v1.8.0...apiv2-v1.9.0) (2025-02-13)


### Features

* add kaggle id and deposition tag ([#433](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/433)) ([9a1fedb](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/9a1fedb80f074a2c22d9b6629acf42f9f5636a65))


### Bug Fixes

* update to trigger workflow ([#442](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/442)) ([1fdbf8b](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/1fdbf8b523de6198a6364ea24406d446a1b9eff6))
* update to trigger workflow 2 ([#443](https://github.com/chanzuckerberg/cryoet-data-portal-backend/issues/443)) ([dfecee5](https://github.com/chanzuckerberg/cryoet-data-portal-backend/commit/dfecee5ead6d52d99e6ab0ef779abd7bfe84e1bd))

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
