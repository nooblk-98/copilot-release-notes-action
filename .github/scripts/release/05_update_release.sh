#!/usr/bin/env bash
set -euo pipefail

CONTEXT_FILE="/tmp/release-context.env"
TITLE_FILE="/tmp/release-title.txt"
NOTES_FILE="/tmp/release-notes.md"

if [[ ! -f "${CONTEXT_FILE}" || ! -f "${TITLE_FILE}" || ! -f "${NOTES_FILE}" ]]; then
  echo "Missing required context files."
  exit 1
fi

# shellcheck disable=SC1090
source "${CONTEXT_FILE}"
RELEASE_TITLE="$(cat "${TITLE_FILE}")"

gh release edit "${NEW_TAG}" \
  --title "${RELEASE_TITLE}" \
  --notes-file "${NOTES_FILE}" \
  --target "${SHA}"

echo "Release ${NEW_TAG} updated successfully."
