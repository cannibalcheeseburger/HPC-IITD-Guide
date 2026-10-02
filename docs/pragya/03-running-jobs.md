# 3. Running jobs

PBS Pro decides where and when jobs run. You describe what you need; it waits for free resources.

## The one rule: request a GPU ✅

Every job needs `ngpus=1` or more. This is enforced for all queues.

```
qsub: Please request at least one GPU using "ngpus=<value>"
```

## Interactive job (a shell on a compute node) ✅

```bash
qsub -I -q debug -P <project_code> -l select=1:ncpus=1:ngpus=1 -l walltime=00:30:00
```

- `-q debug` = short-test queue, max 30 min. For longer work drop it (goes to `standard`, up to 96 h).
- Without `-l walltime=...` the job requests 48 h and `debug` refuses it.
- The command waits in your terminal until a GPU is free. Ctrl-C cancels it.
- Interactive jobs need your terminal alive. For anything long, use a batch job.

## Batch job ✅ (submission tested)

See [`examples/pragya/batch_job.pbs`](../../examples/pragya/batch_job.pbs).

```bash
qsub examples/pragya/batch_job.pbs # prints a job id like 70119.pragya
```

Useful `#PBS` lines:

```bash
#PBS -N name                          # job name
#PBS -P <project_code>                # project code
#PBS -q standard                      # queue
#PBS -l select=1:ncpus=8:ngpus=1      # what you need
#PBS -l walltime=12:00:00             # maximum run time
#PBS -o /path/out.txt                 # stdout file
#PBS -e /path/err.txt                 # stderr file
```

Multi-node job example (seen on this cluster): `-l select=2:ncpus=40:ngpus=1` gives two chunks of 40 cores
and 1 GPU each, possibly on different nodes.

Job arrays: the server allows up to 10000 entries ✅; each sub-job shows as `1234[5].pragya` and only appears in
`qstat` with `-t` ✅. Submitting one with `-J 1-10` is standard PBS Pro syntax ⚠️ (not tried here).

## Watching and stopping jobs ✅

```bash
qstat -u $USER              # your jobs; S column: Q queued, R running, H held
qstat -f <jobid>            # everything, incl. the `comment` field (why it is waiting)
qstat -f -t -F json         # all jobs as JSON (what the availability tool uses)
qdel <jobid>                # cancel a job
qstat -Q                    # queues and their counts
```

## Why is my job still `Q`?  ✅

Read the reason: `qstat -f <jobid>` (inspect the full `comment`, which may wrap across lines).

| Comment | Meaning |
|---|---|
| `Not Running: Insufficient amount of resource: ngpus (R: 1 A: 0 ...)` | You asked for 1 GPU, 0 are free. Wait, or check `bash check_free_nodes.sh` to see when the next jobs end. |
| other `Insufficient ... ncpus` | Not enough free cores on any node |
| `Not Running: would exceed overall limit on resource std_high_gpu_quota in complex` | Shared standard/high quota is exhausted; free nodes alone cannot help. See [quota troubleshooting](07-troubleshooting.md#free-nodes-but-job-blocked-by-quota). |

Shorter walltimes and smaller requests can be easier to fit, but do not bypass a full quota.
The availability tool's "Jobs Ending Soonest" table estimates resource release, not your job's start time.

## Defaults on this server ✅

- `default_qsub_arguments = -koed -v TERM=xterm`: output/error files are kept, and `TERM` is set.
- Default queue: `standard`.
- Default walltime: the server config says 1 min, but jobs without one were seen with 48 h, so always set it.
- Working directory: PBS jobs normally start in your home directory, and `$PBS_O_WORKDIR` holds the directory you submitted
  from, so scripts usually `cd "$PBS_O_WORKDIR"` first ⚠️ (standard PBS behaviour; not checked here).
