# 6. Checking availability

Before waiting on a job, look at what is actually free.

```bash
conda activate <env with pandas>      # any env with python3 + pandas
bash check_free_nodes.sh
```

It takes about a second and needs only `python3`, `pandas`, and the PBS tools (`pbsnodes`, `qstat`) on a login node.
Source: [`util_pbs.py`](../util_pbs.py).

## What it prints

1. **Job counts:** running / queued / held.
2. **Available free resources**, per node type (`amilan_gpu`, `infer_gpu`): nodes in the `free` state with free cores,
   as `CPU free/total` and `GPU free/total`.
3. **Unavailable nodes:** offline/down nodes with PBS's reason.
4. **Possibly stale assignments:** nodes where PBS counts more assigned CPUs/GPUs than running jobs account for.
5. **Per node type:**
   - the 10 running jobs that end soonest (`Job ID, Node, Owner, Start, Walltime, End, Ends In, CPUs, GPUs`),
     with one row per node for multi-node jobs;
   - GPU usage per user.

## How to read it

- **Free GPUs** in section 2 are unassigned node resources, not a promise that your job can start.
  Queue/server quotas, access rules, reservations, and priority can still block it. See
  [queue resource quotas](01-cluster-overview.md#queue-resource-quotas--2026-09-30).
  A request such as `select=1:ncpus=128:ngpus=8` needs all those resources together on one node;
  free resources summed across nodes are insufficient.
- **`Ends In`** in the job table is `start + requested walltime`. Jobs usually finish earlier, so it is an upper bound
  for the requested run duration, not a predicted start time for your job. A finishing job in another
  quota group may not release quota for your queue, and other queued jobs may start first.
- **Stale assignments** (section 4) are capacity PBS thinks is busy but no job owns (seen after failed job cleanups).
  You can't use it; if it grows, tell the admins.
- **Unavailable nodes** don't count as free even if idle.

## Options

```bash
python util_pbs.py --nodes-json nodes.json --jobs-json jobs.json
```

Use saved output of `pbsnodes -F json -a` and `qstat -f -t -F json` instead of querying live. Handy for testing.

## Adding a new node type

Node type = hostname with trailing digits removed (`amilan017` -> `amilan`). New hardware shows up
automatically under its own prefix. To give it a friendlier name, add it to `NODE_TYPE_MAPPING` at the top of `util_pbs.py`.
