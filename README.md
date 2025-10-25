# Sync Closing Labels

GitHub action to copy labels from any issues closed by a pull request into the pull request itself

![](./images/sync-closing-labels.png)

## Quick Start

```yaml
---
name: Sync Closing Labels
on:
- pull_request_target

jobs:
  sync:
    permissions:
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
    - name: Sync labels with closing issues
      uses: williambdean/closing-labels@v0.0.4
      env:
        GH_TOKEN: ${{ github.token }}
```

## Inputs

- `exclude`: A comma separated list of labels to exclude from the closing labels. Default: `""`
  - Example: `exclude: "wontfix,good first issue"` will not add `wontfix` and `good first issue` labels to the pull request
    from the closing issues.
- `respect_unlabeled`: Respect the `unlabeled` event. Default: `true`. Set to `false` will
  relabel the pull request with the *all* closing labels.


Add various configuration in the `with` section of the action:

```yaml

with:
  exclude: "wontfix,good first issue"
  respect_unlabeled: false
```

## Local Development

This script is an entrypoint for a GitHub Action and relies on environment variables set by the Actions runner. To run it locally, you need to provide these variables.

Enter docker container to test action locally:

```terminal
make build
make interactive
```

From inside the container, run the action script with the required environment variables:

```sh
INPUT_OWNER="your-github-username" \
INPUT_REPO="your-repo-name" \
INPUT_PR_NUMBER="123" \
INPUT_EXCLUDE="wontfix,duplicate" \
INPUT_RESPECT_UNLABELED="true" \
INPUT_DRY_RUN="true" \
./entrypoint.sh
```

This command sets the necessary environment variables with example values and then executes the script. You would need to have `gh` (the GitHub CLI) and `jq` installed and authenticated to run it successfully outside of the container. The container provided via the `Makefile` has these dependencies installed.
