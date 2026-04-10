# Copilot Release Notes Action

Generate and publish AI-powered GitHub release titles and release notes using GitHub Copilot.

This repository is structured as a reusable GitHub Action for the GitHub Marketplace.

## Auth Notes

- The action uses your repository/workflow `GITHUB_TOKEN`; no extra external token is required.
- It calls the Copilot API directly and does not require `actions/setup-copilot`.
- No OpenAI API key is required.

If Copilot generation is unavailable, the action falls back to GitHub generated notes plus commit summary.

## Sample Usage (Release Event)

```yaml
name: Auto Release Notes

on:
  release:
    types: [created]

permissions:
  contents: write

jobs:
  release-notes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0

      - name: Generate and update release notes
        uses: nooblk-98/copilot-release-notes-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          copilot_model: gpt-4o
          tag_name: ${{ github.event.release.tag_name }}
          target_commitish: ${{ github.event.release.target_commitish }}
```

## Sample Usage (Manual Trigger)

```yaml
name: Manual Release Notes

on:
  workflow_dispatch:
    inputs:
      tag_name:
        required: true
        type: string
      target_commitish:
        required: false
        type: string

permissions:
  contents: write

jobs:
  release-notes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0

      - name: Generate and update release notes
        uses: nooblk-98/copilot-release-notes-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          tag_name: ${{ inputs.tag_name }}
          target_commitish: ${{ inputs.target_commitish }}
```

## Runner Requirements

- `python3` and `git` (available on `ubuntu-latest`).
- Use `fetch-depth: 0` so tag comparison and commit ranges work correctly.
