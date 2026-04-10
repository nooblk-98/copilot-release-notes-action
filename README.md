# AI Automatic Release Notes (GitHub Action)

Generate and publish AI-powered GitHub release titles and release notes.

This repository is structured as a reusable GitHub Action for the GitHub Marketplace.

## Repository Structure

- `action.yml`: Action definition used by Marketplace.
- `scripts/release/01_prepare_context.sh`: Resolves current and previous release tags.
- `scripts/release/02_build_change_summary.sh`: Builds commit summary for release range.
- `scripts/release/03_generate_release_notes.sh`: Generates release notes (AI + fallback).
- `scripts/release/04_generate_release_title.sh`: Generates release title (AI + fallback).
- `scripts/release/05_update_release.sh`: Updates GitHub release title/body.
- `.github/workflows/auto-release-notes.yml`: Example workflow using this action.

## Inputs

- `github_token` (required): Token with `contents: write` permission.
- `openai_api_key` (optional): API key for AI-generated title/notes.
- `openai_model` (optional): OpenAI model. Default: `gpt-4.1-mini`.
- `tag_name` (optional): Release tag to update. If omitted, latest tag is used.
- `target_commitish` (optional): Release target SHA/branch.

## Outputs

- `release_title`: Final release title used.
- `release_notes`: Final release notes markdown used.

## Required Secrets / Variables

- `OPENAI_API_KEY` (optional, but recommended for AI mode).
- `OPENAI_MODEL` (optional repo variable).

If `openai_api_key` is not provided, the action falls back to non-AI output using commit summary and GitHub generated notes.

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
        uses: lahiru/ai-automatic-releases@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          openai_model: gpt-4.1-mini
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
        uses: lahiru/ai-automatic-releases@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          tag_name: ${{ inputs.tag_name }}
          target_commitish: ${{ inputs.target_commitish }}
```

## Publishing to GitHub Marketplace

1. Ensure `action.yml` is in the repository root.
2. Add a release tag (example: `v1`).
3. In GitHub, open this repository and choose **Draft a new release**.
4. Publish release `v1.0.0` and keep/move major tag `v1` to that commit.
5. In Marketplace listing, use this repository and metadata from `action.yml`.

## Notes

- This action expects `git`, `gh`, `jq`, and `curl` in the runner (available on `ubuntu-latest`).
- Use `fetch-depth: 0` so tag comparison and commit ranges work correctly.
