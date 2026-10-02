# 8. Open questions

Resolve these on Padum with a current account or an authoritative source. Move confirmed answers to their topic page, mark ✅ with a date, and remove them here.

- The official site names PADUM at Hauz Khas and PARAM-PRAGYA at Sonipat, but does `hpc.iitd.ac.in` specifically map to Padum? Confirm current login/account instructions too.
- Which first-login setup is current: copying `.bashrc` / `.bash_profile` from `/home/apps/skeleton/` or sourcing `oneTimeHPCAccountEnvSetup.sh`?
- What are current home and scratch quotas? Community reports conflict (30 GB / 200 TB versus 100 GB / 2 TB).
- Which proxy address scheme and login helper are current: numeric IPs or program-code hostnames? What mappings apply?
- Are CPU-only requests (`ngpus=0`) supported? What are current node classes, queue names, walltime caps, job limits, and project access rules?
- Are reported `scai_q` policy and charging values current? What does each quoted rate represent?
- Are `amgr` and the referenced GPU utilization checker available and supported?
- Does `qstat -n` plus SSH to allocated nodes remain the supported resource-monitoring workflow?
- What is the official guidance for login-node use, off-campus access, data retention, and scratch cleanup?
- What content is currently in the HPC-101 FAQs and official HPC site?

Sources and their disagreements: [research notes](../sources/padum-research-notes.md).
