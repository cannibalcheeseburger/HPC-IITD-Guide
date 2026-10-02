# Padum research notes (external, unverified)

Gathered 2026-10-02 via WebFetch/WebSearch, before any direct testing on Padum. **Nothing in this file has
been run on a real Padum account.** It exists so the next session (any agent) doesn't have to re-fetch the
same pages. Treat every command here as ⚠️ until someone actually runs it and moves the confirmed parts into
`docs/padum/...` (or wherever the restructure lands them) marked ✅ with a date.

Three community repos were fetched, all apparently describing the **same** cluster at `hpc.iitd.ac.in`
(node names haswell/skylake/icelake, queue `scai_q`, 30-100GB home + 2-200TB scratch) — this is a different
cluster from the one this repo calls "pragya" (amilan/infer nodes, `proxy21.iitd.ac.in`, different queues).
Working assumption: **this is Padum.** Not confirmed by name anywhere in the fetched pages — the name "Padum"
came from the repo owner, not from these sources.

The official site initially failed direct retrieval. A later indexed search (2026-10-02) exposed the current
home page, which labels **PADUM Hauz Khas** and **PARAM-PRAGYA Sonipat**, plus official FAQ and workshop
material. Direct page fetches can still time out or require JavaScript. Official material below is
documentary evidence, not direct testing on an account; dated details and operational commands stay ⚠️.

## Source 1: github.com/kanha95/HPC-IIT-Delhi

> Described by the other two repos as the original/most complete resource ("OG Repo").

**Login:**
```
ssh username@hpc.iitd.ac.in
```
Username = abbreviated entry number.

**First-time setup:**
```
cp /home/apps/skeleton/.bashrc $HOME/.bashrc
cp /home/apps/skeleton/.bash_profile $HOME/.bash_profile
ln -s $SCRATCH $HOME/scratch
chmod og-rx $SCRATCH
chmod og-rx $HOME
```
(Aries-IITD's repo instead gives `source /home/apps/skeleton/oneTimeHPCAccountEnvSetup.sh` as the one-time
setup command — possibly the same thing updated, possibly a different/newer step. Unconfirmed which is
current.)

**File transfer:**
```
scp filename username@hpc.iitd.ac.in:~/
scp -r foldername username@hpc.iitd.ac.in:~/
```
GUI alternative: FileZilla, port 22, host `hpc.iitd.ac.in`.

**Interactive job:**
```
qsub -I -P cse -l select=2:ncpus=8:ngpus=1:mem=24G -l walltime=6:00:00
```
With the (restricted) faster nodes:
```
qsub -I -P cse -l select=2:ncpus=8:ngpus=1:mem=24G:centos=skylake -l walltime=6:00:00
```
Batch: edit and `qsub pbsbatch.sh`.

**Queues:** `standard` (default) and `high` (`-q high`, for funded/paying projects).

**Storage:**
- Home: 30GB, persistent
- Scratch: 200TB, auto-deleted after some period — move to home for archival
- Quota check: `lfs quota -hu $USER /home`, `lfs quota -hu $USER /scratch`

**Modules:** `module avail`, `module load packagename`. Reload after getting an interactive allocation.

