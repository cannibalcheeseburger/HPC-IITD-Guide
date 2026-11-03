# Field notes, November 2026

Things learned while running CPU-only experiment batches on both clusters (non-interactive SSH, `qsub` scripts, a
repo kept in sync by hand). ✅ marks something observed directly; ⚠️ marks an inference or a cause that was not
confirmed. Usernames, project codes and proxy details are placeholders (`<user>`, `<project>`).

## Pragya

- ✅ Compute nodes seen in `pbsnodes -a`: 50 `amilan*` nodes (AMD Milan, `ncpus=128`, up to 8 GPUs each) plus one
  `infer` node. There are no haswell or skylake nodes, so no node-type restriction is needed.
- ✅ The `standard` queue (`qstat -Qf standard`): 10 running and 20 queued jobs per user, `walltime` up to 96:00:00,
  and a minimum of one GPU per job (`resources_min.ngpus = 1`).
- ✅ A CPU-only workload still has to request `ngpus=1`. A 64-core request sat in the queue with
  `would exceed overall limit on resource std_high_gpu_...` while nearly every GPU on the cluster was assigned,
  then started about 17 minutes later. Asking for more CPUs does not help in that state, because the wait is for
  GPU quota. (The message itself is already described in [Pragya running jobs](pragya/03-running-jobs.md).)
- ✅ Plain `ssh <host> qstat` works here (`/opt/pbs/default/bin` is on the PATH of a non-interactive session).
- ⚠️ `git` was not installed on the login node when checked (`rpm -q git`: not installed), although `git` had
  worked in an earlier session on the same login node about half an hour before. It may differ per login node or
  have been removed. A script that shells out to `git` on the login node (for example a clean-tree check before
  submission) then fails with `PermissionError: ... 'git'`. A stand-in `git` that exits 0, put on the PATH only for
  that one command, avoids the crash but also hides a dirty tree, so check the tree before using it.

## Padum

- ✅ `hpc.iitd.ac.in` resolves to three login nodes (`login05`, `login07`, `login08` here), and the DNS answer
  rotates between connections. Key authentication works on each, and a command takes about 1.4 s.
- ✅ Node families from `pbsnodes -a`: `aice` (64 cores, 2 GPUs), `cgen` (128 cores, about 770 GB), `chas`, `cice`
  (64 cores), `csky` (40 cores, about 95 GB), `khas`, `scai` and `vsky`. The `chas`/`khas` and `csky`/`vsky` names
  follow the haswell and skylake naming in the older notes; ⚠️ that mapping was inferred from names and was not
  confirmed node by node.
- ✅ `-l select=1:ncpus=30:centos=genoa` landed on `cgen004`, so `centos=genoa` selects the `cgen` nodes in practice.
  No GPU request was needed, which answers the open question about CPU-only requests for these nodes.
- ✅ With no `-q` in the script the job went to the `standard` queue.
- ✅ A 30-core request started about a minute after submission, while a 64-core request showed
  `Not Running: Insufficient amount of resource: ncpus`. Smaller requests found a free node much sooner.
- ✅ A non-interactive `ssh <host> cmd` does not have `qstat` on its PATH (`qstat: command not found`). Use
  `ssh <host> 'bash -lc "qstat ..."'`.
- ✅ A login shell costs about 2.8 s against 1.4 s for a plain command. The extra 1.4 s is the conda initialisation
  block in `~/.bashrc`. Wrapping that block so non-interactive shells skip it removes the cost, and batch scripts
  should `source .../conda.sh` explicitly anyway.
- ⚠️ A first connection attempt with a 25 s timeout was terminated while later attempts took 1.4 s. The cause was
  not found; the connection was reproducibly fast afterwards.
- ✅ Padum and Pragya have separate home directories, even though the path string looked the same. A checkout on
  one is not the checkout on the other.

## Both: pushing code when GitHub is unreachable from the cluster

- ✅ From a Padum login node, `git fetch` over SSH through the HTTP proxy failed with
  `kex_exchange_identification: Connection closed by remote host`. ⚠️ The proxy may need its login script run first;
  that was not tried.
- ✅ A workaround that needs no GitHub access: create a bundle on a machine that has the commits, copy it over
  SSH, fast-forward from it.

```bash
git bundle create sync.bundle <branch> ^<commit-the-cluster-already-has>
scp sync.bundle <cluster>:~/
ssh <cluster> 'cd ~/<repo> && git fetch ~/sync.bundle <branch> && git merge --ff-only FETCH_HEAD'
```

  The cluster checkout then shows `ahead N` of its `origin` ref until a normal push or fetch happens. Check the tree
  is clean first, because `--ff-only` refuses to overwrite divergent work.

## Faster repeated SSH from your own machine

Connection reuse in `~/.ssh/config` saves the handshake on repeat commands (Pragya dropped from 1.3 s to 0.6 s):

```text
Host pragya.iitd.ac.in hpc.iitd.ac.in
    User <user>
    GSSAPIAuthentication no
    ControlMaster auto
    ControlPath ~/.ssh/cm/%r@%h:%p
    ControlPersist 10m
    ServerAliveInterval 30
```

Create the socket directory first (`mkdir -p ~/.ssh/cm && chmod 700 ~/.ssh/cm`). Padum stays near 1.3 s per command
because each command still starts the remote shell and its `.bashrc`.

## Sizing a batch of single-core jobs

- ✅ A tool that packs N independent single-core runs into one PBS job asked for `ncpus=N`. Requesting more cores
  than runs only leaves cores idle and can lengthen the queue wait.
- ✅ The jobs' wait state is visible with `qstat -f <jobid> | grep -E 'job_state|comment'`.
- ✅ A duplicate submission to both clusters is easy to cancel while it is still queued (`qdel <jobid>`); do it
  before the second one starts, since a shared project pays for core-hours on whichever cluster actually runs.
