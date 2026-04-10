#!/usr/bin/env bash
set -euo pipefail

CONTEXT_FILE="/tmp/release-context.env"
SUMMARY_FILE="/tmp/change-summary.md"
TITLE_FILE="/tmp/release-title.txt"

if [[ ! -f "${CONTEXT_FILE}" || ! -f "${SUMMARY_FILE}" ]]; then
  echo "Missing required context files."
  exit 1
fi

# shellcheck disable=SC1090
source "${CONTEXT_FILE}"

SUMMARY_BODY="$(cat "${SUMMARY_FILE}")"
RELEASE_TITLE="Release ${NEW_TAG}"

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  OPENAI_MODEL="${OPENAI_MODEL:-gpt-4.1-mini}"
  REQUEST_JSON="$(jq -n \
    --arg model "${OPENAI_MODEL}" \
    --arg tag "${NEW_TAG}" \
    --arg summary "${SUMMARY_BODY}" \
    '{
      model: $model,
      temperature: 0.2,
      messages: [
        {
          role: "system",
          content: "Generate one short professional GitHub release title. Return only plain text. Max 70 characters."
        },
        {
          role: "user",
          content: ("Tag: " + $tag + "\\nChanges:\\n" + $summary)
        }
      ]
    }')"

  AI_TITLE="$(curl -sS https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer ${OPENAI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "${REQUEST_JSON}" | jq -r '.choices[0].message.content // empty' | head -n 1 | tr -d '\r')"

  if [[ -n "${AI_TITLE}" ]]; then
    RELEASE_TITLE="${AI_TITLE}"
  fi
fi

echo "${RELEASE_TITLE}" > "${TITLE_FILE}"
echo "Wrote title to ${TITLE_FILE}: ${RELEASE_TITLE}"
