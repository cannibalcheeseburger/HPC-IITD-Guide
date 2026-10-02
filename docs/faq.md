# Cross-cluster FAQ

Use the page for the relevant cluster when a mechanism or value differs. Similar command names do not mean the systems share configuration.

![HPC job workflow](hpc-job-workflow.png)

The editable diagram is [`hpc-job-workflow.dot`](hpc-job-workflow.dot).

## Which cluster am I using?

Pragya pages refer to `amilan` / `infer` nodes and PBS server `pragya`. Padum material refers to `hpc.iitd.ac.in`, but that mapping is still unverified; see the [Padum open questions](padum/08-open-questions.md).

## Why is my job waiting?

Read the scheduler comment and check current queue/resource limits. On [Pragya](pragya/03-running-jobs.md), queue quotas can block jobs even with free nodes. For [Padum](padum/03-running-jobs.md), the exact policy is unverified. Free-node counts alone do not promise a start on either system.

General practices supported across the guides: request only the resources and walltime your run needs, test/profile before a large production run, and submit computation through PBS instead of running it on a shared login node. Pragya has direct observations; Padum's similar recommendations come from the [official 2023 workshop slides](https://supercomputing.iitd.ac.in/workshop_files/HPC-2023-01-12.pdf).

## How do I share files with another HPC user?

Padum's [official FAQ example](https://supercomputing.iitd.ac.in/cesm_instruction.php) documents Linux ACLs (`setfacl`) for granting access to selected users and warns that storage may be charged to the file owner's account. This is standard Linux behavior, but the cluster's current filesystem policy and quota accounting should be confirmed. On Pragya, check with the storage owner/admin before changing permissions on shared directories.

## Can I use the same proxy settings on both?

Do not assume so. Pragya's settings and measured behavior are in [its proxy page](pragya/04-internet-and-proxy.md); Padum's community sources disagree on addresses and helpers ([Padum proxy notes](padum/04-internet-and-proxy.md)).

## How should credentials be handled?

Never commit passwords or tokens, and do not place them in scripts shared with others. Keep any local credential file private and use current institute instructions. This is also emphasized by the community [HPC-101 repository](https://github.com/Aries-IITD/HPC-101).

## Why does GitHub SSH work from one IITD machine but not another?

Network access and SSH keys are machine-specific. A user-reported test from the Pragya login node succeeded with `ssh -T git@github.com` over port 22 using a pre-existing registered key ([details](pragya/04-internet-and-proxy.md#github-ssh-access-from-the-pragya-login-node--user-report-2026-10-02)). In the separate environment used to edit this repository, direct SSH timed out on ports 22 and 443, and HTTPS push lacked credentials. A success on Pragya does not establish that another host has the same route or key.

### Option A: tunnel SSH through that host's HTTP CONNECT proxy

⚠️ This recipe was supplied by the repository owner and has not been tested from this editing environment. It requires a working HTTP CONNECT proxy and OpenBSD `nc` with `-X connect` support; check `nc -h` because other netcat variants use different options. Replace the proxy placeholder using the settings for the host where you will run Git.

```bash
ssh -o BatchMode=yes -p 443 -o HostKeyAlias=github.com \
  -o "ProxyCommand=nc -X connect -x <proxy-host>:<proxy-port> %h %p" \
  -T git@ssh.github.com
```

If that reports successful GitHub authentication, use the same connection settings for the push:

```bash
GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=15 -p 443 -o HostKeyAlias=github.com -o Hostname=ssh.github.com -o "ProxyCommand=nc -X connect -x <proxy-host>:<proxy-port> %h %p"' \
  timeout 100 git push -u origin <branch>
```

GitHub documents `ssh.github.com` on port 443 as an alternate SSH endpoint; the proxy tunnel is an additional host-specific step ([GitHub instructions](https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port)).

### Option B: HTTPS remote and local credential setup

When HTTPS works through the host's configured proxy, use an HTTPS remote and authenticate locally with GitHub CLI:

```bash
git remote set-url origin https://github.com/<owner>/<repo>.git
gh auth login
gh auth setup-git
git push -u origin <branch>
```

This requires `gh` to be installed and the signed-in account to have push access. Do not paste a token into chat, a script, or the repository. Run either option on the machine whose network and credentials you intend to use.
