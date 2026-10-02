# 2. Getting started

## Log in

```bash
ssh <kerberos_id>@<login-host>
```

⚠️ The external login hostname was not verified here; get it from the IIT Delhi HPC page or admins.
You land on a login node (`login01`, `login03`, ...). Login nodes are shared: use them for editing files,
submitting jobs and light checks, not for computation.

## One-time shell setup ✅

Login shells (what SSH gives you) read `~/.bash_profile` and **do not** read `~/.bashrc` unless
`~/.bash_profile` says so. If that file is missing, `conda` and other things set up in `~/.bashrc`
will not be found after you log in.

```bash
ls ~/.bash_profile || cp /etc/skel/.bash_profile ~/.bash_profile
source ~/.bashrc            # apply to the current session
```

Test: `env -i HOME=$HOME bash -l -c 'type conda'` should print `conda is a function`.

## Conda ✅

Two options:

- **Your own Miniconda** in your home directory (needs internet through the proxy; see
  [docs/04](04-internet-and-proxy.md)). Run `conda init bash` once, which adds a block to `~/.bashrc`.
- **The system Anaconda:** `module load anaconda/2025.06`.

```bash
conda create -n myenv python=3.10
conda activate myenv
conda env list
```

More on packages: [docs/05](05-python-environments.md).

## Modules ✅

```bash
module avail                 # everything installed
module avail cuda            # search
module load cuda/13.0        # add to your session
module list                  # what is loaded
module purge                 # unload everything
```

Put the `module load` lines inside your job script too, because a job starts with a clean environment.

## tmux: sessions that survive disconnects ✅

```bash
tmux new -s work        # start a named session
# Ctrl-b then d         # detach (it keeps running)
tmux ls                 # list sessions
tmux attach -t work     # come back
```

Handy for long downloads and for keeping a proxy-login script alive.
Inside `man`/`less` press `q` to quit, or the pane will look "stuck".

## Moving files

Use `scp` or `rsync` from your own machine. ⚠️ Details for off-campus transfers not verified.
Large data belongs on `/home` or `/flash`, not on `/tmp`.
