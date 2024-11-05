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

# Then, from the root of the repo, run:
cd ..
pre-commit run --all-files

# Then commit all changed files, *including* any new migrations!
git commit -am "chore: Updating schema to add X feature"
```

## Creating an rdev stack
1. Open a pull request
2. Add a label called "stack" to the PR. This will trigger an action that creates an rdev stack. Once the stack has been created, the PR comment will be updated to reflect the URL you can use to access your rdev instance.
3. **NOTE!!:** For now, all rdevs share a database. Fixing this is a TODO.

## Updating staging/prod
1. Merging a PR to `main` that has a conventional commit title of `feat`, `fix`, or breaking changes (`chore` doesn't count!) will trigger a [release-please](https://github.com/googleapis/release-please/) action that creates a new release candidate PR.
2. Once the release PR has been created, another action gets triggered that builds a new staging docker image. This action also writes updated image sha's to staging/prod envs in `.infra`
3. Once the new image build is complete, *another* action ensures that ArgoCD was able to successfully update staging.
4. Merging the release PR means that the image SHA's in `.infra/prod` are updated in the main branch. ArgoCD will update prod to reflect the latest build.
o## Debugging

### Using VSCode debugger
1. Install the `Dev Containers` extension for vscode
2. Open a new VSCode window in the `apiv2` directory. It will read the `.devcontainer/devcontainer.json` configuration and prompt you to reopen the directory in a container (lower right side of the screen). Click "Reopen in container"
3. Click the "Run and Debug" icon in the icon bar on the right side of the VSCode window (or ctrl+shift+d). Then click the "start debugging" icon at the top of the run and debug panel (or press F5). This will launch a secondary instance of the API service that listens on port 9008.
4. Set all the breakpoints you want. Browse to the api at http://localhost:9008/graphql to trigger them. Remember that the application restarts when files change, so you'll have to start and stop the debugger to pick up any changes you make!

