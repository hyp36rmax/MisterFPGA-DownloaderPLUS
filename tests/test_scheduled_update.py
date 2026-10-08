"""Scheduled publication safety, batching and protected PR regression coverage."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.common.database import ValidationError
from tools import scheduled_update as updater

REPO = 'hyp36rmax/MisterFPGA-DownloaderPLUS'


def pull(number=1):
    return {'number': number, 'node_id': 'PR_1', 'draft': False,
            'base': {'ref': 'main'}, 'head': {'ref': updater.BRANCH, 'sha': 'new',
            'repo': {'full_name': REPO}}, 'state': 'open', 'merged': False, 'mergeable_state': 'clean', 'auto_merge': None, 'html_url': 'https://github.com/' + REPO + '/pull/1'}


class ScheduledPublicationTests(unittest.TestCase):
    def test_no_change_performs_no_commit_push_pr_or_authentication(self):
        publication = updater.plan([], ['one'], True, True)
        with patch.object(updater, 'git') as git, patch.object(updater, 'api') as api:
            self.assertIsNone(updater.publish(publication, REPO))
        git.assert_not_called(); api.assert_not_called()

    def test_multiple_modules_form_one_deterministic_cycle(self):
        paths = ['dist/two/manifest.json', 'dist/one/one.json.zip', 'dist/one/manifest.json']
        p = updater.plan(paths, ['two', 'one'], True, True)
        self.assertEqual(p['modules'], ['one', 'two'])
        self.assertEqual(p, updater.plan(list(reversed(paths)), ['one', 'two'], True, True))
        self.assertTrue(p['publish'])

    def test_invalid_validation_or_large_loss_never_publishes(self):
        for validated, loss in [(False, True), (True, False), (False, False)]:
            with self.assertRaises(ValidationError):
                updater.plan(['dist/one/one.json.zip'], ['one'], validated, loss)

    def test_direct_main_and_unrelated_paths_are_prohibited(self):
        with self.assertRaises(ValidationError):
            updater.plan(['dist/one/manifest.json'], ['one'], True, True, branch='main')
        for path in ['README.md', 'dist/unknown/x', 'dist/one/../main', '.github/workflows/x']:
            with self.assertRaises(ValidationError): updater.plan([path], ['one'], True, True)

    def test_existing_pr_is_selected_and_duplicates_fail_closed(self):
        p = pull()
        self.assertIs(updater.choose_pr([p], REPO), p)
        self.assertIsNone(updater.choose_pr([], REPO))
        with self.assertRaises(ValidationError): updater.choose_pr([p, pull(2)], REPO)
        p['draft'] = True
        with self.assertRaises(ValidationError): updater.choose_pr([p], REPO)

    def test_build_failure_stops_before_whole_validation_or_publication(self):
        with patch.object(updater, 'classification_holds', return_value=(set(), [])), patch.object(updater, 'git', return_value=''), patch.object(updater, 'discover_modules', return_value=['one']), \
             patch.object(updater, 'load_module', return_value=({}, None)), patch.object(updater.subprocess, 'run'), \
             patch.object(updater, 'update_group', return_value=['one']), \
             patch.object(updater, 'build', side_effect=ValidationError('source loss')), patch.object(updater, 'validate') as validate:
            with self.assertRaises(ValidationError): updater.collect()
        validate.assert_not_called()

    def test_validation_failure_stops_cycle_before_plan(self):
        with patch.object(updater, 'classification_holds', return_value=(set(), [])), patch.object(updater, 'git', return_value=''), patch.object(updater, 'discover_modules', return_value=['one']), \
             patch.object(updater, 'load_module', return_value=({}, None)), patch.object(updater.subprocess, 'run'), \
             patch.object(updater, 'update_group', return_value=['one']), patch.object(updater, 'build', return_value={}), \
             patch.object(updater, 'validate', side_effect=subprocess.CalledProcessError(1, 'check')), patch.object(updater, 'plan') as plan:
            with self.assertRaises(subprocess.CalledProcessError): updater.collect()
        plan.assert_not_called()

    def test_hosted_validation_requires_actual_success_without_manual_approval(self):
        workflow = {'id': 3, 'name': 'Validate', 'pull_requests': [{'number': 1}],
                    'status': 'completed', 'conclusion': 'success'}
        with patch.object(updater, 'api', side_effect=[pull(), {'workflow_runs': [workflow]}]):
            updater.wait_validation(REPO, 1, 'new')
        for status, conclusion in [('waiting', None), ('completed', 'failure'), ('completed', 'action_required')]:
            bad = {**workflow, 'status': status, 'conclusion': conclusion}
            with patch.object(updater, 'api', side_effect=[pull(), {'workflow_runs': [bad]}]):
                with self.assertRaises(ValidationError): updater.wait_validation(REPO, 1, 'new')
        with patch.object(updater.time, 'monotonic', side_effect=[0, 901]):
            with self.assertRaises(ValidationError): updater.wait_validation(REPO, 1, 'new')

    def test_auto_merge_uses_enable_mutation_only(self):
        with patch.object(updater, 'api', return_value=pull()), patch.object(updater, 'graphql',
             return_value={'enablePullRequestAutoMerge': {'pullRequest': {'autoMergeRequest': {'enabledAt': 'now'}, 'merged': False, 'headRefOid': 'new'}}}) as mutation:
            updater.enable_auto_merge(REPO, 1, 'new')
        self.assertIn('enablePullRequestAutoMerge', mutation.call_args.args[0])
        self.assertNotIn('mergePullRequest(', mutation.call_args.args[0])
        with patch.object(updater, 'api', return_value=pull()):
            with self.assertRaises(ValidationError): updater.enable_auto_merge(REPO, 1, 'other')

    def test_transient_states_retry_then_enable_once(self):
        eligible = pull()
        for state in ('unstable', 'unknown', 'pending'):
            transient = {**pull(), 'mergeable_state': state}
            with patch.object(updater, 'api', side_effect=[transient, eligible]), \
                 patch.object(updater.time, 'sleep') as sleep, patch.object(updater, 'graphql', return_value={
                     'enablePullRequestAutoMerge': {'pullRequest': {
                         'autoMergeRequest': {'enabledAt': 'now'}, 'merged': False, 'headRefOid': 'new'}}}) as mutation:
                updater.enable_auto_merge(REPO, 1, 'new')
                sleep.assert_called_once()
                mutation.assert_called_once()

    def test_transient_then_merged_is_success_without_mutation(self):
        with patch.object(updater, 'api', side_effect=[{**pull(), 'mergeable_state': 'unstable'},
             {**pull(), 'state': 'closed', 'merged': True}]), patch.object(updater.time, 'sleep'), \
             patch.object(updater, 'graphql') as mutation:
            updater.enable_auto_merge(REPO, 1, 'new')
        mutation.assert_not_called()

    def test_already_auto_merge_enabled_succeeds_without_mutation(self):
        with patch.object(updater, 'api', return_value={**pull(), 'auto_merge': {'enabled_at': 'now'}}), \
             patch.object(updater, 'graphql') as mutation:
            updater.enable_auto_merge(REPO, 1, 'new')
        mutation.assert_not_called()

    def test_persistent_transient_state_times_out(self):
        with patch.object(updater, 'api', return_value={**pull(), 'mergeable_state': 'unknown'}), \
             patch.object(updater.time, 'monotonic', side_effect=[0, 0, 1, 301]), \
             patch.object(updater.time, 'sleep') as sleep, patch.object(updater, 'graphql') as mutation:
            with self.assertRaisesRegex(ValidationError, 'timed out'):
                updater.enable_auto_merge(REPO, 1, 'new')
        sleep.assert_called_once_with(15)
        mutation.assert_not_called()

    def test_closed_conflicting_or_blocked_pr_fails(self):
        for changes in ({'state': 'closed'}, {'mergeable_state': 'dirty'}, {'mergeable_state': 'blocked'},
                        {'head': {**pull()['head'], 'sha': 'replaced'}},
                        {'state': 'closed', 'merged': True, 'head': {**pull()['head'], 'sha': 'replaced'}}):
            with patch.object(updater, 'api', return_value={**pull(), **changes}), patch.object(updater, 'graphql') as mutation:
                with self.assertRaises(ValidationError): updater.enable_auto_merge(REPO, 1, 'new')
            mutation.assert_not_called()

    def test_head_change_while_waiting_and_mutation_response_are_rejected(self):
        with patch.object(updater, 'api', side_effect=[{**pull(), 'mergeable_state': 'unstable'},
             {**pull(), 'head': {**pull()['head'], 'sha': 'other'}}]), patch.object(updater.time, 'sleep'):
            with self.assertRaises(ValidationError): updater.enable_auto_merge(REPO, 1, 'new')
        with patch.object(updater, 'api', return_value=pull()), patch.object(updater, 'graphql', return_value={
             'enablePullRequestAutoMerge': {'pullRequest': {'autoMergeRequest': {}, 'merged': False, 'headRefOid': 'other'}}}):
            with self.assertRaises(ValidationError): updater.enable_auto_merge(REPO, 1, 'new')

    def test_mutation_settling_race_retries_but_access_failure_does_not(self):
        success = {'enablePullRequestAutoMerge': {'pullRequest': {
            'autoMergeRequest': {'enabledAt': 'now'}, 'merged': False, 'headRefOid': 'new'}}}
        with patch.object(updater, 'api', return_value=pull()), patch.object(updater.time, 'sleep') as sleep, \
             patch.object(updater, 'graphql', side_effect=[updater.TransientMergeState('settling'), success]) as mutation:
            updater.enable_auto_merge(REPO, 1, 'new')
        self.assertEqual(mutation.call_count, 2)
        sleep.assert_called_once()
        with patch.object(updater, 'api', side_effect=subprocess.CalledProcessError(1, 'gh')), \
             patch.object(updater.time, 'sleep') as sleep:
            with self.assertRaises(subprocess.CalledProcessError): updater.enable_auto_merge(REPO, 1, 'new')
        sleep.assert_not_called()

    def test_graphql_classifies_only_known_timing_errors(self):
        for message in ('Pull request is in unstable status', 'Pull request is in unknown status', 'Pull request is in pending status'):
            error = {'errors': [{'message': message}]}
            for response in (error, subprocess.CalledProcessError(1, 'gh', output=__import__('json').dumps(error))):
                with patch.object(updater, 'api', side_effect=response if isinstance(response, Exception) else None,
                                  return_value=response if not isinstance(response, Exception) else None):
                    with self.assertRaises(updater.TransientMergeState): updater.graphql('mutation', {})
        with patch.object(updater, 'api', return_value={'errors': [{'message': 'Resource not accessible'}]}):
            with self.assertRaises(ValidationError) as exc: updater.graphql('mutation', {})
        self.assertNotIsInstance(exc.exception, updater.TransientMergeState)

    def test_app_must_have_single_repository_installation_and_auto_merge(self):
        repo = {'allow_auto_merge': True}
        with patch.object(updater, 'api', side_effect=[{'total_count': 1, 'repositories': [{'full_name': REPO}]}, repo, []]):
            self.assertEqual(updater.app_check(REPO), repo)
        with patch.object(updater, 'api', return_value={'total_count': 2, 'repositories': []}):
            with self.assertRaises(ValidationError): updater.app_check(REPO)

    def test_publication_creates_or_updates_one_pr_and_never_merges(self):
        publication = updater.plan(['dist/ssv/manifest.json'], ['ssv'], True, True)
        for existing in (None, pull()):
            calls = []
            def fake_git(*args, **kwargs):
                calls.append(args)
                if args[:1] == ('rev-parse',):
                    return 'base' if sum(c[:1] == ('rev-parse',) for c in calls) == 1 else 'new'
                if args[:2] == ('diff', '--cached'):
                    return 'dist/ssv/manifest.json\0'
                if 'ls-remote' in args:
                    return 'base refs/heads/main' if args[-1] == 'refs/heads/main' else 'old refs/heads/automation/database-updates'
                return ''
            def fake_api(endpoint, fields=None):
                return [existing] if existing and 'state=open' in endpoint else [] if 'state=open' in endpoint else pull()
            with tempfile.TemporaryDirectory() as tmp, patch.object(updater, 'discover_modules', return_value=['ssv']), \
                 patch.object(updater, 'app_check', return_value={'default_branch': 'main', 'allow_merge_commit': True}), \
                 patch.object(updater, 'git', side_effect=fake_git), patch.object(updater, 'api', side_effect=fake_api) as api, \
                 patch.object(updater, 'description', return_value='Validated update'), \
                 patch.object(updater, 'run', return_value=__import__('json').dumps(pull())) as run, \
                 patch.dict('os.environ', {'GITHUB_OUTPUT': str(Path(tmp) / 'outputs')}), patch.object(updater, 'graphql') as mutation:
                updater.publish(publication, REPO)
                output = (Path(tmp) / 'outputs').read_text(encoding='utf-8')
                self.assertIn('pr=1', output)
                self.assertIn('head=new', output)
                mutation.assert_not_called()
                if existing:
                    self.assertIn('PATCH', run.call_args.args[0])
                    self.assertFalse(any(c.args[0].endswith('/pulls') for c in api.call_args_list))
                else:
                    self.assertEqual(sum(c.args[0].endswith('/pulls') for c in api.call_args_list), 1)
            pushes = [c for c in calls if 'push' in c]
            self.assertEqual(len(pushes), 1)
            self.assertEqual(pushes[0][-1], 'HEAD:refs/heads/' + updater.BRANCH)
            self.assertIn('--force-with-lease=refs/heads/' + updater.BRANCH + ':old', pushes[0])

    def test_advanced_main_prevents_branch_or_pr_writes(self):
        p = updater.plan(['dist/ssv/manifest.json'], ['ssv'], True, True)
        with patch.object(updater, 'discover_modules', return_value=['ssv']), \
             patch.object(updater, 'app_check', return_value={'default_branch': 'main', 'allow_merge_commit': True}), \
             patch.object(updater, 'git', side_effect=['old', 'new refs/heads/main']) as git, patch.object(updater, 'api') as api:
            with self.assertRaises(ValidationError): updater.publish(p, REPO)
        api.assert_not_called()
        self.assertFalse(any('push' in c.args for c in git.call_args_list))

    def test_workflow_retains_read_permissions_scopes_secret_and_serializes_publication(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / '.github/workflows/update-databases.yml').read_text(encoding='utf-8')
        source = (root / 'tools/scheduled_update.py').read_text(encoding='utf-8')
        self.assertIn('cancel-in-progress: false', workflow)
        self.assertIn('group: downloaderplus-database-publish', workflow)
        self.assertIn('persist-credentials: false', workflow)
        self.assertNotIn('  contents: write', workflow)
        self.assertNotIn('git push', workflow)
        self.assertNotIn('matrix:', workflow)
        self.assertEqual(workflow.count('${{ secrets.DOWNLOADERPLUS_APP_PRIVATE_KEY }}'), 2)
        self.assertEqual(workflow.count('private-key:'), 2)
        self.assertNotIn('DOWNLOADERPLUS_APP_PRIVATE_KEY', source)
        self.assertIn('repositories: ${{ github.event.repository.name }}', workflow)
        self.assertIn("'HEAD:refs/heads/' + BRANCH", source)
        self.assertNotIn("'HEAD:refs/heads/main'", source)
        self.assertNotIn('mergePullRequest(', source)
        self.assertIn('wait-validation', workflow)
        self.assertIn('enable-auto-merge', workflow)
        self.assertIn('if: github.ref ==', workflow)
        for check in ['verify_dist.py', 'audit_alternatives.py', 'audit_coinop_coverage.py',
                      'audit_filters.py', 'audit_stg_collection.py', 'check_documentation_encoding.py']:
            self.assertIn(check, updater.CHECKS)


if __name__ == '__main__':
    unittest.main()
