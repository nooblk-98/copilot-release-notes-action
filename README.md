# ai-automatic-releases

AI-powered GitHub release notes automation.

## What this repo now contains

- Workflow: `.github/workflows/auto-release-notes.yml`
- Scripts: `.github/scripts/release/*.sh`

The workflow triggers when a release is created and can also be run manually.

## Required GitHub settings

Add this repository secret:

- `OPENAI_API_KEY`: API key used to generate release notes and release title.

Optional repository variable:

- `OPENAI_MODEL`: defaults to `gpt-4.1-mini` when not set.

## Behavior

1. Build release context (current and previous tags).
2. Build commit summary for the release range.
3. Generate baseline notes from GitHub release API.
4. Use AI to rewrite notes and generate a short release title.
5. Update the release title and body.

If `OPENAI_API_KEY` is missing, the workflow falls back to non-AI release notes and title.
