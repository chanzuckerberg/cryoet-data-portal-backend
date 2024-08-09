# Getting started

```
cd apiv2
make build
make init
docker compose exec graphql-api pip install cryoet_data_portal
# You can stop this after a few screenfuls of output if you don't need a full import.
docker compose exec graphql-api python3 scrape.py
```
