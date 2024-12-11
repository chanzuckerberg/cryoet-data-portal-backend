# Running tests

## Seed moto server

Before running tests, make sure to run the following from `/test_infra/`:

```
./seed_moto.sh
```

This script will seed the [moto](https://docs.getmoto.org/en/latest/index.html) server with test data

## Running tests

From the root of the repo run:

```
make apiv2-test
```
