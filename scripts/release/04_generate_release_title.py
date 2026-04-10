#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

CONTEXT_PATH = Path('/tmp/release-context.json')
SUMMARY_PATH = Path('/tmp/change-summary.md')
TITLE_PATH = Path('/tmp/release-title.txt')

if not CONTEXT_PATH.exists() or not SUMMARY_PATH.exists():
    raise SystemExit('Missing required context files.')

context = json.loads(CONTEXT_PATH.read_text(encoding='utf-8'))
new_tag = context['new_tag']
summary_body = SUMMARY_PATH.read_text(encoding='utf-8').strip()

gh_token = os.environ.get('GH_TOKEN', '').strip()
if not gh_token:
    raise SystemExit('GH_TOKEN is required.')

copilot_token = gh_token
copilot_model = os.environ.get('COPILOT_MODEL', 'gpt-4o').strip() or 'gpt-4o'

release_title = f'Release {new_tag}'
request_body = {
    'model': copilot_model,
    'temperature': 0.2,
    'messages': [
        {
            'role': 'system',
            'content': 'Generate one short professional GitHub release title. Return only plain text. Max 70 characters.',
        },
        {
            'role': 'user',
            'content': f'Tag: {new_tag}\nChanges:\n{summary_body}',
        },
    ],
}

try:
    req = urllib.request.Request(
        url='https://api.githubcopilot.com/chat/completions',
        method='POST',
        data=json.dumps(request_body).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {copilot_token}',
            'Content-Type': 'application/json',
            'Copilot-Integration-Id': 'github-actions',
            'Editor-Version': 'github-actions/1.0.0',
            'Editor-Plugin-Version': 'copilot-chat/1.0.0',
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        generated = (data.get('choices', [{}])[0].get('message', {}).get('content') or '').strip().splitlines()[0].strip()
        if generated:
            release_title = generated
except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError):
    pass

TITLE_PATH.write_text(release_title + '\n', encoding='utf-8')
print(f'Wrote title to {TITLE_PATH}: {release_title}')
