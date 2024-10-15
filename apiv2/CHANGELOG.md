# Changelog

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
