# 4. Internet and proxy

## Direct internet does not work ✅

Direct connections to the internet time out. Everything goes through the IITD campus proxy:

```bash
export http_proxy=http://proxy21.iitd.ac.in:3128
export https_proxy=http://proxy21.iitd.ac.in:3128
```

Put these in a small file and `source` it (running it with `bash file` sets the variables only for that
child process, not for your shell). ✅ `curl`, `pip` and `aria2c` were used successfully with these variables;
`wget`, `conda` and `git` normally honour them too ⚠️ (not tested here).

Quick test: `curl -sI https://pypi.org | head -1`

## Proxy login ✅

The campus proxy authenticates by IP address, using a web login that must be refreshed every ~2 minutes.
Scripts named `proxy.sh` do exactly that in a loop. On the shared login nodes many people run one, so
your script will often just print `Already logged in` and exit. That is fine: the IP is already
authenticated and the proxy works without your script running.

### Proxy script review (2026-10-02)

The account-local `~/cert/proxy.sh` follows the login/session-refresh pattern described by the community
[HPC-Details repository](https://github.com/mahesh-keswani/HPC-Details). I reviewed the local copy without
including its credential values here. It stores credentials in the script and uses `curl -k`, which skips
TLS certificate validation. It is therefore not copied into this repository. Keep credentials out of
version control and use the IITD CA certificate to validate the proxy connection; do not copy `-k` into
new scripts. The exact upstream script revision could not be fetched in this environment, so a line-by-line
comparison remains pending.

If the proxy ever stops working, restart a login loop in a `tmux` session (see
[docs/02](02-getting-started.md)).

### Credentials

Do not hardcode your password in a script, and never commit it. Keep it in a file only you can read
(`chmod 600 ~/.proxy_pass`) and read it in the script, or ask the script to prompt. If it was ever
exposed (pasted into a chat, log or repo), change it.

## How fast is it? (measured 2026-09-19 evening) ✅

| Test | Result |
|---|---|
| Latency to the proxy | ~4 ms (LAN) |
| Latency to first byte, external site | 60-280 ms |
| **Download, 1 connection, normal proxy** | **0.4-0.5 MB/s** (3-4 Mbit/s) |
| Download, 4 connections | ~1.4 MB/s combined |
| Campus mirror (`mirrors.iitd.ac.in`), no proxy | ~0.9 MB/s |
| Upload, 10 MB | ~5 MB/s |
| **`aria2c` 4 files x 8 connections, 2.85 GB from PyPI** | **~5.3 MB/s average** (9 min) |

What this means:

- Each single connection is throttled somewhere between the cluster and the internet, well below the
  10 Gb/s network card. The login node itself was not saturated.
- **Parallel connections add up.** Splitting downloads is the fix; see below.
- Numbers depend on time of day. Re-measure if it matters.

Repeat the measurement:

```bash
curl -s -o /dev/null -w '%{speed_download} B/s\n' "https://speed.cloudflare.com/__down?bytes=25000000"
```

## Fast downloads: use `aria2c` ✅

`aria2c` is installed (`/usr/bin/aria2c`). It splits every file into several connections and downloads
several files at once:

```bash
aria2c -x 8 -s 8 -k 5M <url>                       # one big file, 8 connections
aria2c -i urls.txt -d outdir -j 4 -x 8 -s 8 -k 5M  # many files: 4 at once, 8 connections each
```

It reads `http_proxy`/`https_proxy` from the environment. For pip packages, see the
[wheelhouse recipe in docs/05](05-python-environments.md).

Tip: `git clone`, `conda install` and plain `pip install` use one connection per file and stay slow for
large files.

## Campus mirror ✅

`https://mirrors.iitd.ac.in` is reachable directly (no proxy). It carries Ubuntu and Debian.
It has **no** PyPI, Anaconda or conda-forge mirror (those paths return 404).

## Research proxy ⚠️

A second proxy, `10.10.88.6:3128`, is described in a community guide
(github.com/mahesh-keswani/HPC-Details) as giving "high-speed, large data downloads". According to
that guide: run its `research_proxy.sh` (a login script like the normal one, pointing at a different
login page) from an **interactive HPC job**, with your Kerberos credentials, and only **one terminal or
device may use it at a time**.

What we tested:

- ✅ From the **login node** it is reachable and answered without any login by us.
- ✅ Speed from the login node: 0.49-0.51 MB/s per connection, **same as the normal proxy**.
- ✅ From a **compute node** (`amilan023`, debug-queue job, 2026-09-19 23:35 IST): **both proxies failed outright**,
  not just slowly. `curl -x <proxy>` returned `http=000` in ~0.01s, `curl exit code 56` ("failure in receiving
  network data") for every request to both `proxy21.iitd.ac.in:3128` and `10.10.88.6:3128`. TCP connect to the
  proxy itself succeeded (~4ms) but no HTTP response came back.

So on this cluster, at least at the time tested: compute nodes may not have the same outbound route to either
proxy that login nodes have. This was only tried without first running `research_proxy.sh`'s login step from
the compute node (its login may be what opens the route — the guide says to request the job *then* run the
login script there). ⚠️ Whether running the login script from the compute node changes this is untested.
If you need internet access from inside a job, do the proxy login (or any one-off curl/pip/wget call) from the
login node first, or test the login step from the compute node yourself and update this page.
