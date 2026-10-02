# Pragya

Pragya pages are based on direct observations; dated measurements and changing resource details are marked accordingly.

## Quick start

```bash
bash check_free_nodes.sh
qsub -I -q debug -P <project_code> -l select=1:ncpus=1:ngpus=1 -l walltime=00:30:00
qsub examples/pragya/batch_job.pbs
qstat -u $USER
```

Every job needs at least one GPU and an explicit walltime. See [running jobs](03-running-jobs.md) before submitting.

## Pages

1. [Cluster overview](01-cluster-overview.md)
2. [Getting started](02-getting-started.md)
3. [Running jobs](03-running-jobs.md)
4. [Internet and proxy](04-internet-and-proxy.md)
5. [Python environments](05-python-environments.md)
6. [Checking availability](06-checking-availability.md)
7. [Troubleshooting](07-troubleshooting.md)
8. [Open questions](08-open-questions.md)
