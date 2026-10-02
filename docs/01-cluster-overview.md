# 1. Cluster overview

Facts observed on 2026-09-19, with queue quota updates on 2026-09-30. Hardware and queue settings can change; re-check with the commands shown.

## Hardware ✅

| Node names | Count | CPU cores | GPUs per node | GPU link | RAM |
|---|---|---|---|---|---|
| `amilan001` – `amilan050` | 50 | 128 | 8 | NVLink | ~1 TB |
| `infer01` – `infer02` | 2 | 48 | 2 | PCIe | ~0.5 TB |

- All nodes have GPUs. GPU model: ⚠️ not exposed by PBS (see open questions).
- Login nodes are named `login01`, `login03`, ... (96 CPUs, shared by everyone).
- Scheduler: **PBS Pro 2026.0.0**, server name `pragya`.
- About a quarter of the `amilan` nodes are often `offline` (typical reasons: "Unable to clean up one or more cgroups",
  or a health-check hook marking them offline). Offline nodes take no new jobs. The availability tool lists them.

Check yourself: `pbsnodes -a` (or `bash check_free_nodes.sh`).

## Queues ✅

| Queue | Max walltime | Who | Notes |
|---|---|---|---|
| `standard` | 96 h | everyone | default queue; needs >= 1 GPU |
| `debug` | **30 min** | everyone | for short tests; needs >= 1 GPU and an explicit walltime |
| `high` | 96 h | no access list shown | purpose unknown ⚠️ |
| `admin` | 48 h | restricted user list | admins only |
| `workq` | - | disabled | |
| `ext1_q`, `ext2_q`, `ext3_q` | not shown in queue config | project eligibility unconfirmed ⚠️ | enabled; separate resource caps (2026-09-30) |

Free hardware does not guarantee that a queue can allocate it: queue/server quotas also apply.
These caps do not establish dedicated physical nodes for each queue. Check with `qstat -Q` and `qstat -Qf <queue>`.

## Queue resource quotas ✅ (2026-09-30)

Observed with `qstat -Bf` and `qstat -Qf`; the shared standard/high policy was also confirmed by the supplied admin configuration screenshot.

| Queue group | GPU cap | CPU cap | Scope |
|---|---:|---:|---|
| `standard` + `high` combined | 242 | 3898 | server `max_run_res.std_high_gpu_quota` / `std_high_cpu_quota` |
| `ext1_q` | 81 | 1299 | queue `max_run_res.ngpus` / `ncpus` |
| `ext2_q` | 40 | 650 | queue `max_run_res.ngpus` / `ncpus` |
| `ext3_q` | 41 | 649 | queue `max_run_res.ngpus` / `ncpus` |

The GPU split is approximately 60% / 20% / 10% / 10% of 404 GPUs. Limits marked
`[o:PBS_ALL=...]` apply overall, not separately to each user. Switching from `standard` to `high`
does not bypass their shared cap. The `high` queue exposes `cost_factor = 2.5` versus `1` for
`standard`; actual charging semantics remain unconfirmed.

`standard` also shows per-user limits of 10 running jobs and 20 queued jobs
(`max_run` and `max_queued`, `[u:PBS_GENERIC=...]`).

Snapshot on 2026-09-30 around 01:42 IST: `standard` had 242 GPUs assigned, `high` had 0;
`ext1_q`, `ext2_q`, and `ext3_q` had 72, 8, and 21 respectively. These are historical usage
counts, not current availability. Project eligibility for the `ext*` queues must be confirmed with the PI/HPC admins.

```bash
qstat -Bf                 # server-wide caps
qstat -Qf                 # queue caps, assigned resources, and visible access rules
qstat -f <jobid>          # scheduler comment; long lines may wrap
```

## The rules that trip people up ✅

1. **At least one GPU per job.** Otherwise: `qsub: Please request at least one GPU using "ngpus=<value>"`.
   This applies to every queue, including `debug`. It is a server-side check.
2. **State a walltime.** If you don't, the job asks for 48 h (observed), which `debug` rejects with
   `Job violates queue and/or server resource limits`.
3. **Project code:** jobs are submitted with `-P <project_code>` (the code your group was given).
   Whether it is strictly mandatory: ⚠️ untested.

## Storage ✅

| Path | What | Notes |
|---|---|---|
| `/home/...` | your home directory | Lustre, shared with every node. No per-user quota was reported for the tested account (quota shown as 0 = unset). |
| `/flash/...` | second Lustre area | Same filesystem servers as `/home`. Other users' job logs point at `/flash/<dept>/...`; intended use ⚠️ confirm with admins. |
| `/tmp`, `/` | local disk of each node | Not shared; not for results. |

Check your usage: `lfs quota -h -u $USER /home`.

## Installed software ✅

Loaded with **environment modules**: `module avail`, `module load <name>`, `module list`.

- **CUDA:** `cuda/11.6`, `11.8`, `12.6`, `13.0`; also `nccl/2.28.3-1`
- **MPI:** `openmpi/4.1.6`, `openmpi/5.0.9`, `openmpi/5.0.9_cuda13`
- **Python / ML:** `anaconda/2025.06`, prebuilt `conda-2025/pytorch-gpu-2.9.1/py3.14`, `tf-gpu-2.19.1`, `tf-gpu-2.20.0/py3.10`, plus scikit-learn, pandas, numpy, matplotlib, jupyter and others
- **Containers:** `Apptainer/1.4.5`, `singularity/4.3.5`
- **Simulation:** GROMACS (2021.4, 2024.2, 2026.0), LAMMPS (GPU), NAMD (GPU), CP2K (GPU), Quantum ESPRESSO (GPU), VASP (GPU), OpenFOAM (CPU)
- **Other:** `gcc/10.5.0`, R 4.5.2, Julia 1.12.7, MATLAB R2025a, ffmpeg, gnuplot, VMD

## Words you will see in PBS

| Term | Meaning |
|---|---|
| `select=1:ncpus=4:ngpus=1` | one "chunk" (part of a node) with 4 cores and 1 GPU |
| walltime | maximum run time you request; the job is killed at that point |
| `Q` / `R` / `H` | queued / running / held |
| `exec_vnode` | which node(s) and how many cores/GPUs a running job got |
