#!/usr/bin/env python3
"""Fetch the existing PBS availability reports over key-authenticated SSH."""
import shlex
import subprocess
from datetime import datetime, timezone


def fetch(cluster, user, identity, repo, timeout):
    result = {'cluster': cluster, 'fetched_at': datetime.now(timezone.utc).isoformat()}
    try:
        proc = subprocess.run(ssh_command(cluster, user, identity, repo),
                              capture_output=True, text=True, timeout=timeout)
        result.update(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    except subprocess.TimeoutExpired as exc:
        output = exc.output or ''
        if isinstance(output, bytes):
            output = output.decode(errors='replace')
        result.update(exit_code=124, stdout=output,
                      stderr=f'SSH command timed out after {timeout}s')
    except OSError as exc:
        result.update(exit_code=127, stdout='', stderr=str(exc))
    return result


CLUSTERS = {
    'pragya': ('pragya.iitd.ac.in', 'pragya'),
    'padum': ('login5.hpc.iitd.ac.in', 'hpc'),
}


def ssh_command(cluster, user, identity, repo):
    host, environment = CLUSTERS[cluster]
    if repo == '~':
        remote_path = '"$HOME"'
    elif repo.startswith('~/'):
        remote_path = '"$HOME"/' + shlex.quote(repo[2:])
    else:
        remote_path = shlex.quote(repo)
    pbs_bin = '/opt/pbs/2024.1.5/bin' if cluster == 'padum' else '/opt/pbs/2026.0.0/bin'
    script = (
        f'set -e; conda activate {shlex.quote(environment)}; '
        f'cd {remote_path}; '
        'printf "HOST=%s ENV=%s REPO=%s\\n" "$(hostname -f)" "$CONDA_DEFAULT_ENV" "$PWD"; '
        'if ! command -v pbsnodes >/dev/null || ! command -v qstat >/dev/null; then '
        f'if test -x {pbs_bin}/pbsnodes && test -x {pbs_bin}/qstat; then '
        f'export PATH={shlex.quote(pbs_bin)}:"$PATH"; '
        f'printf "PBS PATH fallback: %s\\n" {shlex.quote(pbs_bin)} >&2; '
        'else printf "PBS tools missing on %s after Conda activation\\n" "$(hostname -f)" >&2; exit 127; fi; fi; '
        'bash check_free_nodes.sh'
    )
    command = ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
               '-o', 'ConnectTimeout=15', '-o', 'ConnectionAttempts=1',
               '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=2']
    if identity:
        command += ['-o', 'IdentitiesOnly=yes', '-i', identity]
    return command + [f'{user}@{host}', 'bash -ic ' + shlex.quote(script)]


def main(argv=None):
    import argparse
    from concurrent.futures import ThreadPoolExecutor
    import json
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', default=os.environ.get('HPC_SSH_USER'),
                        help='Remote account on both clusters (or set HPC_SSH_USER)')
    parser.add_argument('--identity', help='SSH private key path; otherwise use normal SSH defaults')
    parser.add_argument('--cluster', choices=['both', *CLUSTERS], default='both')
    parser.add_argument('--repo', default='~/HPC-IITD-Guide', help='Repository path on both servers')
    parser.add_argument('--timeout', type=float, default=120, help='Per-server timeout in seconds (default 120)')
    parser.add_argument('--json', action='store_true', help='Emit JSON with raw stdout, stderr and exit codes')
    args = parser.parse_args(argv)
    if not args.user or args.user.startswith('-') or any(c.isspace() for c in args.user) or '@' in args.user:
        parser.error('Provide a valid remote account via --user or HPC_SSH_USER')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    clusters = list(CLUSTERS) if args.cluster == 'both' else [args.cluster]
    identity = os.path.expanduser(args.identity) if args.identity else None
    with ThreadPoolExecutor(max_workers=len(clusters)) as pool:
        futures = [pool.submit(fetch, c, args.user, identity, args.repo, args.timeout) for c in clusters]
        results = [future.result() for future in futures]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            state = 'OK' if result['exit_code'] == 0 else f"FAILED (exit {result['exit_code']})"
            print(f"\n=== {result['cluster'].upper()} | {state} | request started {result['fetched_at']} ===")
            print(result['stdout'], end='' if result['stdout'].endswith('\n') else '\n')
            if result['stderr']:
                print('--- SSH / shell diagnostics ---')
                print(result['stderr'].rstrip())
        print('\nFree resources are snapshots, not scheduling guarantees. Check queue quotas, eligibility, GPU memory and drivers before submitting.')
    return int(any(r['exit_code'] != 0 for r in results))


if __name__ == '__main__':
    raise SystemExit(main())

