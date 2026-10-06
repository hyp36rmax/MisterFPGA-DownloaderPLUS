"""One fail-closed scheduled build and protected database publication cycle."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build import build
from tools.common.database import ValidationError, canonical_json
from tools.common.engine import ROOT, discover_modules, load_module, update_group

BRANCH = 'automation/database-updates'
TITLE = 'Update validated DownloaderPLUS databases'
CHECKS = (
    'verify_dist.py', 'check_module_catalog.py', 'check_readme_documentation.py',
    'audit_alternatives.py', 'audit_arcade_systems.py', 'audit_coinop_coverage.py',
    'audit_filters.py', 'audit_stg_matrix.py', 'audit_stg_master.py',
    'audit_stg_collection.py', 'check_documentation_encoding.py',
)


def run(arguments, root=ROOT, input_text=None):
    return subprocess.check_output(arguments, cwd=root, input=input_text,
                                   text=True, encoding='utf-8')


def git(*arguments, root=ROOT):
    return run(['git', *arguments], root)


def validate(root=ROOT):
    for check in CHECKS:
        subprocess.run([sys.executable, 'tools/' + check], cwd=root, check=True)


def plan(paths, names, validated, large_loss_passed, branch=BRANCH):
    if branch != BRANCH:
        raise ValidationError('Publication is restricted to the automation feature branch')
    if not validated or not large_loss_passed:
        raise ValidationError('Validation or source-loss protection failed; no publication')
    known = set(names)
    changed = set()
    for path in paths:
        parts = path.split('/')
        if len(parts) < 3 or parts[0] != 'dist' or parts[1] not in known or '..' in parts:
            raise ValidationError('Unexpected publication path: ' + path)
        changed.add(parts[1])
    return {'branch': branch, 'modules': sorted(changed), 'paths': sorted(set(paths)),
            'publish': bool(changed), 'validated': True, 'large_loss_passed': True}


def description(publication, root=ROOT):
    lines = ['Validated database updates rebuilt from current main and authoritative sources.', '',
             'Changed modules:']
    for name in publication['modules']:
        display = load_module(name)[0].get('display_name', name)
        manifest_path = 'dist/' + name + '/manifest.json'
        after = json.loads((root / manifest_path).read_text(encoding='utf-8'))
        try:
            before = json.loads(git('show', 'HEAD:' + manifest_path, root=root))
        except subprocess.CalledProcessError:
            before = {}
        source_keys = ('upstream_semantic_sha256', 'source_semantic_sha256', 'source_commit',
                       'source_fingerprints', 'contributors')
        source_changed = any(before.get(k) != after.get(k) for k in source_keys)
        files = [p.rsplit('/', 1)[-1] for p in publication['paths'] if p.startswith('dist/' + name + '/')]
        lines.append('- ' + display + ': ' + ', '.join(files) +
                     '; source provenance ' + ('changed' if source_changed else 'unchanged') + '.')
    lines += ['', 'Validation: safety tests, independent module builds, whole-distribution integrity,',
              'catalog, documentation, encoding, alternatives, registry/ownership, public coverage,',
              'filters, STG master and TATE checks passed.', '',
              'Source integrity and existing large-loss safeguards passed. No direct-main publication.']
    return '\n'.join(lines) + '\n'


def collect(root=ROOT):
    if git('status', '--porcelain', root=root).strip():
        raise ValidationError('Scheduled cycle requires a clean checkout of current main')
    names = discover_modules()
    owners = [n for n in names if 'source_module' not in load_module(n)[0]
              and load_module(n)[0].get('source_mode') != 'complete']
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=root, check=True)
    cache = {}
    for owner in owners:
        for name in update_group(owner):
            print(canonical_json(build(name, source_cache=cache)).decode('utf-8'), flush=True)
        validate(root)
    build('arcade-systems-complete', source_cache=cache)
    validate(root)
    paths = git('diff', '--name-only', '-z', 'HEAD', root=root).split('\0')
    paths += git('ls-files', '--others', '--exclude-standard', '-z', root=root).split('\0')
    return plan([p for p in paths if p], names, validated=True, large_loss_passed=True)


def api(endpoint, fields=None):
    args = ['gh', 'api', endpoint]
    if fields is not None:
        args += ['--method', 'POST', '--input', '-']
    return json.loads(run(args, input_text=json.dumps(fields) if fields is not None else None))


def choose_pr(pulls, repository):
    matching = [p for p in pulls if p['head']['ref'] == BRANCH and
                p['head']['repo'] and p['head']['repo']['full_name'] == repository]
    if len(matching) > 1:
        raise ValidationError('Multiple automation PRs require review')
    if matching and (matching[0]['draft'] or matching[0]['base']['ref'] != 'main'):
        raise ValidationError('Unexpected automation PR state requires review')
    return matching[0] if matching else None


def app_check(repository):
    inventory = api('installation/repositories?per_page=100')
    if inventory['total_count'] != 1 or inventory['repositories'][0]['full_name'] != repository:
        raise ValidationError('Publication installation must be limited to this repository')
    repo = api('repos/' + repository)
    if not repo['allow_auto_merge']:
        raise ValidationError('Normal repository auto-merge is not enabled')
    # Reading PRs confirms the installation can access the publication target.
    api('repos/' + repository + '/pulls?state=open&per_page=100')
    print('App authentication and single-repository installation verified; auto-merge enabled.')
    return repo


def graphql(query, variables):
    result = api('graphql', {'query': query, 'variables': variables})
    if result.get('errors'):
        raise ValidationError('Protected auto-merge configuration failed')
    return result['data']


def publish(publication, repository, root=ROOT):
    # No credential, branch, commit or PR operation on a successful no-change cycle.
    if not publication['publish']:
        print('No material changes; no commit, branch update or PR action.')
        return None
    publication = plan(publication['paths'], discover_modules(), publication['validated'],
                       publication['large_loss_passed'], publication['branch'])
    repo = app_check(repository)
    if repo['default_branch'] != 'main' or not repo['allow_merge_commit']:
        raise ValidationError('Repository merge convention changed; review required')
    base = git('rev-parse', 'HEAD', root=root).strip()
    credentials = ['-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential']
    remote_main = git(*credentials, 'ls-remote', 'origin', 'refs/heads/main', root=root).split()[0]
    if remote_main != base:
        raise ValidationError('Main advanced during validation; regenerate from current main')
    pr = choose_pr(api('repos/' + repository + '/pulls?state=open&per_page=100'), repository)
    old = git(*credentials, 'ls-remote', 'origin', 'refs/heads/' + BRANCH, root=root).split()
    previous = old[0] if old else ''
    # Pause any old pending auto-merge before replacing that PR's head.
    if pr and pr.get('auto_merge'):
        graphql('mutation($id:ID!){disablePullRequestAutoMerge(input:{pullRequestId:$id}){pullRequest{id}}}', {'id': pr['node_id']})
    body = description(publication, root)
    git('add', '--', *publication['paths'], root=root)
    staged = set(git('diff', '--cached', '--name-only', '-z', root=root).split('\0')) - {''}
    if staged != set(publication['paths']):
        raise ValidationError('Staged publication differs from the validated artifact plan')
    git('-c', 'user.name=DownloaderPLUS Updater', '-c', 'user.email=updater@users.noreply.github.com',
        'commit', '-m', TITLE, root=root)
    head = git('rev-parse', 'HEAD', root=root).strip()
    git(*credentials, 'push', '--force-with-lease=refs/heads/' + BRANCH + ':' + previous,
        'origin', 'HEAD:refs/heads/' + BRANCH, root=root)
    if pr:
        args = ['gh', 'api', 'repos/' + repository + '/pulls/' + str(pr['number']),
                '--method', 'PATCH', '--input', '-']
        pr = json.loads(run(args, root, json.dumps({'title': TITLE, 'body': body})))
    else:
        pr = api('repos/' + repository + '/pulls',
                 {'title': TITLE, 'body': body, 'head': BRANCH, 'base': 'main', 'draft': False})
    if pr['head']['sha'] != head:
        raise ValidationError('Automation PR head changed; protected auto-merge not enabled')
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as out:
        out.write('pr=' + str(pr['number']) + '\nhead=' + head + '\n')
    print('Protected automation publication: ' + pr['html_url'])
    return pr


def wait_validation(repository, number, head, timeout=900):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        pr = api('repos/' + repository + '/pulls/' + str(number))
        if pr['head']['sha'] != head:
            raise ValidationError('Automation PR head changed during hosted validation')
        runs = api('repos/' + repository + '/actions/runs?event=pull_request&head_sha=' + head + '&per_page=100')['workflow_runs']
        runs = [r for r in runs if r['name'] == 'Validate' and
                any(p['number'] == number for p in r.get('pull_requests', []))]
        if runs:
            latest = max(runs, key=lambda r: r['id'])
            if latest['status'] in {'waiting', 'action_required'}:
                raise ValidationError('Required PR validation needs unexpected manual approval')
            if latest['status'] == 'completed':
                if latest['conclusion'] != 'success':
                    raise ValidationError('Required PR validation failed: ' + str(latest['conclusion']))
                print('Normal PR Validate workflow passed automatically.')
                return
        time.sleep(15)
    raise ValidationError('Normal required PR validation did not complete automatically')


def enable_auto_merge(repository, number, head):
    pr = api('repos/' + repository + '/pulls/' + str(number))
    if pr['head']['sha'] != head or choose_pr([pr], repository) is None:
        raise ValidationError('Unexpected automation PR; auto-merge prohibited')
    # This mutation enables protected auto-merge only, never a direct merge endpoint.
    data = graphql('mutation($id:ID!){enablePullRequestAutoMerge(input:{pullRequestId:$id,mergeMethod:MERGE}){pullRequest{autoMergeRequest{enabledAt} merged}}}',
                   {'id': pr['node_id']})['enablePullRequestAutoMerge']['pullRequest']
    if not data['autoMergeRequest'] and not data['merged']:
        raise ValidationError('Protected auto-merge was not enabled')
    print('Normal protected auto-merge enabled: ' + pr['html_url'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('collect', 'publish', 'check-app', 'wait-validation', 'enable-auto-merge'))
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--pr', type=int)
    parser.add_argument('--head')
    args = parser.parse_args()
    repository = os.environ.get('GITHUB_REPOSITORY', '')
    try:
        if args.mode == 'check-app':
            app_check(repository)
        elif args.mode == 'wait-validation':
            wait_validation(repository, args.pr, args.head)
        elif args.mode == 'enable-auto-merge':
            enable_auto_merge(repository, args.pr, args.head)
        elif args.mode == 'collect':
            publication = collect()
            args.plan.write_bytes(canonical_json(publication))
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as out:
                out.write('changed=' + str(publication['publish']).lower() + '\n')
        else:
            publish(json.loads(args.plan.read_text(encoding='utf-8')), repository)
    except (ValidationError, subprocess.CalledProcessError, OSError, ValueError) as exc:
        # Never include command output or credential-bearing response bodies.
        parser.exit(1, 'Scheduled database cycle failed; no protected-main bypass: ' +
                    (str(exc) if isinstance(exc, ValidationError) else type(exc).__name__) + '\n')


if __name__ == '__main__':
    main()
