# 7. Troubleshooting

Find your message, apply the fix. ✅ = reproduced on the cluster.

## Submitting jobs

| Message / symptom | Cause | Fix |
|---|---|---|
| `qsub: Please request at least one GPU using "ngpus=<value>"` ✅ | Every job must ask for a GPU, in every queue | Add `ngpus=1`: `-l select=1:ncpus=1:ngpus=1` |
| `qsub: Job violates queue and/or server resource limits` (to `debug`) ✅ | No walltime given, so it defaults to 48 h; `debug` allows 30 min | Add `-l walltime=00:30:00` (or less) |
| `qstat: Unknown queue scai_q` ✅ | That queue doesn't exist on this cluster | Use `standard`, `debug` (or omit `-q`) |
| Job stays `Q`, `comment = Insufficient amount of resource: ngpus (R: 1 A: 0 ...)` ✅ | No free GPU right now | Run `bash check_free_nodes.sh`; wait, or ask for less/shorter. See [docs/03](03-running-jobs.md) |
| `qsub -I` hangs with no prompt | Waiting in the queue (interactive jobs wait in your terminal) | Ctrl-C to cancel; use a batch job if it will wait long |

## Free nodes but job blocked by quota

✅ Reproduced on 2026-09-30 for a one-node, 128-CPU, 8-GPU, 48-hour interactive request:

```text
Not Running: would exceed overall limit on resource std_high_gpu_quota in complex
```

Cause: the shared standard/high GPU cap was full even though the availability report showed
fully free nodes. See [the dated limits and usage snapshot](01-cluster-overview.md#queue-resource-quotas--2026-09-30).

What to do:

1. Read `qstat -f <jobid>` and leave an existing queued job waiting if the request is still needed.
   Switching to `high` or reducing walltime alone does not remove this quota blocker.
2. Request fewer GPUs only if the workload supports it. This can fit smaller amounts of newly freed quota,
   but cannot start while the shared GPU cap is completely full.
3. Ask your PI/HPC support whether `<project_code>` is eligible for an `ext*` queue.
   Visible quota headroom or absence of a queue access list does not prove project eligibility.
4. If `qstat` says the job has finished, inspect `qstat -xf <jobid>`. The observed interactive job
   later showed `job_state = F` and a quota comment ending in `and terminated`, without running;
   the output did not establish why it was terminated. A terminated job is no longer waiting and
   needs a new submission if still wanted. Keep an interactive submission's terminal alive, or use a batch job.

There is no reliable start-time estimate from free-node counts alone: quota, node fit, and scheduling
priority must all allow the job to run.

## Shell and environment

| Symptom | Cause | Fix |
|---|---|---|
| `conda: command not found` after SSH login ✅ | No `~/.bash_profile`, so login shells don't read `~/.bashrc` | `cp /etc/skel/.bash_profile ~/.bash_profile && source ~/.bashrc` |
| `pip` is version 21.x / Python 3.9 ✅ | You're using the system pip, not your env's | `conda activate <env>` first; `pip install -U pip` |
| `pip install --report` says unknown option | pip older than 22.2 | Upgrade pip inside the env |
| `torch.cuda.is_available()` is `False` | On a login node: expected (no GPU). On a GPU node: driver/CUDA build mismatch | Test inside a GPU job; see "PyTorch and CUDA" in [docs/05](05-python-environments.md) |
| `bash export_proxy.sh` did nothing | A script run with `bash` can't change your shell | `source export_proxy.sh` |
| `man`/`less` seems stuck | Pager waiting for input | Press `q` |

## Internet

| Symptom | Cause | Fix |
|---|---|---|
| `curl`/`pip`/`git` time out ✅ | No direct internet | Set `http_proxy`/`https_proxy` ([docs/04](04-internet-and-proxy.md)) |
| Downloads are ~0.4 MB/s ✅ | Per-connection throttle | Use `aria2c -x 8 -s 8`; see [docs/04](04-internet-and-proxy.md) |
| `proxy.sh` prints `Already logged in` ⚠️ | Older helpers exit; the locally reviewed revision keeps retrying | Check which copy you run and test connectivity separately; see [retry behavior and verification scope](04-internet-and-proxy.md#proxy-login-) |
| Proxy stops working | Login session expired and nobody is refreshing it | Run the proxy login script in `tmux` |
| `curl: (28) timeout` on direct mirrors | Only `mirrors.iitd.ac.in` (Ubuntu/Debian) works without the proxy | Use the proxy for everything else |

## Nodes

| Symptom | Cause | Fix |
|---|---|---|
| Node `offline`, comment "Unable to clean up one or more cgroups" ✅ | A previous job left cgroup state behind | Only admins can clear it; report the node name |
| Node `offline`, "Marked Offline by ... fs_check hook" ✅ | A health check failed (e.g. a missing user's directory) | Admins; report it |
| Node shows CPUs/GPUs assigned but no jobs ✅ | Stale PBS accounting | Not usable; tell admins (the availability tool flags these) |
