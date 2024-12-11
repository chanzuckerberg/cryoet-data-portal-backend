# Pre-deployment

## Committing to the repo

From the root of the repo, run:

```
pre-commit run --all-files
```

Then commit all changed files, _including_ any new migrations! Following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standards:

```
git commit -am "chore: Updating schema to add X feature"
```

## Creating an rdev stack

1. Open a pull request
2. Add a label called "stack" to the PR. This will trigger an action that creates an rdev stack. Once the stack has been created, the PR comment will be updated to reflect the URL you can use to access your rdev instance.
3. **NOTE!!:** For now, all rdevs share a database. Fixing this is a TODO.

## Updating staging/prod

1. Merging a PR to `main` that has a conventional commit title of `feat`, `fix`, or breaking changes (`chore` doesn't count!) will trigger a [release-please](https://github.com/googleapis/release-please/) action that creates a new release candidate PR.
2. Once the release PR has been created, another action gets triggered that builds a new staging docker image. This action also writes updated image sha's to staging/prod envs in `.infra`
3. Once the new image build is complete, _another_ action ensures that ArgoCD was able to successfully update staging.
4. Merging the release PR means that the image SHA's in `.infra/prod` are updated in the main branch. ArgoCD will update prod to reflect the latest build.
