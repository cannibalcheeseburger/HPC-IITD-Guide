# 3. Running jobs (unverified)

⚠️ The following PBS forms are transcribed from [kanha95/HPC-IIT-Delhi](https://github.com/kanha95/HPC-IIT-Delhi) and [Aries-IITD/HPC-101](https://github.com/Aries-IITD/HPC-101). Queue names, project access, resources, and limits need direct confirmation.

## Interactive example

```bash
qsub -I -P <project_code> -q standard \
  -l select=1:ncpus=4:ngpus=1 -l walltime=01:00:00
```

Some source examples add `centos=haswell`, `skylake`, or `icelake` to the resource request. Check the scheduler's current accepted resource names before using them. Sources disagree on whether CPU-only jobs are allowed.

## Plan and run jobs responsibly

⚠️ IIT Delhi's [2023 Padum workshop](https://supercomputing.iitd.ac.in/workshop_files/HPC-2023-01-12.pdf) recommends profiling and estimating resource, walltime, and disk needs before production runs; avoiding multi-minute computation on login nodes; and doing scratch work in scratch while backing up important results in home. Confirm current filesystem policy and quotas first. The same general workflow matches Pragya's directly tested scheduler-first guidance, but paths and retention rules differ.

## Check resource use in a running job

⚠️ The same workshop suggests listing allocated nodes with `qstat -n <job_id>`, then checking your own processes on each allocated node with `top -u "$USER"`; for GPU jobs, use `nvidia-smi` or `nvidia-smi -l 1` and stop the monitor with Ctrl-C. Follow current site access rules when connecting to allocated nodes. This helps distinguish a scheduler problem from a program that is not using the requested CPU/GPU resources.

## Batch jobs

See the [illustrative Padum batch template](../../examples/padum/batch_job.pbs). Submit with `qsub <script>` only after confirming project, queue, resource, and walltime requirements.

Reported monitoring commands:

```bash
qstat -u $USER
qstat -f <job_id>
qdel <job_id>
cat "$PBS_NODEFILE"
```

These commands and reported walltime/job-count limits remain ⚠️. Do not infer a start time from queue listings.
