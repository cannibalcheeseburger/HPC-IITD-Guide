# 5. Python environments

## Pick an environment tool ✅

| Option | When to use |
|---|---|
| Your own conda env (`conda create -n name python=3.10`) | Most projects; full control |
| `python -m venv .venv` | Small projects, no conda needed |
| Prebuilt modules, e.g. `module load conda-2025/pytorch-gpu-2.9.1/py3.14` | You just need PyTorch/TF and the versions match |

Always activate the environment (also inside job scripts) and check the right `pip` is in use:

```bash
conda activate myenv
which pip && pip --version        # should point inside the env, and be pip >= 22.2 for the recipe below
```

Outside an env, `pip` is the system one (Python 3.9, pip 21.x), which is too old for the recipe below.
`pip install -U pip` fixes that inside an env.

## Why installs are slow here

`pip` and `conda` download one file at a time over one connection, and each connection is throttled
to about 0.4 MB/s ([docs/04](04-internet-and-proxy.md)). PyTorch with its CUDA libraries is several GB:
about 2 hours that way. Downloading in parallel first cuts it to minutes.

## Fast pip installs (wheelhouse) ✅

Download the wheels in parallel with `aria2c`, then install from the local folder with no network.
Do not run several `pip install` commands at once in the same environment: pip has no locking and they can
corrupt each other. Parallelize only the downloading.

```bash
conda activate myenv
mkdir -p ~/wheelhouse/myproject && cd ~/wheelhouse/myproject

# 1. let pip work out the exact files, without installing anything (needs pip >= 22.2)
pip install --dry-run --quiet --report report.json -r /path/to/requirements.txt

# 2. turn the report into a list of URLs
python -c "import json; [print(i['download_info']['url']) for i in json.load(open('report.json'))['install']]" > urls.txt

# 3. download: 4 files at once, 8 connections each
aria2c -i urls.txt -d wheels -j 4 -x 8 -s 8 -k 5M -c --file-allocation=none --console-log-level=warn

# 4. install from the local files only
pip install --no-index --find-links wheels -r /path/to/requirements.txt
```

Notes:

- **Already-installed packages are skipped** in step 1, so the wheelhouse only contains what was missing.
  To make a wheelhouse that can build a fresh environment, add `--ignore-installed` in step 1.
- `-c` lets you re-run step 3 and resume interrupted downloads.
- The wheels depend on your Python version and platform, so resolve with the same env you install into.
- Run long downloads inside `tmux`.

### Measured result (2026-09-19)

Project with 12 pinned packages (numpy, pandas, scipy, matplotlib, torch 2.13.0, tensorboard, gymnasium,
pandapower, ...), Python 3.10:

| Step | Result |
|---|---|
| Resolve (step 1) | 64 files, 2.85 GB, 9 s |
| Download (step 3) | **9 min**, ~5.3 MB/s average (a single connection would take ~2 h) |
| Install (step 4) | 1 min 27 s, no network |
| Check | `pip check` clean; all pinned versions match; all imports work |

## PyTorch and CUDA ✅ / ⚠️

- `pip install torch` from PyPI installs a CUDA build plus its libraries (`nvidia-*` wheels). Here it gave
  `torch 2.13.0+cu130`, i.e. built for **CUDA 13.0**.
- ✅ `import torch` works on the login node, but `torch.cuda.is_available()` is `False` there because
  login nodes have no GPU. That is expected.
- ⚠️ Whether the GPU driver on the compute nodes supports CUDA 13 was not verified. Check inside a
  GPU job: `python -c "import torch; print(torch.cuda.is_available())"`. If it prints `False` on a GPU node,
  install a torch build that matches the driver (pytorch.org lists the options) or use a prebuilt module.
- The `cuda/13.0` module exists (`module load cuda/13.0`) if you need the compiler/toolkit itself.
  Prebuilt wheels don't need it.

## conda ✅

`conda install` downloads packages in parallel, but each one on a single connection, so large packages
are still slow. Just be patient, or use the system modules where a fitting one exists.
