#!/usr/bin/env bash
set -euo pipefail

CONTEXT_FILE="/tmp/release-context.env"
SUMMARY_FILE="/tmp/change-summary.md"
GENERATED_JSON="/tmp/generated-notes.json"
NOTES_FILE="/tmp/release-notes.md"

if [[ ! -f "${CONTEXT_FILE}" || ! -f "${SUMMARY_FILE}" ]]; then
  echo "Missing required context files."
  exit 1
fi

# shellcheck disable=SC1090
source "${CONTEXT_FILE}"

if [[ -n "${PREVIOUS_TAG}" ]]; then
  gh api \
    --method POST \
    -H "Accept: application/vnd.github+json" \
    "/repos/${REPO}/releases/generate-notes" \
    -f tag_name="${NEW_TAG}" \
    -f target_commitish="${SHA}" \
    -f previous_tag_name="${PREVIOUS_TAG}" \
    > "${GENERATED_JSON}"
else
  gh api \
    --method POST \
    -H "Accept: application/vnd.github+json" \
    "/repos/${REPO}/releases/generate-notes" \
    -f tag_name="${NEW_TAG}" \
    -f target_commitish="${SHA}" \
    > "${GENERATED_JSON}"
fi

GITHUB_BODY="$(jq -r '.body // ""' "${GENERATED_JSON}")"
SUMMARY_BODY="$(cat "${SUMMARY_FILE}")"
DEFAULT_NOTES=$(
  cat <<EOF
## Release ${NEW_TAG}

### Highlights
${SUMMARY_BODY}

### Full Changelog
${GITHUB_BODY}
EOF
)

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  OPENAI_MODEL="${OPENAI_MODEL:-gpt-4.1-mini}"
  REQUEST_JSON="$(jq -n \
    --arg model "${OPENAI_MODEL}" \
    --arg tag "${NEW_TAG}" \
    --arg prev "${PREVIOUS_TAG:-none}" \
    --arg summary "${SUMMARY_BODY}" \
    --arg generated "${GITHUB_BODY}" \
    '{
      model: $model,
      temperature: 0.2,
      messages: [
        {
          role: "system",
          content: "You write concise professional GitHub release notes in markdown. Keep facts grounded in provided content only."
        },
        {
          role: "user",
          content: (
            "Create release notes in markdown with sections: Summary, New Features, Bug Fixes, Improvements, and Full Changelog. " +
            "Tag: " + $tag + ". Previous tag: " + $prev + "\\n\\nCommit summary:\\n" + $summary + "\\n\\nGitHub generated notes:\\n" + $generated
          )
        }
      ]
    }')"

  AI_NOTES="$(curl -sS https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer ${OPENAI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "${REQUEST_JSON}" | jq -r '.choices[0].message.content // empty')"

  if [[ -n "${AI_NOTES}" ]]; then
    printf '%s\n' "${AI_NOTES}" > "${NOTES_FILE}"
  else
    printf '%s\n' "${DEFAULT_NOTES}" > "${NOTES_FILE}"
  fi
else
  printf '%s\n' "${DEFAULT_NOTES}" > "${NOTES_FILE}"
fi

echo "Wrote release notes to ${NOTES_FILE}"
