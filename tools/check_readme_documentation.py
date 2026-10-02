"""Report README hardware inventory and local documentation link mismatches."""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.check_module_catalog import published_inventory
from tools.common.arcade_systems import ROOT, eligible_modules, registry
from tools.common.database import ValidationError


def system_inventory(root=ROOT):
    published = {item['name'] for item in published_inventory(root)}
    entries = registry(root)['modules']
    groups = json.loads((root / 'docs/arcade-systems-presentation.json').read_text(encoding='utf-8'))
    active, reserve = {}, set()
    for module in eligible_modules(root):
        if module not in published:
            raise ValidationError('Registered system lacks published artifact: ' + module)
        entry = entries[module]
        for destination in entry['destination_roots']:
            name = destination.rsplit('/', 1)[1][1:]
            if entry['management_state'] == 'reserve':
                reserve.add(name)
                continue
            matches = [g for g in groups if name == g['prefix'] or name.startswith(g['prefix'] + ' ')]
            if len(matches) != 1:
                raise ValidationError('System grouping needs review: ' + name)
            group = matches[0]
            label = name[len(group['prefix']) + 1:] if group['strip_prefix'] else name
            key = (group['group'], label)
            if key in active:
                raise ValidationError('Duplicate registry system: ' + name)
            active[key] = name
    return active, reserve


def validate_systems(text, active, reserve):
    issues, seen, reserve_seen = [], set(), set()
    section = text.split('## Available Arcade Systems\n', 1)[1].split('\n## ', 1)[0]
    available, reserved = section.split('### Reserve Systems\n', 1)
    for line in available.splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if cells[0] == 'Manufacturer or family' or set(cells[0]) <= {'-', ':'}:
            continue
        if len(cells) != 2:
            issues.append('Invalid systems table row: ' + line)
            continue
        for label in cells[1].split(', '):
            key = (cells[0], label)
            if key in seen:
                issues.append('Duplicate system: ' + str(key))
            seen.add(key)
            if key not in active:
                issues.append('Unavailable or incorrectly grouped system: ' + str(key))
    for line in reserved.splitlines():
        if line.startswith('- '):
            name = line[2:]
            if name in reserve_seen:
                issues.append('Duplicate Reserve system: ' + name)
            reserve_seen.add(name)
            if name not in reserve:
                issues.append('Unavailable or misclassified Reserve system: ' + name)
    issues.extend('Missing system: ' + str(key) for key in sorted(active.keys() - seen))
    issues.extend('Missing Reserve system: ' + name for name in sorted(reserve - reserve_seen))
    return issues


def documentation_issues(root=ROOT):
    issues = []
    files = [root / 'README.md', *sorted((root / 'docs').rglob('*.md')), *sorted((root / 'modules').rglob('*.md'))]
    for file in files:
        text = file.read_text(encoding='utf-8')
        for number, line in enumerate(text.splitlines(), 1):
            if 'gitee' in line.casefold():
                issues.append(f'{file.relative_to(root)}:{number}: public source wording')
            for target in re.findall(r'\]\(([^)]+)\)', line):
                target = target.split(' "', 1)[0].strip('<>')
                url = urlsplit(target)
                if url.scheme or target.startswith('//'):
                    continue
                destination = file.parent / unquote(url.path) if url.path else file
                if not destination.exists():
                    issues.append(f'{file.relative_to(root)}:{number}: missing link {target}')
                elif url.fragment and destination.suffix == '.md':
                    headings = re.findall(r'^#{1,6} (.+)$', destination.read_text(encoding='utf-8'), re.M)
                    anchors = {re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-') for heading in headings}
                    if unquote(url.fragment) not in anchors:
                        issues.append(f'{file.relative_to(root)}:{number}: missing heading {target}')
    return issues


def main():
    try:
        active, reserve = system_inventory()
        issues = validate_systems((ROOT / 'README.md').read_text(encoding='utf-8'), active, reserve)
        issues += documentation_issues()
        print(json.dumps({'available_systems': len(active), 'reserve_systems': len(reserve),
                          'status': 'FAIL' if issues else 'PASS', 'issues': issues}, indent=2))
        return bool(issues)
    except (ValueError, IndexError, KeyError, OSError) as exc:
        print('README documentation validation failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
