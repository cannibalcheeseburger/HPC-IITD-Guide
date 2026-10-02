# 7. Troubleshooting (unverified)

No Padum errors have been reproduced by this project. These are source-reported starting points, not confirmed fixes.

| Symptom | Suggested next step |
|---|---|
| `qsub: Maximum number of jobs for project ... already in queue ...` | ⚠️ Official FAQ example indicates a project queue job-count limit. Inspect current jobs and ask the project/HPC admin about its limit before resubmitting. |
| `Project ... cannot use high queue for job submission` | ⚠️ Official FAQ example indicates the project lacks `high` queue access. Use an authorized queue or request access; changing resource size will not grant queue permission. |
| Job remains queued | Inspect `qstat -f <job_id>` for scheduler comments; verify queue access and requested resources. ⚠️ |
| Python command or package is missing | Check `module avail` and activate the intended environment within the allocation. ⚠️ |
| Internet request fails | Verify proxy authentication and address with current Padum guidance; see [proxy notes](04-internet-and-proxy.md). ⚠️ |
| Job is running but seems idle or slow | ⚠️ Use `qstat -n <job_id>` to find its allocated nodes, then inspect your own processes with `top -u "$USER"` and GPU use with `nvidia-smi` on those nodes. Compare actual use with the resources requested. |
| GPU appears occupied after a program exits | Inspect `nvidia-smi`; ask support before terminating a process you do not own. ⚠️ |

These two exact scheduler messages appear in IIT Delhi's [official FAQ/example page](https://supercomputing.iitd.ac.in/cesm_instruction.php), but the page may contain legacy examples; verify current limits and access with admins.

When a symptom is reproduced, record the exact message, cause, and tested fix here with the date. Keep all untested suggestions marked ⚠️.
