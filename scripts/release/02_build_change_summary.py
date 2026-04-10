#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

CONTEXT_PATH = Path('/tmp/release-context.json')
SUMMARY_PATH = Path('/tmp/change-summary.md')

if not CONTEXT_PATH.exists():
    raise SystemExit(f'Missing {CONTEXT_PATH}.')

context = json.loads(CONTEXT_PATH.read_text(encoding='utf-8'))
new_tag = context['new_tag']
previous_tag = context.get('previous_tag', '')

if previous_tag:
    rev_range = f'{previous_tag}..{new_tag}'
else:
    rev_range = new_tag

result = subprocess.check_output(
    ['git', 'log', '--pretty=format:- %s (%h)', rev_range],
    text=True,
).strip()

if not result:
    result = '- No commit messages detected for this release range.'

SUMMARY_PATH.write_text(result + '\n', encoding='utf-8')
print(f'Wrote change summary to {SUMMARY_PATH}')