**Proxy / internet:**
```
export SSL_CERT_FILE=$HOME/CCIITD-CA.crt     # after downloading the IITD CA cert
python2 iitdproxy.py proxyAuth.txt           # keeps the terminal open; don't close it
```
In a *new* terminal:
```
export http_proxy=10.10.78.XX:3128
export https_proxy=10.10.78.XX:3128
```
XX by program: 22 = B.Tech, 62 = M.Tech, 61 = PhD. (Different proxy IP scheme than the other two repos below,
which use a hostname + numeric suffix instead — e.g. `proxy22.iitd.ernet.in` — see Source 3. Possibly an
older/alternate proxy; don't assume one is current without checking.)

**Conda:**
```
module load apps/anaconda/3
conda create --prefix=~/myenv
source activate ~/myenv
module unload apps/anaconda/3        # after activating, to avoid clashes
```

**Common commands:**
- `qstat -u $USER`
- `qdel JOBID`
- GPU stuck/full: `nvidia-smi` then `kill -9 PID`
- `cat $PBS_NODEFILE` — nodes allocated to the current job

**Off-campus access:** email `updaters@cse.iitd.ac.in` for SRI access, then:
```
ssh username@sri.cse.iitd.ac.in
ssh username@hpc.iitd.ac.in
```
Or VPN (CSC services / OpenVPN).

**Support:** `hpchelp@iitd.ac.in`

## Source 2: github.com/Aries-IITD/HPC-101

Structured as: `GPU Nodes/`, `Proxy and Network/`, `Memory Management/`, `FAQs/`, `Misc/`. Explicitly a
"collection of problems students faced and solutions", pointing back to Source 1 as the fuller resource.
Official site and `hpchelp@iitd.ac.in` repeated here too.

**`README.md` (top level)** — just the structure description above plus a contribution note: "make sure
you do not leave your kerberos password in any of those scripts" (a rule worth keeping in our own guide too).

**`GPU Nodes/` folder:**
```
qsub -P <PROJECT_NAME> -q high -lselect=1:ncpus=4:ngpus=1:centos=<haswell/skylake/icelake> -lwalltime=23:59:59 -I
```
- Queues/pricing: `standard` Rs 1/GPU/hr + Rs 0.1/GPU/hr (two numbers given, meaning unclear — maybe GPU +
  CPU, or on-demand + idle); `high` Rs 5/GPU/hr + Rs 0.5/GPU/hr; `scai_q` dedicated to "Yardi School of AI"
  projects with 80GB A100s.
- `centos=` node choices: `haswell` (older GPUs), `skylake` (32GB V100), `icelake` (40GB A100 standard /
  80GB A100 on `scai_q`).
- Max walltime: 168h standard/high; `scai_q` A100s capped at 24h.
- `qstat -u $USER` — remaining time; `qstat -u $USER -T` — expected wait before start.
- `python3 gpu_util_checker.py <JOB_ID>` — a script in that repo folder that monitors GPU utilization and
  can kill underutilized jobs (kill lines commented out by default). Not fetched/verified here.
- Tip: `screen -S anti_job_blowout` to hold an interactive allocation, detach with Ctrl-A D, then ssh
  straight into the allocated node — lets you close the original terminal without losing the job. (Compare
  our own `tmux` guidance for Pragya — same idea, different tool.)

**`Proxy and Network/` folder:**
```
screen -S proxy
chmod +x proxy.sh
./proxy.sh
```
Detach: Ctrl-A, D. Also gives a pip SSL workaround:
```
pip install <PACKAGE/REQUIREMENTS_LIST/BUILD> --trusted-host=pypi.org --trusted-host=files.pythonhosted.org --user
```

**`FAQs/README.md`:** fetch returned only the heading "## HPC FAQs" with no visible body — either empty,
or the content is images/not plain markdown. Re-check directly if the FAQ page matters:
https://github.com/Aries-IITD/HPC-101/blob/main/FAQs/README.md

**Main `README.md` also documents** (this is the single most detailed source found):

Account creation: apply at https://userm.iitd.ernet.in/usermanage/hpc.html with Kerberos ID/password; one
field asks for a "Faculty supervisor (uid)" and an account expiry date (the example used was 15 Dec, i.e.
these accounts expire and get renewed). One-time setup:
```
source /home/apps/skeleton/oneTimeHPCAccountEnvSetup.sh
```

VSCode Remote-SSH: add host `{kerberos_username}@login1.hpc.iitd.ac.in`.

Internet setup (their version — differs from Source 1's in the proxy address format):
```bash
# download proxy.sh from the repo, fill in kerberos username/password, and set:
proxy_add = "https://proxy{PROGRAM_CODE}.iitd.ernet.in/cgi-bin/proxy.cgi"
# PROGRAM_CODE map:
#   btech=22 dual=62 diit=21 faculty=82 integrated=21 mtech=62 phd=61
#   retfaculty=82 staff=21 irdstaff=21 mba=21 mdes=21 msc=21 msr=21 pgdip=21
./proxy.sh &
export http_proxy="http://proxy{PROGRAM_CODE}.iitd.ac.in:3128"
export https_proxy="http://proxy{PROGRAM_CODE}.iitd.ac.in:3128"
wget google.com    # verify
```
Note: our own `pragya` proxy script (`~/cert/proxy.sh`) also points at a `proxy.cgi` login page and uses
`proxy21.iitd.ac.in:3128` — `21` would be `staff` in this map. Consistent with the account used in this
session being a staff account. Worth checking if Padum uses the exact same login backend as Pragya's
normal proxy (same `proxy.cgi`, same program-code scheme) — plausible, since it's the same institute-wide
proxy infrastructure, just a different numbered proxy node/program code.

Conda: `wget https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh` then
`sh Anaconda3-2024.06-1-Linux-x86_64.sh`.

Interactive / batch jobs: same `qsub -I ...` shape as above; batch via a generic `batchjob.sh` from the repo
(contents below); `qstat -T -u {kerberos_userid}`; `qstat -ans {job_id}`; `qdel {job_id}`.

Rules stated: max 168h per job; max 10 concurrently running jobs per user; max 2 jobs per user on `scai_q`;
**never run code on login nodes — 30 warnings and the account is banned** (this is a much more concrete/harsh
rule than anything observed on Pragya so far — worth highlighting prominently if confirmed for Padum).

Research proxy (same one documented for Pragya, `10.10.88.6:3128`):
```
./research_proxy.sh &            # after getting an interactive job, in the same terminal
export https_proxy=http://10.10.88.6:3128
export http_proxy=http://10.10.88.6:3128
wget www.google.com              # ping is disabled on this HPC
```
Same "one device/terminal at a time" and "no extra compute, just faster downloads" caveats as the Pragya
version. (This increases confidence that Pragya's and Padum's research-proxy setups are the same shared
institute resource, not cluster-specific.)

Data sharing between two HPC accounts:
```
setfacl -m u:{KERBEROS_USERID_OF_DESTINATION}:rwx $HOME/scratch/datasets
chmod og+rwx $HOME/scratch/datasets
```

AMGR (balance/allocation tool):
```
amgr login
amgr ls project
amgr checkbalance project -n {PROJECT_NAME}
```
(No equivalent seen yet on Pragya — worth checking if `amgr` exists there too.)

**`batchjob.sh` (generic template from this repo), verbatim:**
```sh
#!/bin/sh
#PBS -N {JOB_NAME}
#PBS -P {PROJECT_NAME}
#PBS -q standard
#PBS -m bea
#PBS -M $USER@iitd.ac.in
#PBS -l select=1:ncpus=1:ngpus=1:centos={NODE}
#PBS -l walltime=50:00:00
# $PBS_O_WORKDIR is the directory from where the job is fired.

echo "==============================="
echo $PBS_JOBID
cat $PBS_NODEFILE
echo "==============================="
cd $HOME

# Now you can add all the regular linux command which you would have run in the interactive job
```

**`sample_batch_job.sh`** (a real, personal example job from the repo — not reproduced verbatim here since
it names a specific person's project code, email and file paths; the useful shape is: job name, project,
queue `standard`, walltime 36h, `ncpus=1:ngpus=0:centos=icelake` (a CPU-only job on an icelake node), email
notifications on, then in-script: print job id + `$PBS_NODEFILE`, source the proxy exports, `conda activate`
an env, `cd` to a scratch path, run a Python script). Confirms: (a) you can request `ngpus=0` for CPU-only
work on Padum (unlike Pragya, which refuses any job without ngpus>=1 — a real, confirmed difference between
the two clusters if this is accurate), (b) the proxy exports are commonly sourced inside the batch script
itself so the job can reach the internet while running.

## Source 3: github.com/mahesh-keswani/HPC-Details

This is the repo already used as a source for Pragya's `proxy.sh` and `research_proxy.sh` (see
`docs/pragya/04-internet-and-proxy.md`). It describes general IITD HPC GPU-node and proxy/network tips,
and appears to discuss the Padum system in its community guidance. The shared institute context makes
some concepts plausibly relevant to both clusters, but does not prove that hostnames, scripts, access
rules, or performance match. Pragya pages retain direct observations; Padum claims remain ⚠️ until checked.
The repository's direct URL is https://github.com/mahesh-keswani/HPC-Details.

## Open questions this raises (see `docs/padum/08-open-questions.md`)

- Is "Padum" actually the name of the `hpc.iitd.ac.in` cluster these three repos describe? Not confirmed
  by any fetched source — only by the repo owner's own statement.
- Which setup is current: `cp /home/apps/skeleton/.bashrc ...` (Source 1) or
  `source /home/apps/skeleton/oneTimeHPCAccountEnvSetup.sh` (Source 2)? They may be the same script renamed,
  or two different eras.
- Which proxy scheme is current: numeric IP by program (`10.10.78.XX`, Source 1) or
  `proxy{code}.iitd.ernet.in` hostname (Source 2)? Could both work; could one be stale.
- Storage numbers disagree between sources: 30GB home / 200TB scratch (Source 1) vs 100GB root / 2TB
  scratch (Source 2). Different account tiers? Different point in time? Needs a real `lfs quota` check.
- Does Padum really allow `ngpus=0` (CPU-only jobs), unlike Pragya? If true, that's a genuine, useful
  contrast to put in a cluster-comparison table.
- Is the "30 warnings -> ban" login-node rule real and current? Worth confirming before stating it as fact,
  but worth warning users about even with a caveat either way.
- `amgr` balance tool, `gpu_util_checker.py`, and the FAQs page content were not actually retrieved — only
  described secondhand. Fetch them directly if/when someone has a Padum account to test against.

## Source 4: IIT Delhi official HPC material (retrieved 2026-10-02)

- [Official HPC homepage](https://supercomputing.iitd.ac.in/) currently distinguishes PADUM (Hauz Khas)
  from PARAM-PRAGYA (Sonipat). This supports the cluster names; it does not explicitly tie the legacy
  `hpc.iitd.ac.in` hostname to Padum.
- [Official PBS FAQ/example page](https://supercomputing.iitd.ac.in/cesm_instruction.php) shows a PBS
  `qsub` error for a project's maximum queued jobs and another error saying a project cannot use `high`.
  It also documents ACL-based file sharing. Its examples look legacy and are not proof of current
  policies; use the messages as diagnostic leads and confirm with admins.
- [PADUM workshop slides, 2023-01-12](https://supercomputing.iitd.ac.in/workshop_files/HPC-2023-01-12.pdf)
  recommend avoiding multi-minute work on login nodes, profiling and estimating resources before
  production jobs, working from scratch, backing up important outputs in home, and reporting unusual
  errors or corruption to `hpchelp@iitd.ac.in`. For resource monitoring, they suggest getting allocated
  node names with `qstat -n <job_id>`, then using `top -u $USER` for CPU processes and `nvidia-smi`
  (or `nvidia-smi -l 1`) for GPU use on those nodes. This should only be done for one's own allocation.
- [HPC tutorial, 2024-05-02](https://supercomputing.iitd.ac.in/workshop_files/HPC_20240502.pdf)
  is an official newer training source; the fetched index exposes its title and support contact, but not
  enough text to distill more specific procedures safely.
- The current site reports total system storage, but those totals are not individual quotas. They do not
  resolve the conflicting community-reported home/scratch quotas above.
- The original community guide mentions clearing a GPU process with `kill -9` after CUDA errors. This is
  unsafe as a general fix on shared systems and is not recommended here: inspect only processes in your
  own job and ask support if resources remain stuck.
