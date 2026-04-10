#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

CONTEXT_PATH = Path('/tmp/release-context.json')
SUMMARY_PATH = Path('/tmp/change-summary.md')
NOTES_PATH = Path('/tmp/release-notes.md')

if not CONTEXT_PATH.exists() or not SUMMARY_PATH.exists():
    raise SystemExit('Missing required context files.')

context = json.loads(CONTEXT_PATH.read_text(encoding='utf-8'))
repo = context['repo']
sha = context['sha']
new_tag = context['new_tag']
previous_tag = context.get('previous_tag', '')
summary_body = SUMMARY_PATH.read_text(encoding='utf-8').strip()

gh_token = os.environ.get('GH_TOKEN', '').strip()
if not gh_token:
    raise SystemExit('GH_TOKEN is required.')


def gh_api(method: str, endpoint: str, payload: dict) -> dict:
    url = f'https://api.github.com{endpoint}'
    req = urllib.request.Request(
        url=url,
        method=method,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {gh_token}',
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


payload = {
    'tag_name': new_tag,
    'target_commitish': sha,
}
if previous_tag:
    payload['previous_tag_name'] = previous_tag

generated = gh_api('POST', f'/repos/{repo}/releases/generate-notes', payload)
github_body = generated.get('body', '').strip()

default_notes = (
    f'## Release {new_tag}\n\n'
    f'### Highlights\n{summary_body}\n\n'
    f'### Full Changelog\n{github_body}\n'
)

copilot_token = os.environ.get('COPILOT_TOKEN', '').strip() or gh_token
copilot_model = os.environ.get('COPILOT_MODEL', 'gpt-4o').strip() or 'gpt-4o'
ai_notes = ''

request_body = {
    'model': copilot_model,
    'temperature': 0.2,
    'messages': [
        {
            'role': 'system',
            'content': 'You write concise professional GitHub release notes in markdown. Keep facts grounded in provided content only.',
        },
        {
            'role': 'user',
            'content': (
                'Create release notes in markdown with sections: Summary, New Features, Bug Fixes, Improvements, and Full Changelog. '
                f'Tag: {new_tag}. Previous tag: {previous_tag or "none"}\n\n'
                f'Commit summary:\n{summary_body}\n\n'
                f'GitHub generated notes:\n{github_body}'
            ),
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
        ai_notes = (data.get('choices', [{}])[0].get('message', {}).get('content') or '').strip()
except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError):
    ai_notes = ''

NOTES_PATH.write_text((ai_notes or default_notes).rstrip() + '\n', encoding='utf-8')
print(f'Wrote release notes to {NOTES_PATH}')
