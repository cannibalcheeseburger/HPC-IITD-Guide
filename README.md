# IIT Delhi HPC Guide

A practical, evolving reference to IIT Delhi's Pragya and Padum HPC systems. ✅ marks direct testing; ⚠️ marks a claim drawn from documentation, community repositories, or inference. Padum has not been tested directly; treat its pages as research notes, not official instructions.

## Choose a cluster

- **[Pragya](docs/pragya/README.md):** directly tested, with PBS guidance and a live resource availability tool.
- **[Padum](docs/padum/README.md):** community-sourced guidance for the older `hpc.iitd.ac.in` system; every operational detail remains unverified.

## Shared topics

[FAQ and cross-cluster notes](docs/faq.md) collects general questions and clearly separates any cluster-specific answers. Raw, cited source material is in [docs/sources](docs/sources/).

![HPC job workflow](docs/hpc-job-workflow.png)

Editable diagram source: [`docs/hpc-job-workflow.dot`](docs/hpc-job-workflow.dot).

## Repository layout

```text
docs/pragya/       Verified Pragya guide (plus its open questions)
docs/padum/        Cited, unverified Padum guide and open questions
docs/sources/      Raw external research notes
examples/pragya/   Pragya PBS example
examples/padum/    Padum PBS template (unverified)
util_pbs.py        Pragya PBS availability reporting
check_free_nodes.sh  Main wrapper; check_nodes.sh is a compatibility alias
```

## Availability tool (Pragya only)

On a Pragya login node, with Python 3, pandas, `pbsnodes`, and `qstat` available:

```bash
bash check_free_nodes.sh
# Alias: bash check_nodes.sh
```

For offline input, pass captured PBS JSON: `python util_pbs.py --nodes-json nodes.json --jobs-json jobs.json`. The tool does not query Padum.

## Contributing

Add findings to the relevant cluster page in the same session. Cite sources for untested details and retain ⚠️ until direct verification; date values that can change. Keep one canonical home per fact, update links and indexes when moving pages, and never commit passwords, tokens, personal identifiers, or project codes.
