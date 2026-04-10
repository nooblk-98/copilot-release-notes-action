# AI Automatic Release Notes (GitHub Action)

Generate and publish AI-powered GitHub release titles and release notes using GitHub Copilot.

This repository is structured as a reusable GitHub Action for the GitHub Marketplace.

## Repository Structure

- `action.yml`: Marketplace action definition.
- `scripts/release/01_prepare_context.py`: Resolves current and previous tags.
- `scripts/release/02_build_change_summary.py`: Builds commit summary for release range.
- `scripts/release/03_generate_release_notes.py`: Generates release notes (Copilot + fallback).
- `scripts/release/04_generate_release_title.py`: Generates release title (Copilot + fallback).
- `scripts/release/05_update_release.py`: Updates GitHub release title and body.
- `.github/workflows/auto-release-notes.yml`: Example workflow using this action.

## Inputs

- `github_token` (required): GitHub token with `contents: write` permission.
- `copilot_token` (optional): Copilot token used for AI generation.
  - If omitted, `github_token` is used.
- `copilot_model` (optional): Copilot model name. Default: `gpt-4o`.
- `tag_name` (optional): Release tag to update. If omitted, latest tag is used.
- `target_commitish` (optional): Target commit SHA/branch.

## Outputs

- `release_title`: Final release title used.
- `release_notes`: Final release notes markdown used.

## Auth Notes

- You can run this with the current GitHub user's token flow.
- No OpenAI API key is required.
- For best Copilot reliability in Actions, provide `copilot_token` as a repo secret (example: `COPILOT_TOKEN`).

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
        uses: nooblk-98/ai-automatic-releases@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          copilot_token: ${{ secrets.COPILOT_TOKEN }}
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
        uses: nooblk-98/ai-automatic-releases@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          copilot_token: ${{ secrets.COPILOT_TOKEN }}
          tag_name: ${{ inputs.tag_name }}
          target_commitish: ${{ inputs.target_commitish }}
```

## Publishing to GitHub Marketplace

1. Keep `action.yml` in repository root.
2. Create release `v1.0.0`.
3. Create/move major tag `v1` to that release commit.
4. Publish Marketplace listing from this repository.

## Runner Requirements

- `python3` and `git` (available on `ubuntu-latest`).
- Use `fetch-depth: 0` so tag comparison and commit ranges work correctly.
