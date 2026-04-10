#!/usr/bin/env python3
import json
import os
import urllib.request
from pathlib import Path

CONTEXT_PATH = Path('/tmp/release-context.json')
TITLE_PATH = Path('/tmp/release-title.txt')
NOTES_PATH = Path('/tmp/release-notes.md')

if not CONTEXT_PATH.exists() or not TITLE_PATH.exists() or not NOTES_PATH.exists():
    raise SystemExit('Missing required context files.')

context = json.loads(CONTEXT_PATH.read_text(encoding='utf-8'))
repo = context['repo']
new_tag = context['new_tag']
sha = context['sha']

release_title = TITLE_PATH.read_text(encoding='utf-8').strip()
release_notes = NOTES_PATH.read_text(encoding='utf-8').strip()

gh_token = os.environ.get('GH_TOKEN', '').strip()
if not gh_token:
    raise SystemExit('GH_TOKEN is required.')

headers = {
    'Authorization': f'Bearer {gh_token}',
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/json',
}

get_req = urllib.request.Request(
    url=f'https://api.github.com/repos/{repo}/releases/tags/{new_tag}',
    method='GET',
    headers=headers,
)
with urllib.request.urlopen(get_req) as resp:
    release = json.loads(resp.read().decode('utf-8'))

release_id = release['id']
update_payload = {
    'tag_name': new_tag,
    'target_commitish': sha,
    'name': release_title,
    'body': release_notes,
}

patch_req = urllib.request.Request(
    url=f'https://api.github.com/repos/{repo}/releases/{release_id}',
    method='PATCH',
    data=json.dumps(update_payload).encode('utf-8'),
    headers=headers,
)
with urllib.request.urlopen(patch_req):
    pass

print(f'Release {new_tag} updated successfully.')
