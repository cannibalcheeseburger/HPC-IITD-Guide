# Padum

✅ PBS availability reporting was tested on the user-identified Padum environment on 2026-10-02. Other instructions remain unverified. ⚠️ This guide summarizes three community repositories that describe `hpc.iitd.ac.in`; the identification of the current environment as Padum is user-supplied. Confirm operational details with the HPC administrators or an account holder before relying on them.

## Research-based starting points

The repositories generally describe PBS jobs with `qsub`, home and scratch storage, environment modules, and proxy-based internet access. They disagree on setup scripts, storage quotas, proxy addresses, and some resource rules. General HPC workflows may also be relevant to Pragya, but cluster settings are documented there only from separate direct observations. Conflicts and citations are recorded in [open questions](08-open-questions.md) and [Padum research notes](../sources/padum-research-notes.md).

Sources: [kanha95/HPC-IIT-Delhi](https://github.com/kanha95/HPC-IIT-Delhi), [Aries-IITD/HPC-101](https://github.com/Aries-IITD/HPC-101), and [mahesh-keswani/HPC-Details](https://github.com/mahesh-keswani/HPC-Details).

## Pages

1. [Cluster overview](01-cluster-overview.md)
2. [Getting started](02-getting-started.md)
3. [Running jobs](03-running-jobs.md)
4. [Internet and proxy](04-internet-and-proxy.md)
5. [Python environments](05-python-environments.md)
6. [Availability checks](06-checking-availability.md)
7. [Troubleshooting](07-troubleshooting.md)
8. [Open questions](08-open-questions.md)

An example batch template is at [`examples/padum/batch_job.pbs`](../../examples/padum/batch_job.pbs); its resource requests are illustrative and unverified.
