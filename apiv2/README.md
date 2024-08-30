# Getting started

```
make apiv2-init # from the root of the repo
docker compose exec graphql-api pip install cryoet_data_portal
# You can stop this after a few screenfuls of output if you don't need a full import.
docker compose exec graphql-api python3 scrape.py
```

After the above steps, browse the api at [http://localhost:9009/graphql](http://localhost:9009/graphql)

## How to make changes to the schema

```
# First, make any necessary changes to apiv2/schema/schema.yaml, then run this to generate new code & migrations and apply them:
make update-schema
```
