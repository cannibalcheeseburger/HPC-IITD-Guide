# 6. Checking availability (unverified)

⚠️ Community guides report `qstat -u $USER` for a user's jobs and `qstat -T -u $USER` for estimated wait information. Confirm support and output semantics on Padum.

```bash
qstat -u $USER
qstat -f <job_id>
```

There is no Padum equivalent of this repository's Pragya-only `util_pbs.py` report. Queue listings do not establish that a request can start: resource fit, project access, limits, and priority may apply. Do not use Pragya's node names, queue quotas, or availability tool as Padum data.

To document a future availability tool, first capture Padum's own PBS output and verify the resource fields with an account holder.
