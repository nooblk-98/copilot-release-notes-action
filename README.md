# Copilot Release Notes Action

Generate and publish AI-powered GitHub release titles and release notes using GitHub Copilot.

This repository is structured as a reusable GitHub Action for the GitHub Marketplace.

## Auth Notes

- The action uses your repository/workflow `GITHUB_TOKEN`; no extra external token is required.
- It calls the Copilot API directly and does not require `actions/setup-copilot`.
- No OpenAI API key is required.

If Copilot generation is unavailable, the action falls back to GitHub generated notes plus commit summary.

## Sample Output

```md
### Summary
- Tag: `v1.4.0`
- Previous tag: `v1.3.0`

### New Features
- feat: add automatic category grouping for commits (a1b2c3d)
- feat: support manual workflow_dispatch release updates (d4e5f6g)

### Bug Fixes
- fix: remove duplicate changelog lines in release body (h7i8j9k)

### Updates
- chore: improve README examples and simplify setup (l0m1n2o)

### GitHub Generated Notes
* Merged PR #12 from `feature/release-note-cleanup`
* Merged PR #13 from `fix/remove-duplicate-heading`
```

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
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate and update release notes
        uses: nooblk-98/copilot-release-notes-action@main
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
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate and update release notes
        uses: nooblk-98/copilot-release-notes-action@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          tag_name: ${{ inputs.tag_name }}
          target_commitish: ${{ inputs.target_commitish }}
```

## Runner Requirements

- `python3` and `git` (available on `ubuntu-latest`).
- Use `fetch-depth: 0` so tag comparison and commit ranges work correctly.
