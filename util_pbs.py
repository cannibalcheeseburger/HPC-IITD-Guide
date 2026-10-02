import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime

import pandas as pd

# --- CONFIGURATION ---
# Node type is derived from the short hostname with trailing digits stripped
# (amilan017 -> 'amilan'). Add an entry here only to give a prefix a friendlier
# name; unlisted prefixes still get their own report under the bare prefix.
PRAGYA_NODE_TYPE_MAPPING = {
    'amilan': 'amilan_gpu',   # 128 CPU cores, 8 GPUs (NVLink)
    'infer': 'infer_gpu',     # 48 CPU cores, 2 GPUs (PCIe)
}

# Imported from the user's Padum HPC-availibility project (2026-10-02).
PADUM_NODE_TYPE_MAPPING = {
    'scai': 'amd_epyc_gpu',
    'aice': 'icelake_a100_gpu',
    'vsky': 'skylake_v100_gpu',
    'khas': 'haswell_k40_gpu',
    'cice': 'icelake_cpu',
    'csky': 'skylake_cpu',
    'chas': 'haswell_cpu',
    'cgen': 'amd_genoa_cpu',
    'amd001': 'amd_large_mem_cpu',
}
NODE_TYPE_MAPPING = PRAGYA_NODE_TYPE_MAPPING

# Node states that mean "cannot run anything new / not worth waiting on".
UNAVAILABLE_STATES = ('down', 'offline', 'unknown', 'unresolvable')
# Job states that hold resources on nodes (exec_vnode is set).
ACTIVE_JOB_STATES = ('R', 'E', 'S', 'U')

PBS_TIME_FORMAT = '%a %b %d %H:%M:%S %Y'   # e.g. "Sat Sep 19 03:30:49 2026"
TOP_N_JOBS = 10


