"""Public GitHub event-to-workflow contract for prelaunch CI."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / '.github' / 'workflows'
HEAVY = next(name for name in ('test.yml', 'quality.yml', 'db-tests.yml') if (WORKFLOWS / name).exists())
SECURITY = [name for name in ('gitleaks.yml', 'trufflehog.yml', 'secret-scan.yml') if (WORKFLOWS / name).exists()]
EXPECTED_JOBS = {'quality'}
MERGE_QUEUE = False
BASELINE = None


def block(source, key):
    """Read one top-level YAML mapping block; triggers are intentionally simple."""
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines) if line == key + ':') + 1
    end = next((i for i in range(start, len(lines)) if lines[i] and not lines[i][0].isspace() and not lines[i].startswith('#')), len(lines))
    return lines[start:end]


def workflow(name):
    return (WORKFLOWS / name).read_text()


def event_lines(source, event):
    lines = block(source, 'on')
    start = next((i for i, line in enumerate(lines) if line == '  ' + event + ':'), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if re.match(r'^  [a-z_]+:', lines[i])), len(lines))
    return lines[start + 1:end]


def selected(source, event, *, action=None, branch='main'):
    lines = event_lines(source, event)
    if lines is None:
        return False
    spec = '\n'.join(lines)
    if event == 'schedule':
        return branch == 'main' and bool(re.search(r'^    - cron:', spec, re.M))
    if event == 'pull_request':
        types = re.search(r'^    types: \[([^]]+)\]', spec, re.M)
        return action in [item.strip() for item in types.group(1).split(',')] if types else action in ('opened', 'synchronize', 'reopened')
    if event == 'push':
        return bool(re.search(r'^    branches: \[main\]$', spec, re.M)) and branch == 'main'
    return True


def jobs(source):
    return set(re.findall(r'^  ([\w-]+):\s*$', '\n'.join(block(source, 'jobs')), re.M))


class WorkflowEventContract(unittest.TestCase):
    def test_full_suite_runs_for_candidate_and_operator_events(self):
        source = workflow(HEAVY)
        self.assertTrue(selected(source, 'pull_request', action='ready_for_review'))
        self.assertTrue(selected(source, 'workflow_dispatch'))
        self.assertTrue(selected(source, 'schedule', branch='main'))
        schedule = event_lines(source, 'schedule')
        crons = re.findall(r'^    - cron: ["\']?(\d+ \d+ \* \* \*)', '\n'.join(schedule), re.M)
        self.assertEqual(len(crons), 1)

    def test_draft_and_incremental_events_do_not_launch_full_suite(self):
        source = workflow(HEAVY)
        for action in ('opened', 'reopened', 'synchronize', 'converted_to_draft'):
            with self.subTest(action=action):
                self.assertFalse(selected(source, 'pull_request', action=action))
        self.assertFalse(selected(source, 'push', branch='main'))
        self.assertFalse(selected(source, 'push', branch='feature'))
        self.assertFalse(selected(source, 'schedule', branch='feature'))

    def test_secret_scans_cover_every_pr_and_main_push_only(self):
        if not SECURITY:
            self.skipTest('No secret-scan workflow exists in this repository')
        for name in SECURITY:
            with self.subTest(name=name):
                source = workflow(name)
                for action in ('opened', 'synchronize', 'reopened'):
                    self.assertTrue(selected(source, 'pull_request', action=action))
                self.assertTrue(selected(source, 'push', branch='main'))
                self.assertFalse(selected(source, 'push', branch='feature'))

    def test_baseline_runs_with_candidate_cadence_when_present(self):
        if BASELINE is None:
            self.skipTest('No separate baseline workflow in this repository')
        source = workflow(BASELINE)
        self.assertTrue(selected(source, 'pull_request', action='ready_for_review'))
        self.assertTrue(selected(source, 'workflow_dispatch'))
        self.assertTrue(selected(source, 'schedule', branch='main'))
        self.assertFalse(selected(source, 'pull_request', action='synchronize'))
        self.assertFalse(selected(source, 'push', branch='main'))
        self.assertIn('baseline', jobs(source))

    def test_existing_job_names_remain(self):
        source = workflow(HEAVY)
        self.assertTrue(EXPECTED_JOBS.issubset(jobs(source)))
        if MERGE_QUEUE:
            self.assertTrue(selected(source, 'merge_group'))
            for name in SECURITY:
                self.assertTrue(selected(workflow(name), 'merge_group'))
        if 'secret-scan.yml' in SECURITY:
            self.assertIn('scan', jobs(workflow('secret-scan.yml')))


if __name__ == '__main__':
    unittest.main()
