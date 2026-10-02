# 5. Python environments (unverified)

⚠️ The [HPC-IIT-Delhi guide](https://github.com/kanha95/HPC-IIT-Delhi) reports a system Anaconda module and creating an environment under home. [HPC-101](https://github.com/Aries-IITD/HPC-101) also describes downloading an Anaconda installer. Neither flow has been tested here; check available modules and current storage limits first.

Reported module-based pattern:

```bash
module load apps/anaconda/3
conda create --prefix="$HOME/myenv"
conda activate "$HOME/myenv"
```

Sources differ on whether to unload the module after environment activation and how batch jobs should activate it. Test imports inside a scheduled allocation before depending on an environment. See [open questions](08-open-questions.md).

For package downloads, consult the [proxy page](04-internet-and-proxy.md). Do not assume Pragya's measured download rates or wheelhouse recipe will behave the same way on Padum.
