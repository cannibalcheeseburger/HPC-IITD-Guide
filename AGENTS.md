# AGENTS.md

Instructions for any AI agent (Claude Code, Codex, etc.) working in this repository.

## Current state / handoff (read this first)

**2026-10-02:** Repo is being restructured from "Pragya-only guide" into a **multi-cluster reference**
covering two IIT Delhi HPC systems: **Pragya** (this session's own cluster, directly tested) and **Padum**
(the older `hpc.iitd.ac.in` system, known only from community repos so far — no direct account access).
This restructure was just started and handed off mid-way; nothing about Padum has been written into the
guide proper yet. Picking this up:

1. **Read `docs/sources/padum-research-notes.md` first.** It's a raw, citation-linked dump of everything
   found on Padum from three community GitHub repos (kanha95/HPC-IIT-Delhi, Aries-IITD/HPC-101,
   mahesh-keswani/HPC-Details) plus a failed attempt at supercomputing.iitd.ac.in (returned no usable
   content via fetch — try again with a real browser, or ask the owner to paste the relevant page). It is
   explicitly unverified (⚠️ everywhere) and flags several **disagreements between the three sources**
   (storage quotas, proxy address scheme, setup script name) that need resolving, ideally by someone with
   an actual Padum account.
2. **Decide and execute the folder split.** Everything in `docs/01` through `08` right now is 100%
   Pragya-specific despite generic names. Recommended shape (not yet done):
   - `docs/pragya/01-...` through `08-...` — move the existing files here as-is (git mv, keep history)
   - `docs/padum/01-...` — mirror the same topic numbers/names, populate from the research notes, every
     claim marked ⚠️ until someone tests it on Padum, then ✅ with a date
   - A shared top-level `docs/faq.md` or similar for questions that apply to both (e.g. "why is my job
     waiting", "how do I speed up downloads") with cluster-specific answers inline, rather than duplicating
     prose per cluster where the mechanism is genuinely identical (e.g. the research-proxy backend looks
     shared between both clusters — see the notes file).
   - `README.md` becomes a top-level index pointing at both cluster trees, each cluster's own README/index
     keeps its "quick start".
   - `examples/` should probably split into `examples/pragya/` and `examples/padum/` once a Padum batch
     template exists (one candidate PBS script is already transcribed in the research notes).
   - Update this file (or split it into `docs/pragya/AGENTS.md` / `docs/padum/AGENTS.md` if that ends up
     clearer) once the split is done — keep one canonical set of maintenance rules, don't fork them.
3. **The verification-marker convention (✅ / ⚠️) and "one home per fact, move don't duplicate" rule below
   apply to Padum content from day one** — don't let unverified community-repo claims get stated as fact.
4. Nothing else is mid-flight: no background jobs, downloads, or qsub jobs are pending from the Pragya work
   (see `docs/pragya` history below — the proxy test job that was queued when this session started has
   since completed; its result is already recorded in docs/04 / docs/08).
5. Repo hygiene already done in this handoff: removed 24 zero-byte `cge_*.json` leftovers and `__pycache__`;
   replaced a broken empty `.git/` with a real `git init` (first commit will be made right after this file
   is written — check `git log` to see what's already committed vs. new).

## What this repo is

A **living, hands-on reference for navigating IIT Delhi's HPC clusters and their quirks** — not an
official document, a record of things actually tried, with sources and dates. Plus a small tool
(`util_pbs.py` / `check_free_nodes.sh`) that reports free GPUs/CPUs on Pragya right now.

The owner wants it **simple but complete**, covering both clusters, **kept growing as things are learned**,
and usable as a quick lookup ("how do I get around this cluster's quirks") rather than read start to finish.

## Maintaining the guide

- **When you learn something, add it to the right page in the same session.** Facts come from things
  actually run (errors hit, commands tried, measurements) — or, for Padum until someone has access, from a
  named external source — never from memory or assumption.
- **Mark verification on every non-trivial claim.** ✅ = tested directly (add a date if the value can
  drift: speeds, queue limits, free resources, quotas). ⚠️ = from documentation/a community repo/inference,
  not tested by us. Don't state untested things as fact, and don't let a ⚠️ silently turn into fact on a
  later edit — re-verify first.
- **Cite sources for anything not tested directly**, especially Padum content: which repo/page, so the next
  person can re-check it. `docs/sources/` holds raw external research; pages under `docs/` hold the
  distilled, cited version.
- **One home per fact — move, don't duplicate.** When an open question gets answered, put the answer on
  its proper page and delete the question. New unknowns go into the relevant open-questions list.
- **Errors go in a troubleshooting page** as message -> cause -> fix. Reproduced ones get ✅.
- Keep pages short and scannable (tables, small code blocks). Keep index/contents tables in sync when
  adding a page.
- **Never write secrets or personal identifiers into the repo:** no passwords or tokens, no usernames or
  IDs of other people, no personal project codes (use `<project_code>`). If a password shows up in tool
  output, don't repeat it anywhere, including in commit messages.
- Don't commit throwaway files. Scratch work goes in the session scratchpad; big downloads go to
  `~/wheelhouse/` (outside this repo), not here.
- This is a real git repo now (`git init` done 2026-10-02) — commit as you go with plain, factual messages;
  no attribution lines needed.

## The availability tool (Pragya only, for now)

- Run: `bash check_free_nodes.sh` (runs `python3 util_pbs.py`, ~1s). Needs python3 + pandas
  (`conda activate pragya` works) and `pbsnodes`/`qstat` on `PATH` (a Pragya login node).
- Offline testing: `python util_pbs.py --nodes-json <pbsnodes -F json -a output> --jobs-json <qstat -f -t -F json output>`.
- No test suite, linter, or build step.

Everything is in `util_pbs.py`. `main()` fetches `pbsnodes -F json -a` and one `qstat -f -t -F json` (all
jobs), then:

1. `build_allocations`: one row per (job, node) for running jobs, using the per-node share parsed from
   `exec_vnode` (`(amilan009:ncpus=40:ngpus=1)+(amilan023:...)`). Don't use the job-wide `Resource_List`
   for per-node numbers; it double-counts multi-node jobs.
2. `print_available_resources`: for `state == 'free'` nodes, free = `resources_available -
   resources_assigned` (PBS's own accounting, which the scheduler uses); also lists offline/down nodes
   with their `comment`.
3. `print_unbacked_assignments`: flags nodes whose `resources_assigned` exceeds what running jobs account
   for (stale PBS accounting).
4. `report_node_type`: per type, top 10 jobs by end (`stime + walltime`) and per-user GPU totals; jobs on
   offline/down nodes are excluded.

Node type = hostname (from `Mom`) with trailing digits stripped; `NODE_TYPE_MAPPING` only supplies
friendlier names. If this tool is ever extended to Padum, it would need a second PBS endpoint/credentials
and different node-type prefixes (haswell/skylake/icelake per the research notes) — not attempted yet.

## Pragya facts to remember (details live in `docs/`)

- 52 nodes: `amilan001-050` (128 cores, 8 GPUs) and `infer01-02` (48 cores, 2 GPUs). Every job must
  request >= 1 GPU; always set a walltime (`debug` max 30 min). Queues: `standard`, `debug`, `high`,
  `admin` (restricted), `workq` (disabled), plus `ext1_q`/`ext2_q`/`ext3_q` with their own GPU/CPU quotas.
- No direct internet from the login node; use `proxy21.iitd.ac.in:3128`. Single connections are throttled
  (~0.4 MB/s); parallel `aria2c` downloads reach ~5 MB/s. **From a compute node, both the normal and
  research proxy failed outright** (not just slow) in the one test run so far — see `docs/04`.
- Job IDs may be array subjobs (`123[4].pragya`), only listed with `qstat -t`; array parents have state
  `B` and no `exec_vnode`.

## Gotchas

- `test_pbs.json` is a stale `pbsnodes` snapshot no longer written by the scripts; only useful as a
  `--nodes-json` test fixture.
