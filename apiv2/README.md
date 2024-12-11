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
# First, make any necessary changes to `apiv2/schema/schema.yaml`, then run this to generate new code & migrations and apply them:
cd apiv2
make update-schema
```

When ready to commit and push your changes, follow the guidelines [here]().

## Debugging

### Using VSCode debugger

1. Install the `Dev Containers` extension for vscode
2. Open a new VSCode window in the `apiv2` directory. It will read the `.devcontainer/devcontainer.json` configuration and prompt you to reopen the directory in a container (lower right side of the screen). Click "Reopen in container"
3. Click the "Run and Debug" icon in the icon bar on the right side of the VSCode window (or ctrl+shift+d). Then click the "start debugging" icon at the top of the run and debug panel (or press F5). This will launch a secondary instance of the API service that listens on port 9008.
4. Set all the breakpoints you want. Browse to the api at http://localhost:9008/graphql to trigger them. Remember that the application restarts when files change, so you'll have to start and stop the debugger to pick up any changes you make!
