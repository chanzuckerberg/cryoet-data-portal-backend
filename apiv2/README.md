# Getting started

```
make init # from the root of the repo
```

After the above steps, browse the api at [http://localhost:9009/graphql](http://localhost:9009/graphql)

If you'd like to load some data from the production portal into the db, run this from the root of the repo:
```make db-import
```
make db-import-dataset
```

## Testing

From the `apiv2` directory, run:

```
# Run all tests
$ make test

# Just run ingestion tests
$ FILE=db_import make test-file

# Just run apiv2 tests
$ FILE=tests make test-file

# Run a single test file
$ FILE=tests/test_aggregates.py make test-file
```

## Common Commands

| Command                     | Description                                                                                     |
| --------------------------- | ----------------------------------------------------------------------------------------------- |
| `make test`                 | Runs unit tests for api v2 and db ingestion                                                     |
| `make update-schema`        | If `schema/schema.yaml` has been modified, run this to re-run codegen and create new migrations |
| `make codegen`              | If any codegen templates have been modified, run this to apply the changes                      |
| `make pgconsole`            | Open a psql console in the apiv2 database                                                       |
| `make alembic-upgrade-head` | Run all alembic migrations to bring the db structure up to date.                                |
| `make stop`                 | Stops all the docker containers started by this application.                                    |
| `make clean`                | Removes all the docker containers started by this application.                                  |

## How to make changes to the schema

**NOTE:** Most schema changes will require accompanying changes to the `db_import` scripts to support the new fields!

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

## RELEASES - Updating staging/prod

**TL;DR:**

- Merging to main will deploy changes to staging
- Merging a release-please pull request will deploy changes to production

**Still reading / How this works:**

1. Merging a PR to `main` that has a conventional commit title of `feat`, `fix`, or breaking changes (`chore` doesn't count!) will trigger a [release-please](https://github.com/googleapis/release-please/) action that creates a new release candidate PR.
2. Once the release PR has been created, another action gets triggered that builds a new staging docker image. This action also writes updated image sha's to staging/prod envs in `.infra`
3. Once the new image build is complete, _another_ action ensures that ArgoCD was able to successfully update staging.
4. Merging the release PR means that the image SHA's in `.infra/prod` are updated in the main branch. ArgoCD will update prod to reflect the latest build.

## Debugging

### Using VSCode debugger

1. Install the `Dev Containers` extension for vscode
2. Open a new VSCode window in the `apiv2` directory. It will read the `.devcontainer/devcontainer.json` configuration and prompt you to reopen the directory in a container (lower right side of the screen). Click "Reopen in container"
3. Click the "Run and Debug" icon in the icon bar on the right side of the VSCode window (or ctrl+shift+d). Then click the "start debugging" icon at the top of the run and debug panel (or press F5). This will launch a secondary instance of the API service that listens on port 9008.
4. Set all the breakpoints you want. Browse to the api at http://localhost:9008/graphql to trigger them. Remember that the application restarts when files change, so you'll have to start and stop the debugger to pick up any changes you make!