def run_json(cmd):
    """Runs a PBS command that emits JSON on stdout and returns the parsed dict."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit(f"Error: '{cmd[0]}' not found. Run this on a PBS login node.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error: {' '.join(cmd)} failed: {e.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit(f"Error: could not decode JSON from {' '.join(cmd)}.")


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"Error: could not read {path}: {e}")


def short_host(name):
    return name.split('.')[0]


def node_type_of(node_name, detail, mapping=None):
    host = short_host(detail.get('Mom') or node_name)
    prefix = re.sub(r'\d+$', '', host)
    mapping = NODE_TYPE_MAPPING if mapping is None else mapping
    return mapping.get(host, mapping.get(prefix, prefix))


def detect_cluster(nodes):
    """Infer labels from PBS node names, including offline captures."""
    matches = set()
    for name, detail in nodes.items():
        host = short_host(detail.get('Mom') or name)
        prefix = re.sub(r'\d+$', '', host)
        for cluster, mapping in (('pragya', PRAGYA_NODE_TYPE_MAPPING),
                                 ('padum', PADUM_NODE_TYPE_MAPPING)):
            if host in mapping or prefix in mapping:
                matches.add(cluster)
    if len(matches) > 1:
        raise ValueError('nodes match both clusters; set --cluster pragya or --cluster padum')
    return next(iter(matches), 'generic')


def select_cluster(requested, environment, nodes):
    """CLI overrides HPC_CLUSTER; auto detects from the supplied node data."""
    selection = requested if requested is not None else environment or 'auto'
    if selection not in ('auto', 'pragya', 'padum'):
        raise ValueError('HPC_CLUSTER must be auto, pragya, or padum')
    return detect_cluster(nodes) if selection == 'auto' else selection


def is_unavailable(detail):
    state = detail.get('state', '')
    return any(s in state for s in UNAVAILABLE_STATES)


def parse_exec_vnode(exec_vnode):
    """
    Splits '(amilan009:ncpus=40:ngpus=1)+(amilan023:ncpus=40:ngpus=1)' into
    {'amilan009': {'ncpus': 40, 'ngpus': 1}, 'amilan023': {...}}.
    Resources are summed if a node appears in more than one chunk.
    """
    alloc = defaultdict(lambda: {'ncpus': 0, 'ngpus': 0})
    for part in exec_vnode.replace('(', '').replace(')', '').split('+'):
        name, *resources = part.split(':')
        for res in resources:
            key, _, value = res.partition('=')
            if key in ('ncpus', 'ngpus'):
                alloc[name][key] += int(value)
        alloc[name]  # a vnode with no ncpus/ngpus is still recorded
    return alloc


def parse_walltime(value):
    """'48:00:00' (or plain seconds) -> timedelta-compatible seconds, else None."""
    try:
        if ':' in str(value):
            parts = [int(p) for p in str(value).split(':')]
            while len(parts) < 3:
                parts.insert(0, 0)
            h, m, s = parts[-3:]
            return h * 3600 + m * 60 + s
        return int(value)
    except (TypeError, ValueError):
        return None


def build_allocations(jobs_data, nodes):
    """
    One row per (job, node) for every active job, using the per-node share from
    exec_vnode rather than the job-wide Resource_List (which would over-count
    multi-node jobs).
    """
    rows = []
    for job_id, job in jobs_data.get('Jobs', {}).items():
        if job.get('job_state') not in ACTIVE_JOB_STATES or 'exec_vnode' not in job:
            continue

        start = None
        try:
            start = datetime.strptime(job['stime'], PBS_TIME_FORMAT)
        except (KeyError, ValueError):
            pass
        walltime_s = parse_walltime(job.get('Resource_List', {}).get('walltime'))
        end = start + pd.Timedelta(seconds=walltime_s) if start and walltime_s is not None else pd.NaT

        for node, res in parse_exec_vnode(job['exec_vnode']).items():
            if node not in nodes:
                continue
            rows.append({
                'Job ID': job_id,
                'Node': node,
                'Owner': job.get('Job_Owner', 'N/A').split('@')[0],
                'Queue': job.get('queue', 'N/A'),
                'Start': start or pd.NaT,
                'Walltime': job.get('Resource_List', {}).get('walltime', 'N/A'),
                'End': end,
                'CPUs': res['ncpus'],
                'GPUs': res['ngpus'],
            })
    return pd.DataFrame(rows)


def free_resources(detail):
    avail = detail.get('resources_available', {})
    used = detail.get('resources_assigned', {})
    total_cpu, total_gpu = int(avail.get('ncpus', 0)), int(avail.get('ngpus', 0))
    free_cpu = total_cpu - int(used.get('ncpus', 0))
    free_gpu = total_gpu - int(used.get('ngpus', 0))
    return free_cpu, total_cpu, free_gpu, total_gpu


def print_job_counts(jobs_data):
    counts = defaultdict(int)
    for job in jobs_data.get('Jobs', {}).values():
        counts[job.get('job_state')] += 1
    print(f"Jobs: {counts['R']} running, {counts['Q']} queued, {counts['H']} held")
    print()


def print_available_resources(nodes, types):
    """Prints free CPUs/GPUs for nodes in the 'free' state, grouped by node type."""
    print('--- AVAILABLE FREE RESOURCES ---')
    by_type = defaultdict(list)
    for name, detail in nodes.items():
        by_type[types[name]].append(name)

    found_free = False
    for node_type, names in sorted(by_type.items()):
        lines = []
        tot_cpu = tot_gpu = 0
        for name in sorted(names):
            detail = nodes[name]
            if detail.get('state') != 'free':
                continue
            free_cpu, total_cpu, free_gpu, total_gpu = free_resources(detail)
            if free_cpu <= 0:
                continue
            tot_cpu += free_cpu
            tot_gpu += free_gpu
            gpu = f"   GPU {free_gpu}/{total_gpu}" if total_gpu else ''
            lines.append(f"  {name:<12} CPU {free_cpu}/{total_cpu}{gpu}")
        if lines:
            found_free = True
            print(f"[{node_type}] {len(lines)} nodes with free cores "
                  f"({tot_cpu} CPUs, {tot_gpu} GPUs free in total)")
            print('\n'.join(lines))
            print()
    if not found_free:
        print("No nodes are currently in a 'free' state with available resources.")
        print()

    unavailable = [(n, d) for n, d in sorted(nodes.items()) if is_unavailable(d)]
    if unavailable:
        print(f"Unavailable nodes ({len(unavailable)}):")
        for name, detail in unavailable:
            comment = detail.get('comment', '')
            print(f"  {name:<12} {detail.get('state')}" + (f" -- {comment}" if comment else ''))
    print('-' * 40)
    print()


def print_unbacked_assignments(nodes, allocations):
    """
    Flags available nodes where PBS counts more assigned CPUs/GPUs than the running
    jobs account for (leaked accounting, e.g. after a failed job cleanup). Those
    resources look busy to the scheduler but belong to no job.
    """
    if allocations.empty:
        used = pd.DataFrame(columns=['CPUs', 'GPUs'])
    else:
        used = allocations.groupby('Node')[['CPUs', 'GPUs']].sum()
    lines = []
    for name, detail in sorted(nodes.items()):
        if is_unavailable(detail):
            continue
        assigned = detail.get('resources_assigned', {})
        job_cpu, job_gpu = used.loc[name].tolist() if name in used.index else (0, 0)
        extra_cpu = int(assigned.get('ncpus', 0)) - job_cpu
        extra_gpu = int(assigned.get('ngpus', 0)) - job_gpu
        if extra_cpu > 0 or extra_gpu > 0:
            lines.append(f"  {name:<12} +{max(extra_cpu, 0)} CPUs, +{max(extra_gpu, 0)} GPUs")
    if lines:
        print('Nodes with PBS-assigned resources not backed by any running job (possibly stale):')
        print('\n'.join(lines))
        print('-' * 40)
        print()


def format_delta(delta):
    if pd.isna(delta):
        return 'N/A'
    secs = int(delta.total_seconds())
    if secs <= 0:
        return 'overdue'
    h, m = divmod(secs // 60, 60)
    d, h = divmod(h, 24)
    return f"{d}d {h}h {m}m" if d else f"{h}h {m}m"


def report_node_type(node_type, node_names, nodes, allocations, now):
    """Prints the soonest-ending jobs and per-user GPU usage for one node type."""
    up = [n for n in node_names if not is_unavailable(nodes[n])]
    print(f'--- REPORT FOR {node_type.upper()} NODES ({len(up)}/{len(node_names)} up) ---')

    df = allocations[allocations['Node'].isin(up)] if not allocations.empty else allocations
    if df.empty:
        print('No running jobs found on this node type.')
        print('-' * 40)
        print()
        return

    df = df.sort_values('End', na_position='last').reset_index(drop=True)
    shown = df.head(TOP_N_JOBS).copy()
    shown['Ends In'] = (shown['End'] - now).map(format_delta)
    shown['Start'] = shown['Start'].dt.strftime('%m-%d %H:%M')
    shown['End'] = shown['End'].dt.strftime('%m-%d %H:%M')
    print('Jobs Ending Soonest:')
    print(shown[['Job ID', 'Node', 'Owner', 'Start', 'Walltime', 'End', 'Ends In', 'CPUs', 'GPUs']]
          .to_string())
    print()

    gpus_by_user = df[df['GPUs'] > 0].groupby('Owner')['GPUs'].sum()
    print('GPU Usage Summary:')
    if gpus_by_user.empty:
        print('- No users are currently using GPUs on these nodes.')
    else:
        for user, gpus in gpus_by_user.sort_values(ascending=False).items():
            print(f'- {user}: {gpus} GPUs')
    print('-' * 40)
    print()


def main():
    parser = argparse.ArgumentParser(description='Report free resources and job end times on the PBS cluster.')
    parser.add_argument('--cluster', choices=('auto', 'pragya', 'padum'),
                        help='node labels: CLI overrides HPC_CLUSTER; default: auto-detect from PBS nodes')
    parser.add_argument('--nodes-json', help="saved 'pbsnodes -F json -a' output (default: run pbsnodes)")
    parser.add_argument('--jobs-json', help="saved 'qstat -f -t -F json' output (default: run qstat)")
    args = parser.parse_args()

    node_data = load_json(args.nodes_json) if args.nodes_json else run_json(['pbsnodes', '-F', 'json', '-a'])
    jobs_data = load_json(args.jobs_json) if args.jobs_json else run_json(['qstat', '-f', '-t', '-F', 'json'])

    nodes = node_data.get('nodes', {})
    if not nodes:
        sys.exit('Error: no nodes found in pbsnodes output.')
    try:
        cluster = select_cluster(args.cluster, os.environ.get('HPC_CLUSTER'), nodes)
    except ValueError as error:
        parser.error(str(error))
    mapping = {'padum': PADUM_NODE_TYPE_MAPPING, 'pragya': PRAGYA_NODE_TYPE_MAPPING}.get(cluster, {})
    if cluster == 'generic':
        print('Cluster not recognized; reporting generic node prefixes. '
              'Set HPC_CLUSTER or --cluster to select known labels.', file=sys.stderr)
    types = {name: node_type_of(name, detail, mapping) for name, detail in nodes.items()}
    now = datetime.fromtimestamp(jobs_data.get('timestamp', datetime.now().timestamp()))

    print_job_counts(jobs_data)
    print_available_resources(nodes, types)

    allocations = build_allocations(jobs_data, nodes)
    print_unbacked_assignments(nodes, allocations)
    names_by_type = defaultdict(list)
    for name, node_type in types.items():
        names_by_type[node_type].append(name)
    for node_type, names in sorted(names_by_type.items()):
        report_node_type(node_type, sorted(names), nodes, allocations, now)


if __name__ == '__main__':
    main()
