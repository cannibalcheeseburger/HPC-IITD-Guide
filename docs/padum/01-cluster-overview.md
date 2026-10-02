# 1. Cluster overview (unverified)

⚠️ IIT Delhi's [official HPC site](https://supercomputing.iitd.ac.in/) currently labels PADUM at Hauz Khas and PARAM-PRAGYA at Sonipat. The community sources below describe `hpc.iitd.ac.in`; the exact mapping of that legacy host to the Padum system is not stated explicitly in the fetched official material. Details may be old or account-specific.

## Reported configuration

| Topic | Community-reported details |
|---|---|
| Nodes | `haswell`, `skylake`, `icelake` classes; exact hardware and availability need confirmation. [Aries-IITD/HPC-101](https://github.com/Aries-IITD/HPC-101) |
| Queues | `standard`, `high`; `scai_q` also appears in one account. Access and current policies are unknown. [Aries-IITD/HPC-101](https://github.com/Aries-IITD/HPC-101) |
| Scheduler | PBS-style `qsub`, `qstat`, and `qdel`. [kanha95/HPC-IIT-Delhi](https://github.com/kanha95/HPC-IIT-Delhi) |
| Storage | Home and scratch are described, but reported per-user quotas conflict: 30 GB / 200 TB versus 100 GB / 2 TB. Do not rely on either value. Official site-wide storage totals are not user quotas. |

The cited community and official material is collected in the [research notes](../sources/padum-research-notes.md). Check `qstat -Qf`, `lfs quota`, and administrator guidance on an active account before choosing resources or planning storage.

## Reported cautions

⚠️ A community guide warns against running computation on login nodes. Use a scheduler allocation and confirm local policy. CPU-only jobs, per-user limits, walltime caps, and queue pricing are unresolved; see [open questions](08-open-questions.md).
