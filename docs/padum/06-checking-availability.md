# 6. Checking availability

## Integrated PBS report

✅ On 2026-10-02, `pbsnodes -F json -a` and `qstat -f -t -F json` returned valid JSON on the user-identified Padum environment. The integrated report was checked against those captures; changing counts are snapshots, not cluster limits.

From this repository on a Padum login node, with Python 3 and pandas available:

```bash
bash check_padum_nodes.sh
```

The wrapper runs `util_pbs.py --cluster padum`. It reports free CPU/GPU counts, unavailable nodes, jobs ordered by requested walltime end, and GPU use by owner. Multi-node jobs use each vnode's allocated resources. ⚠️ An estimated end is not a scheduling guarantee; queue limits, priority, project access, and resource fit still apply. Assignment discrepancies can also reflect limited job visibility or changes between snapshots.

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
