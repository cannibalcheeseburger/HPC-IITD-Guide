import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'fetch_free_nodes.py'


class FetchTests(unittest.TestCase):
    def test_remote_command_loads_shell_environment_and_repo_safely(self):
        self.assertTrue(SCRIPT.exists(), 'Local fetch script must exist')
        spec = importlib.util.spec_from_file_location('fetch_free_nodes', SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.module = module
        command = module.ssh_command('pragya', 'account', None, '~/repo with spaces')
        self.assertIn('BatchMode=yes', command)
        self.assertIn('StrictHostKeyChecking=yes', command)
        self.assertIn('account@pragya.iitd.ac.in', command)
        self.assertIn('bash -ic', command[-1])
        self.assertIn('conda activate pragya', command[-1])
        self.assertIn('check_free_nodes.sh', command[-1])
        self.assertIn('set -e', command[-1])

    def test_padum_uses_requested_login5_host(self):
        self.test_remote_command_loads_shell_environment_and_repo_safely()
        command = self.module.ssh_command('padum', 'account', None, '~/repo')
        self.assertIn('account@login5.hpc.iitd.ac.in', command)

    def test_missing_pbs_path_uses_verified_directory(self):
        import shlex
        import tempfile
        self.test_remote_command_loads_shell_environment_and_repo_safely()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            pbs = repo / 'pbs-bin'
            pbs.mkdir()
            for name in ('pbsnodes', 'qstat'):
                binary = pbs / name
                binary.write_text('#!/bin/sh\nexit 0\n')
                binary.chmod(0o700)
            (repo / 'check_free_nodes.sh').write_text('command -v pbsnodes && command -v qstat\n')
            command = self.module.ssh_command('padum', 'account', None, str(repo))
            script = shlex.split(command[-1])[2].replace('/opt/pbs/2024.1.5/bin', str(pbs))
            proc = subprocess.run(['bash', '-c', 'export PATH=/usr/bin:/bin; conda() { :; }; ' + script],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn(str(pbs / 'pbsnodes'), proc.stdout)
            self.assertIn(str(pbs / 'qstat'), proc.stdout)

    def test_fetch_preserves_failure_output_and_marks_timeout(self):
        self.test_remote_command_loads_shell_environment_and_repo_safely()
        self.assertTrue(hasattr(self.module, 'fetch'), 'Fetch execution must exist')
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 7, 'partial report', 'error')):
            result = self.module.fetch('padum', 'account', None, '~/repo', 10)
        self.assertEqual(result['exit_code'], 7)
        self.assertEqual(result['stdout'], 'partial report')
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired([], 10, output=b'partial')):
            result = self.module.fetch('padum', 'account', None, '~/repo', 10)
        self.assertEqual(result['exit_code'], 124)
        self.assertIn('partial', result['stdout'])
        self.assertIn('timed out', result['stderr'])

    def test_cli_returns_both_reports_and_nonzero_for_partial_failure(self):
        import io
        import json
        from contextlib import redirect_stdout
        self.test_remote_command_loads_shell_environment_and_repo_safely()
        self.assertTrue(hasattr(self.module, 'main'), 'CLI entry point must exist')
        def fake_fetch(cluster, *args):
            return {'cluster': cluster, 'exit_code': 0 if cluster == 'pragya' else 1,
                    'stdout': 'report', 'stderr': '', 'fetched_at': 'test fixture'}
        output = io.StringIO()
        with patch.object(self.module, 'fetch', side_effect=fake_fetch), redirect_stdout(output):
            code = self.module.main(['--user', 'account', '--json'])
        self.assertEqual(code, 1)
        self.assertEqual([r['cluster'] for r in json.loads(output.getvalue())], ['pragya', 'padum'])


if __name__ == '__main__':
    unittest.main()
