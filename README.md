# IIT Delhi HPC Guide

A practical, evolving reference to IIT Delhi's Pragya and Padum HPC systems. ✅ marks direct testing; ⚠️ marks a claim drawn from documentation, community repositories, or inference. Padum availability reporting has been tested directly; other Padum operational guidance remains research-based unless marked ✅.

## Choose a cluster

- **[Pragya](docs/pragya/README.md):** directly tested, with PBS guidance and a live resource availability tool.
- **[Padum](docs/padum/README.md):** community-sourced guidance for the older `hpc.iitd.ac.in` system, with a tested PBS availability report; other operational details remain unverified.

## Shared topics

[FAQ and cross-cluster notes](docs/faq.md) collects general questions and clearly separates any cluster-specific answers. Raw, cited source material is in [docs/sources](docs/sources/).

![HPC job workflow](docs/hpc-job-workflow.png)

Editable diagram source: [`docs/hpc-job-workflow.dot`](docs/hpc-job-workflow.dot).

## Repository layout

```text
docs/pragya/       Verified Pragya guide (plus its open questions)
docs/padum/        Padum guide with per-claim verification and open questions
docs/sources/      Raw external research notes
examples/pragya/   Pragya PBS example
examples/padum/    Padum PBS template (unverified)
util_pbs.py        Shared PBS availability reporting
check_free_nodes.sh  Shared availability wrapper
```

## Availability tools

On either cluster’s login node, with Python 3, pandas, `pbsnodes`, and `qstat` available:

```bash
bash check_free_nodes.sh
```

Cluster labels are automatically detected from PBS node names. Override with an environment variable or command option (the option takes precedence):

```bash
HPC_CLUSTER=padum bash check_free_nodes.sh
bash check_free_nodes.sh --cluster pragya
```

Use `export HPC_CLUSTER=padum` in your Padum shell setup if you prefer a fixed selection; use `pragya` on Pragya. `--cluster auto` explicitly requests detection, overriding the environment. Selection changes labels and queries the local PBS server.

For offline input, pass both captures; detection uses the captured node names:

```bash
python3 util_pbs.py --nodes-json <pbsnodes.json> --jobs-json <qstat.json>
```

Unknown clusters use generic node prefixes; mixed known cluster names require an explicit selection. See [Padum availability](docs/padum/06-checking-availability.md) for verification and migration details.

## Contributing

Add findings to the relevant cluster page in the same session. Cite sources for untested details and retain ⚠️ until direct verification; date values that can change. Keep one canonical home per fact, update links and indexes when moving pages, and never commit passwords, tokens, personal identifiers, or project codes.
