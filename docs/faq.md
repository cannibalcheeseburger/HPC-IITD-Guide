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
