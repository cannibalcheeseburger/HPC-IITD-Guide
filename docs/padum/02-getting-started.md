# 2. Getting started (unverified)

⚠️ These steps come from community repositories and have not been tested on Padum. Confirm current access instructions with IIT Delhi HPC support.

## Login and account

The [HPC-IIT-Delhi guide](https://github.com/kanha95/HPC-IIT-Delhi) reports SSH access via `hpc.iitd.ac.in` and an account request page at `https://userm.iitd.ac.in/usermanage/hpc.html`:

```bash
ssh <kerberos_id>@hpc.iitd.ac.in
```

Use your own account identifier; never copy personal usernames from examples. Off-campus access requirements are not verified.

## First login setup

Sources conflict between copying shell files from `/home/apps/skeleton/` and sourcing `oneTimeHPCAccountEnvSetup.sh`. Do not run either blindly; ask an account holder which setup applies to a new account. See [open questions](08-open-questions.md).

## Files and software

⚠️ Community sources suggest `scp` for transfers, `module avail` / `module load <name>` for modules, and reloading modules after entering a compute allocation. Example:

```bash
scp local-file <kerberos_id>@hpc.iitd.ac.in:~/
module avail
```

See [Python environments](05-python-environments.md) for the source-reported Anaconda setup. Never place passwords in scripts or commit them.
