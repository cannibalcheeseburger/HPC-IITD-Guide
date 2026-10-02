# Repository Guidelines

## Purpose and structure

This repository is a practical reference to IIT Delhi's Pragya and Padum HPC systems, plus a shared PBS availability tool. `docs/pragya/` contains directly tested Pragya guidance; `docs/padum/` contains Padum guidance with per-claim verification markers; `docs/faq.md` holds cross-cluster answers; `docs/sources/` keeps raw research. `docs/hpc-job-workflow.dot` is the editable source for its PNG. PBS examples live in `examples/pragya/` and `examples/padum/`. `util_pbs.py` supports both clusters through `check_free_nodes.sh`. Labels are auto-detected from PBS node names; `--cluster` overrides `HPC_CLUSTER`.

## Verification and documentation

- Mark directly tested claims ✅ and date values that can change (quotas, queue limits, speeds). Mark claims from documentation, community repositories, or inference ⚠️ and cite the source.
- The three community repositories in `docs/sources/padum-research-notes.md` are sources about Padum. General workflows may also be useful on Pragya, but apply cluster-specific settings only when they are independently verified. Similarity is not verification.
- Add findings to the appropriate page in the same session. Keep one canonical home per fact; move resolved questions out of open-question pages.
- Keep pages short and scannable. Update indexes, examples, and relative links when moving files.

## Development and checks

The current working environment is Padum, as identified by the user. The former `~/HPC-availibility` project is integrated here; its original source is retained in `docs/sources/padum-availability/`. Use `bash check_free_nodes.sh` on Padum. Verify individual commands and findings before marking them as directly tested.

There is no build system, test suite, linter, or formatter. On a Pragya login node, `bash check_free_nodes.sh` runs the live availability report and requires Python 3, pandas, `pbsnodes`, and `qstat`. For offline input, use `python util_pbs.py --nodes-json <pbsnodes.json> --jobs-json <qstat.json>`. Offline captures also support auto-detection; use `--cluster padum` or `--cluster pragya` to override. Cluster selection changes node labels; PBS commands query the local server, so run the shared wrapper on the intended cluster.

For documentation-only changes, review Markdown links and commands against their cited source and verification marker. Avoid submitting cluster jobs just to validate prose unless the task calls for direct testing.

## Style and examples

Use Markdown headings, short paragraphs, tables for comparisons, and fenced `bash` or `sh` examples. Use placeholders such as `<project_code>` and `<kerberos_id>`; never include real credentials, tokens, personal identifiers, or another person's project code. Keep Pragya and Padum PBS scripts in their corresponding example directories and label untested Padum requests ⚠️.

## Git and contributions

Use plain, factual commit messages (for example, `Add Padum proxy research notes`). Describe the affected cluster and verification status in change summaries. No pull request template or formal test gate is configured; include relevant links and note any unverified operational detail when proposing changes.
