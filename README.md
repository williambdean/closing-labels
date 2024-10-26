# Sync Closing Labels

GitHub action to add closing labels to a pull request

## Quick Start

```yaml
name: Sync Closing Labels
on:
- pull_request_target

jobs:
  sync:
    permissions:
      contents: read
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v2
    - name: Sync labels with closing issues
      uses: wd60622/closing-labels@v0.0.3
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
