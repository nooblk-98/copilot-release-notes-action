#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

CONTEXT_PATH = Path('/tmp/release-context.json')


def run_git(*args: str) -> str:
    return subprocess.check_output(['git', *args], text=True).strip()


repo = os.environ['GITHUB_REPOSITORY']
sha = os.environ.get('RELEASE_TARGET') or os.environ.get('GITHUB_SHA', '')
release_tag = os.environ.get('RELEASE_TAG', '').strip()

if release_tag:
    new_tag = release_tag
else:
    new_tag = run_git('describe', '--tags', '--abbrev=0')

all_tags = run_git('tag', '--sort=-version:refname').splitlines()
previous_tag = ''
for tag in all_tags:
    if tag != new_tag:
        previous_tag = tag
        break

context = {
    'repo': repo,
    'sha': sha,
    'new_tag': new_tag,
    'previous_tag': previous_tag,
}

CONTEXT_PATH.write_text(json.dumps(context), encoding='utf-8')
print(f'Saved release context to {CONTEXT_PATH}')
print(f'New release: {new_tag}')
print(f"Previous release: {previous_tag or 'none'}")
