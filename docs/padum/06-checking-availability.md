# 6. Checking availability

## Latest availability snapshot ✅ (2026-10-13, 03:08 IST)

A read-only report on fixed `login05` with Conda `hpc` exited 0: 339 running, 111 queued and 77 held jobs; 1955 free CPUs and 79 free GPUs. GPU breakdown by reporter labels: K40 group 78, AMD EPYC GPU group 1 (scai01), A100 group 0 and V100 group 0. Labels are mappings, not fresh GPU hardware verification. The normal fetch first failed strict trust for `login5.hpc.iitd.ac.in`; a diagnostic retry used the previously established `HostKeyAlias=hpc.iitd.ac.in` with strict checking and the checked PBS PATH fallback. No known_hosts edits or job submissions were made. This snapshot does not establish queue eligibility or scheduling time.

## Remote execution verified ✅ (2026-10-11)

The existing `~/HPC-IITD-Guide` copy on this cluster completed `bash check_free_nodes.sh` with exit status 0 after loading the account's `~/.bashrc` via `bash -ic` and activating Conda environment `hpc`:

```bash
conda activate hpc
cd ~/HPC-IITD-Guide
bash check_free_nodes.sh
```

The remote copy identified Padum and reported 333 running, 146 queued, and 45 held jobs, with 1891 free CPUs and 88 free GPUs. Of those GPUs, 83 were in the K40-labelled group and 5 in the V100-labelled group; the A100-labelled group reported none free. Hardware labels are tool mappings, not fresh GPU-model verification. Job-owner details were hidden by default (`HPC_SHOW_JOBS=1` enables them). These are historical availability snapshots, not resource limits or guarantees of scheduling. Remote checkout revisions were not compared with this repository; output formats differed between the two hosts. No jobs were submitted and no inference was run.


## Local fetcher: missing PBS command diagnosis (2026-10-11)

A user-supplied fetch failure showed successful Conda activation and repository entry, but `pbsnodes` was absent from PATH. ✅ Fresh diagnostic connections to `login07.hpc.iitd.ac.in` and `login08.hpc.iitd.ac.in` found `pbsnodes` both before and after activating `hpc`. The failing login hostname was not captured, so the cause of the intermittent PATH difference remains unverified.

The local `fetch_free_nodes.py` now prints the login hostname and checks PBS tools after Conda activation. If either tool is missing, it adds `/opt/pbs/2024.1.5/bin` to that command's PATH only after verifying executable `pbsnodes` and `qstat` there; otherwise it fails with an explicit diagnostic. No remote startup files are changed. ✅ A regression test reproduced missing PBS tools on PATH and verified fallback; a live rerun on login07 returned exit status 0. The fallback branch was tested locally, not on the unidentified failing node.

✅ Follow-up on 2026-10-11: the user requested `login5.hpc.iitd.ac.in` as the fixed Padum destination, and the local fetcher was updated accordingly. It reached hostname `login05.hpc.iitd.ac.in`; the PBS PATH fallback was used and the report exited 0. Thus missing PBS tools on the initialized PATH were observed on this node; the reason for its shell setup difference remains unresolved. The endpoint's ED25519 key matched the saved key for `hpc.iitd.ac.in`; the verification run used `HostKeyAlias=hpc.iitd.ac.in` with strict checking. The normal client does not set that alias, so trust for `login5.hpc.iitd.ac.in` must be established in the client's `known_hosts` before use.

## Integrated PBS report

✅ On 2026-10-02, `pbsnodes -F json -a` and `qstat -f -t -F json` returned valid JSON on the user-identified Padum environment. The integrated report was checked against those captures; changing counts are snapshots, not cluster limits.

From this repository on a Padum login node, with Python 3 and pandas available:

```bash
bash check_free_nodes.sh
```

The shared wrapper runs `util_pbs.py` and detects Padum from PBS node names. Set `HPC_CLUSTER=padum` or pass `--cluster padum` to override; the command option takes precedence. Detection also works with saved node JSON. ✅ This selection was checked against the 2026-10-02 Padum capture and synthetic Pragya data; a live Pragya run of auto-detection remains unverified. It reports free CPU/GPU counts, unavailable nodes, jobs ordered by requested walltime end, and GPU use by owner. Multi-node jobs use each vnode's allocated resources. ⚠️ An estimated end is not a scheduling guarantee; queue limits, priority, project access, and resource fit still apply. Assignment discrepancies can also reflect limited job visibility or changes between snapshots.

To inspect saved output without querying PBS:

```bash
python3 util_pbs.py --cluster padum --nodes-json <pbsnodes.json> --jobs-json <qstat.json>
```

✅ The captured node names covered `scai`, `aice`, `vsky`, `khas`, `cice`, `csky`, `chas`, and `cgen`. ⚠️ Hardware labels come from the former local project; they do not independently verify processor or GPU models. Its `amd001` label is retained but was absent from this capture. Unknown prefixes receive their own report.

## Migration from HPC-availibility

The former `~/HPC-availibility` report is integrated into the shared engine. Original source and usage notes are preserved in [the source archive](../sources/padum-availability/README.md). The new wrapper works from any directory and uses captured JSON in memory rather than writing `test_pbs.json` or per-job temporary files. Generated captures, empty `cge_*.json` files, caches, and the empty `.git` directory were not imported; captures can contain other users' identifiers.

Use the integrated wrapper after removing the old checkout. Install pandas in your chosen Python environment if needed: `python3 -m pip install pandas`.

## Individual jobs

⚠️ Community guides report `qstat -u $USER` and `qstat -T -u $USER`; support and estimated-wait semantics remain unverified. Sources are recorded in [Padum research notes](../sources/padum-research-notes.md).

```bash
qstat -u $USER
qstat -f <job_id>
```
