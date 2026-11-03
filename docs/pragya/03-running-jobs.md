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
- Without explicit walltime, historical requests were seen with 48 h; the standard queue default was 1 h on 2026-10-11. Always request walltime explicitly; debug only allows up to 30 min.
- The command waits in your terminal until a GPU is free. Ctrl-C cancels it.
- Interactive jobs need your terminal alive. For anything long, use a batch job.

## One-hour interactive allocation from your local machine

✅ Read-only checks on 2026-10-11 confirmed `default_queue = standard`, standard enabled/started with a 96-hour maximum, at least one GPU required, and a one-hour queue default. Debug was enabled/started with a 30-minute maximum, so a one-hour request does not fit debug. The combined standard/high caps remained 242 GPUs and 3898 CPUs. These are dated policy observations, not a promise of immediate admission.

Use an interactive SSH session so `qsub -I` has a terminal. Load shell setup and activate Conda in the same shell that will submit (a separate `bash -ic 'conda activate ...'` exits without changing its parent shell):

```bash
ssh -t <kerberos_id>@pragya.iitd.ac.in
source ~/.bashrc
conda activate pragya
qsub -I -lselect=1:ncpus=16:ngpus=1 -lwalltime=01:00:00 -P <project_code>
```

Omitting `-q` uses the current default queue, verified above as standard. While the foreground command waits, use Ctrl-C to cancel, or use `qdel <jobid>` from a second logged-in terminal. Once admitted, check `hostname -f`, `$PBS_JOBID`, and `nvidia-smi` before using the allocation. Do not assume Conda initialization carries into the compute-node shell; check and activate there as needed.

✅ A pre-existing job for the tested account used the user-supplied project in high with `select=1:ncpus=16:ngpus=1`. No new job was submitted during these checks. Existing project use in high is not proof of new-job eligibility in standard. Inspect `qstat -f <jobid>` for the actual queue, state, allocation and waiting reason; avoid a purported "dry run" implemented by submitting and deleting a real job.

For persistent model serving, use a PBS script rather than keeping an interactive terminal alive. `qsub <script.pbs>` returns a job ID; the script explicitly initializes its environment and runs the foreground server within the allocation. ✅ The installed `qsub` usage also lists `qsub [options] -- command [arg1 ...]` for direct executable submission; without `--`, command arguments are not a valid replacement for a script. Serving, GPU fit and SSH forwarding still require separate tests. Do not export the entire login environment with `-V` unless necessary; it can propagate secrets and unwanted proxy settings.

## Short four-GPU allocation verified ✅ (2026-10-12)

A live interactive request with `select=1:ncpus=64:ngpus=4`, `walltime=00:10:00`, and the account's project was accepted into standard and ran on `amilan040`. The compute-node shell printed its allocated job ID; `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader` exposed four NVIDIA A100-SXM4-80GB GPUs, each reporting 81920 MiB. This identifies the GPUs visible in this allocation, not every Pragya node's hardware.

```bash
qsub -I -lselect=1:ncpus=64:ngpus=4 -lwalltime=00:10:00 -P <project_code>
```

After read-only hostname/GPU checks, the test shell exited. `qstat -xf -F json <test_jobid>` confirmed finished state, exit status 0, 64 CPUs / 4 GPUs and the requested 10-minute walltime. The pre-existing 48-hour job remained running and was not modified. Quick admission on this occasion does not prove shorter walltime always improves scheduling; resource fit, queue/project rules and current load still apply.

⚠️ In the same session, the user reported Ollama working with Qwen. Model tag, runtime endpoint, GPU offload and inference output were not independently captured in this report; distinguish that user confirmation from the directly verified allocation above.

## Ollama context and simultaneous workers ✅ (2026-10-12)

A separate 30-minute interactive allocation requested `select=1:ncpus=32:ngpus=2` and ran on `amilan015`, with two A100 80GB GPUs. Local Hermes CLI workers connected through loopback SSH tunnels; the login host was only the jump host, not an inference host. Ollama 0.40.3 served `qwen3.8:27b` (Q4_K_M) from account-owned `/flash` storage.

- Increasing context from 65536 to 131072 succeeded. Both split-server inventories reported `context_length=131072`; each runner logged 66/66 layers offloaded to GPU and a 131072-token slot. This verifies capacity, not accurate retrieval from a full 128K prompt.
- Setting `OLLAMA_NUM_PARALLEL=2` on one 128K server still produced only one runner slot (`n_seq_max=1`) in this experiment. Two launched workers queued their main generation; configuration alone did not prove concurrent inference.
- Two separate loopback servers, each restricted with `CUDA_VISIBLE_DEVICES` to a different GPU within this allocation, supported simultaneously streaming Hermes workers. Their streamed-text intervals overlapped by 20.238 seconds. Do not select GPUs outside the scheduler allocation or generalize this observed backend behavior to all Ollama models/releases.
- A focused read-only review of prior incorrect proposals took 25.865 seconds for the successful 64K solo run and 49.578 seconds for the 128K solo run. The split workers took about 101.560 seconds wall-clock, followed by 70.107 seconds for Qwen synthesis. These are single observations with different server topology/cache states, not controlled throughput measurements.
- More workers did not demonstrate better integrated correctness here: solo and team outputs missed an independently reproduced Python `str.format()` crash (`KeyError: 'CONDA_DEFAULT_ENV'`), and the synthesis retained false PBS claims. In particular, it wrongly rejected scriptless `qsub -I`, despite that being the actual working allocation command. All operational proposals still require independent verification.

The temporary servers were stopped and the interactive shell exited; `qsub` reported the evaluation job completed. Only evaluation tunnels were closed. Experimental profiles and local raw traces remain available; the default Hermes model was not changed. This was a reconstructed review with short prompts and separate Hermes CLI processes, not a full-conversation A/B, native-subagent test, or long-context recall benchmark.

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
