#!/usr/bin/env python3
import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

CONTEXT_PATH = Path(tempfile.gettempdir()) / 'release-context.json'
SUMMARY_PATH = Path(tempfile.gettempdir()) / 'change-summary.md'
NOTES_PATH = Path(tempfile.gettempdir()) / 'release-notes.md'
API_TIMEOUT = 30

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


def categorize_changes(summary: str) -> dict:
    categories = {
        'new_features': [],
        'bug_fixes': [],
        'updates': [],
        'other_changes': [],
    }
    for raw_line in summary.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if any(k in lower for k in ['feat', 'feature', 'add', 'introduc', 'implement', 'new']):
            categories['new_features'].append(line)
        elif any(k in lower for k in ['fix', 'bug', 'hotfix', 'patch', 'error', 'issue', 'resolve']):
            categories['bug_fixes'].append(line)
        elif any(k in lower for k in ['update', 'upgrade', 'improve', 'enhanc', 'refactor', 'perf', 'optimi', 'chore']):
            categories['updates'].append(line)
        else:
            categories['other_changes'].append(line)
    return categories


def section(title: str, items: list[str]) -> str:
    if not items:
        return ''
    body = '\n'.join(items)
    return f'### {title}\n{body}\n'


def remove_full_changelog_lines(text: str) -> str:
    kept = []
    for raw in text.splitlines():
        if raw.strip().lower().startswith('full changelog:'):
            continue
        kept.append(raw)
    return '\n'.join(kept).strip()


def remove_duplicate_release_heading(text: str, tag: str) -> str:
    lines = text.splitlines()
    if not lines:
        return text.strip()

    first = lines[0].strip().lower()
    expected = f'release {tag}'.lower()
    if first.startswith('#'):
        heading_text = first.lstrip('#').strip()
        if heading_text == expected:
            lines = lines[1:]
            while lines and not lines[0].strip():
                lines = lines[1:]
    return '\n'.join(lines).strip()


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
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise SystemExit(f'GitHub API error {e.code} on {method} {endpoint}: {e.reason}')
    except urllib.error.URLError as e:
        raise SystemExit(f'GitHub API request failed for {endpoint}: {e.reason}')


payload = {
    'tag_name': new_tag,
    'target_commitish': sha,
}
if previous_tag:
    payload['previous_tag_name'] = previous_tag

generated = gh_api('POST', f'/repos/{repo}/releases/generate-notes', payload)
github_body = generated.get('body', '').strip()
clean_github_body = remove_full_changelog_lines(github_body)

changes = categorize_changes(summary_body)
default_notes = (
    f'### Summary\n'
    f'- Tag: `{new_tag}`\n'
    f'- Previous tag: `{previous_tag or "none"}`\n\n'
    f'{section("New Features", changes["new_features"])}\n'
    f'{section("Bug Fixes", changes["bug_fixes"])}\n'
    f'{section("Updates", changes["updates"])}\n'
    f'{section("Other Changes", changes["other_changes"])}\n'
    f'### GitHub Generated Notes\n'
    f'{clean_github_body or "- No GitHub generated notes."}\n'
)

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
                'Create release notes in markdown with sections: Summary, New Features, Bug Fixes, Updates, and Other Changes. '
                f'Tag: {new_tag}. Previous tag: {previous_tag or "none"}\n\n'
                f'Commit summary:\n{summary_body}\n\n'
                f'GitHub generated notes:\n{clean_github_body}\n\n'
                'Do not duplicate a "Full Changelog" heading and do not repeat the same changelog line twice. '
                'Do not include empty category sections. Do not include a References section.'
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
            'Authorization': f'Bearer {gh_token}',
            'Content-Type': 'application/json',
            'Copilot-Integration-Id': 'github-actions',
            'Editor-Version': 'github-actions/1.0.0',
            'Editor-Plugin-Version': 'copilot-chat/1.0.0',
        },
    )
    with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        ai_notes = (data.get('choices', [{}])[0].get('message', {}).get('content') or '').strip()
except urllib.error.HTTPError as e:
    print(f'Warning: Copilot API returned HTTP {e.code}: {e.reason} — falling back to default notes.')
except urllib.error.URLError as e:
    print(f'Warning: Copilot API unreachable: {e.reason} — falling back to default notes.')
except (KeyError, IndexError, json.JSONDecodeError) as e:
    print(f'Warning: Unexpected Copilot API response ({e}) — falling back to default notes.')

final_notes = remove_full_changelog_lines(ai_notes or default_notes)
final_notes = remove_duplicate_release_heading(final_notes, new_tag)
NOTES_PATH.write_text(final_notes.rstrip() + '\n', encoding='utf-8')
print(f'Wrote release notes to {NOTES_PATH}')
