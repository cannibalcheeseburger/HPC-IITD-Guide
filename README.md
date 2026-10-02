# IIT Delhi HPC Guide

A short, practical reference for getting around IIT Delhi's HPC clusters and their quirks, written from
things actually tried, with sources and dates. It also ships a small tool that shows which GPUs are free
on Pragya right now.

> **Status (2026-10-02):** this guide currently covers **Pragya** in depth, from direct testing. A
> **Padum** section (the older `hpc.iitd.ac.in` cluster) is in progress — raw research is in
> [docs/sources/padum-research-notes.md](docs/sources/padum-research-notes.md), unverified until someone
> with Padum access checks it. See [AGENTS.md](AGENTS.md) for the current handoff state and restructure plan.

## Pragya

> **How to read the marks:** ✅ = tested on the cluster (date given where it matters).
> ⚠️ = taken from documentation or inferred, not tested. Open questions are listed in
> [docs/08-open-questions.md](docs/08-open-questions.md).

## Quick start

```bash
# 1. one-time: make sure conda/modules load when you log in over SSH  (docs/02)
cp /etc/skel/.bash_profile ~/.bash_profile      # only if you have no ~/.bash_profile

# 2. see what is free right now
bash check_free_nodes.sh

# 3. get a GPU for a short interactive session (every job needs >= 1 GPU)
qsub -I -q debug -P <project_code> -l select=1:ncpus=1:ngpus=1 -l walltime=00:30:00

# 4. or submit a batch job
qsub examples/batch_job.pbs

# 5. watch your jobs
qstat -u $USER
```

Internet only works through the campus proxy, and it is slow per connection. See
[docs/04](docs/04-internet-and-proxy.md) for the proxy settings and how to download ~15x faster.

## Contents

| # | Page | What it covers |
|---|---|---|
| 1 | [Cluster overview](docs/01-cluster-overview.md) | Nodes, GPUs, queues, storage, installed software, the rules |
| 2 | [Getting started](docs/02-getting-started.md) | Login, shell setup, conda, modules, tmux |
| 3 | [Running jobs](docs/03-running-jobs.md) | Interactive and batch jobs, monitoring, why a job is waiting |
| 4 | [Internet and proxy](docs/04-internet-and-proxy.md) | Proxy setup, measured speeds, research proxy, fast downloads |
| 5 | [Python environments](docs/05-python-environments.md) | conda, pip, installing big packages (PyTorch) quickly |
| 6 | [Checking availability](docs/06-checking-availability.md) | The `check_free_nodes.sh` tool and how to read it |
| 7 | [Troubleshooting](docs/07-troubleshooting.md) | Error message -> cause -> fix |
| 8 | [Open questions](docs/08-open-questions.md) | Things not yet confirmed |

`examples/batch_job.pbs` is a batch-job template.

## Rules of thumb

- **Every job must request at least one GPU** (`ngpus=1`). There are no CPU-only nodes or queues.
- **Always set a walltime** (`-l walltime=HH:MM:SS`). The `debug` queue rejects anything over 30 minutes.
- **Free GPUs do not guarantee a job can start.** Queue quotas also apply; see
  [quota troubleshooting](docs/07-troubleshooting.md#free-nodes-but-job-blocked-by-quota).
- **Don't run heavy work on the login node.** Use a job.
- **Never put your password in a script that other people can read** (see [docs/04](docs/04-internet-and-proxy.md#credentials)).
