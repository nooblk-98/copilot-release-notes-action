#!/usr/bin/env bash
set -euo pipefail

CONTEXT_FILE="/tmp/release-context.env"
SUMMARY_FILE="/tmp/change-summary.md"

if [[ ! -f "${CONTEXT_FILE}" ]]; then
  echo "Missing ${CONTEXT_FILE}."
  exit 1
fi

# shellcheck disable=SC1090
source "${CONTEXT_FILE}"

if [[ -n "${PREVIOUS_TAG}" ]]; then
  git log --pretty=format:'- %s (%h)' "${PREVIOUS_TAG}".."${NEW_TAG}" > "${SUMMARY_FILE}"
else
  git log --pretty=format:'- %s (%h)' "${NEW_TAG}" > "${SUMMARY_FILE}"
fi

if [[ ! -s "${SUMMARY_FILE}" ]]; then
  echo "- No commit messages detected for this release range." > "${SUMMARY_FILE}"
fi

echo "Wrote change summary to ${SUMMARY_FILE}"
