# 2. Getting started

✅ SSH access and existing-account shell initialization were tested on 2026-10-11 as described below. ⚠️ New-account setup and other community instructions remain unverified; confirm current policy with IIT Delhi HPC support.

## Login and account

The [HPC-IIT-Delhi guide](https://github.com/kanha95/HPC-IIT-Delhi) reports SSH access via `hpc.iitd.ac.in` and an account request page at `https://userm.iitd.ac.in/usermanage/hpc.html`:

```bash
ssh <kerberos_id>@hpc.iitd.ac.in
```

Use your own account identifier; never copy personal usernames from examples. Off-campus access requirements are not verified.

### Tested existing-account access ✅ (2026-10-11)

Key-authenticated SSH to `hpc.iitd.ac.in` succeeded with an existing account and matching saved host key, reaching `login05.hpc.iitd.ac.in` and `login07.hpc.iitd.ac.in`. The user identifies this environment as Padum; these checks do not independently resolve the legacy-host mapping to the official system name.

The initial non-interactive shell did not expose `qstat` on PATH. Loading the account's existing `~/.bashrc` via interactive Bash exposed both `qsub` and `qstat` under `/opt/pbs/2024.1.5/bin`:

```bash
ssh <kerberos_id>@hpc.iitd.ac.in 'bash -ic '\''hostname -f; command -v qsub; command -v qstat; command -v ollama'\'''
```

An account-local Ollama binary resolved at `$HOME/ollama/bin/ollama`; its version, model cache, GPU compatibility, and serving status were not checked. This is not evidence of a site-wide installation. One SSH command completed only after roughly 30 seconds following authentication, so a short timeout can misidentify slow shell initialization as failed access. Bash's no-terminal job-control warnings did not prevent execution. No shell files were changed, jobs submitted, or inference run.

## First login setup

Sources conflict between copying shell files from `/home/apps/skeleton/` and sourcing `oneTimeHPCAccountEnvSetup.sh`. Do not run either blindly; ask an account holder which setup applies to a new account. See [open questions](08-open-questions.md).

## Files and software

⚠️ Community sources suggest `scp` for transfers, `module avail` / `module load <name>` for modules, and reloading modules after entering a compute allocation. Example:

```bash
scp local-file <kerberos_id>@hpc.iitd.ac.in:~/
module avail
```

See [Python environments](05-python-environments.md) for the source-reported Anaconda setup. Never place passwords in scripts or commit them.
