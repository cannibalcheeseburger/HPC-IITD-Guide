# 8. Open questions

Things this guide doesn't know yet. When one is answered, move it into the right page, mark it ✅ with the date,
and delete it here.

## Access and accounts

- What is the external SSH login hostname / VPN requirement?
- Is `-P <project_code>` strictly required, and how does a user look up their own code?
- Are there accounting or usage charges? Jobs carry an `am_job_cache` resource with a `cost_factor`, which suggests some
  allocation tracking, but nothing was confirmed.

## Hardware and software

- Which GPU model is in the `amilan` (8 GPUs, NVLink) and `infer` (2 GPUs, PCIe) nodes? PBS doesn't say.
- Which NVIDIA driver / maximum CUDA version do compute nodes have? (A CUDA 13 PyTorch build is installed in one env; not yet tested on a GPU.)
- Is the `nvidia-smi` command available on GPU nodes? (Assumed, not tested.)

## Scheduling

- What is the `high` queue for, and who may use it? It has no visible access list.
- Does `debug` get scheduling priority over `standard`? No evidence yet either way.
- Which projects may use `ext1_q`, `ext2_q`, and `ext3_q`, and how is eligibility enforced?
- Are there additional per-user GPU or project limits? The visible `standard` running/queued job limits
  are recorded in [cluster overview](01-cluster-overview.md#queue-resource-quotas--2026-09-30).
- Why do jobs without a walltime get 48 h when the server default says 1 min? (Probably a submit hook; can't read hooks without admin rights.)

## Storage

- What is `/flash` intended for, and does it have a purge policy or quota? `/home` showed no quota for the tested user.
- Backups? Off-campus data transfer route?

## Network

- ~~Research proxy from a compute node: untested~~ -> ✅ answered 2026-09-19, see [docs/04](04-internet-and-proxy.md):
  both proxies failed outright from a compute node (not just slow). New question: does running the proxy
  login script *from the compute node itself* (as the research-proxy guide describes) change that?
- Where exactly is the per-connection throttle: proxy, campus link, or upstream? Only admins can say. Measured numbers are in [docs/04](04-internet-and-proxy.md).
- Is it faster off-peak? Only one evening was measured.
