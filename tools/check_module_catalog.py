"""Validate the README catalog against configured, registered published modules."""
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.common.database import ValidationError
from tools.common.engine import ROOT, discover_modules, load_module
from tools.common.arcade_systems import NAMESPACE, eligible_modules, registry
from tools.verify_dist import verify_one

# Presentation priority only; published inventory is discovered below.
PRIORITY = ('coinop-collection', 'pgm-ezio', 'arcade-systems-complete',
            'arcade-systems-reserve', 'pgm-ezio-arcade-systems')


def display_name(config, root):
    if 'display_name' in config:
        return config['display_name']
    heading = (root / 'modules' / config['name'] / 'README.md').read_text(encoding='utf-8').splitlines()[0]
    if not heading.startswith('# '):
        raise ValidationError('Missing display name: ' + config['name'])
    return heading[2:].removesuffix(' module')


def source_label(config, root):
    mode = config.get('source_mode', 'transformation')
    if mode == 'transformation':
        return 'Authoritative database transformation'
    if mode == 'complete':
        return 'Approved Arcade Systems aggregate'
    if mode == 'documentation':
        return 'Navigation guidance'
    if mode == 'coinop-family':
        return 'Coin-Op database selection'
    if mode == 'repository':
        if 'source_module' in config:
            parent, _ = load_module(config['source_module'], root)
            return 'Shared ' + display_name(parent, root).split(' (')[0] + ' presentation'
        return 'Repository distribution'
    if mode == 'database':
        authority = config['upstream_db_id']
        labels = {'jtcores': 'JTCORES', 'meathax/meatcores': 'MeatCores',
                  'distribution_mister': 'Official MiSTer'}
        return labels.get(authority, authority) + ' database selection'
    raise ValidationError('Unrecognized catalog source mode: ' + mode)


def published_inventory(root=ROOT):
    root = Path(root)
    configs = {name: load_module(name, root) for name in discover_modules(root)}
    approved = registry(root)['modules']
    eligible_modules(root)  # Validate authorities and canonical configured roots.
    artifacts = sorted((root / 'dist').glob('*/*.json.zip'))
    inventory = []
    seen = set()
    for artifact in artifacts:
        name = artifact.parent.name
        if name not in configs:
            raise ValidationError('Published artifact without module configuration: ' + str(artifact.relative_to(root)))
        if name in seen:
            raise ValidationError('Multiple published artifacts for module: ' + name)
        seen.add(name)
        config, policy = configs[name]
        if artifact.name != name + '.json.zip':
            raise ValidationError('Incorrect published artifact filename: ' + str(artifact.relative_to(root)))
        database, _ = verify_one(name, root, verbose=False)
        if database['db_id'] != config['derived_db_id']:
            raise ValidationError('Published database identity differs from configuration: ' + name)
        mode = config.get('source_mode')
        if mode in {'complete', 'documentation'}:
            destination = NAMESPACE.rstrip('/')
        elif name in approved:
            roots = approved[name]['destination_roots']
            if len(roots) != 1:
                raise ValidationError('Individual module has ambiguous navigation roots: ' + name)
            destination = roots[0]
        elif 'target_folder' in config:
            destination = '_Arcade/' + config['target_folder']
        else:
            destination = policy.destination('_Arcade', 'folders')
        if mode not in {'complete', 'documentation'} and destination not in database['folders']:
            raise ValidationError('Configured navigation root absent from published artifact: ' + name)
        if destination.startswith(NAMESPACE):
            if not destination[len(NAMESPACE):].split('/')[0].startswith('_'):
                raise ValidationError('Published Arcade Systems destination missing leading underscore: ' + name)
        inventory.append({'name': name, 'display_name': display_name(config, root),
                          'source_mode': source_label(config, root),
                          'destination': destination.rstrip('/') + '/', 'artifact': artifact.name})
    if len({item['display_name'] for item in inventory}) != len(inventory):
        raise ValidationError('Published module display names are not unique')
    priority = {name: i for i, name in enumerate(PRIORITY)}
    return sorted(inventory, key=lambda item: (priority.get(item['name'], len(PRIORITY)), item['display_name'].casefold()))


def catalog_rows(readme):
    lines = readme.splitlines()
    start = lines.index('## Available modules') + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith('## ')), len(lines))
    rows = []
    for i in range(start, end):
        if not lines[i].startswith('|'):
            continue
        cells = [cell.strip() for cell in lines[i].strip('|').split('|')]
        if cells == ['Module', 'Source mode', 'Navigation destination', 'Artifact'] or all(set(cell) <= {'-', ':'} for cell in cells):
            continue
        if len(cells) != 4:
            raise ValidationError(f'README.md:{i + 1}: expected four catalog columns')
        rows.append({'line': i + 1, 'display_name': cells[0], 'source_mode': cells[1],
                     'destination': cells[2].strip('`'), 'artifact': cells[3].strip('`')})
    return rows


def validate_rows(rows, inventory):
    expected = {item['display_name']: item for item in inventory}
    issues = []
    seen = set()
    for row in rows:
        name = row['display_name']
        location = f"README.md:{row['line']}"
        if name in seen:
            issues.append({'kind': 'duplicate', 'location': location, 'module': name})
        seen.add(name)
        destination = row['destination']
        if destination.startswith(NAMESPACE) and destination != NAMESPACE:
            if not destination[len(NAMESPACE):].split('/')[0].startswith('_'):
                issues.append({'kind': 'leading_underscore', 'location': location, 'module': name})
        if name not in expected:
            issues.append({'kind': 'stale', 'location': location, 'module': name})
            continue
        for field in ('artifact', 'destination', 'source_mode'):
            if row[field] != expected[name][field]:
                issues.append({'kind': field, 'location': location, 'module': name,
                               'actual': row[field], 'expected': expected[name][field]})
    for name in expected.keys() - seen:
        issues.append({'kind': 'missing', 'location': 'README.md: Available modules', 'module': name})
    if [row['display_name'] for row in rows] != [item['display_name'] for item in inventory]:
        issues.append({'kind': 'order', 'location': 'README.md: Available modules'})
    return issues


def main():
    try:
        inventory = published_inventory()
        rows = catalog_rows((ROOT / 'README.md').read_text(encoding='utf-8'))
        issues = validate_rows(rows, inventory)
        print(json.dumps({'published_modules': len(inventory), 'table_rows': len(rows),
                          'status': 'FAIL' if issues else 'PASS', 'issues': issues}, indent=2))
        return bool(issues)
    except (ValueError, OSError, KeyError) as exc:
        print('Module catalog validation failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
