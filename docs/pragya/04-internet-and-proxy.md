# 4. Internet and proxy

## Direct campus SSH transfer experiment ✅ (2026-10-11)

From the tested client, SSH to Pragya used a direct campus connection, not the HTTP proxy. A bounded upload benchmark sent existing model bytes to remote `/dev/null` (no files created): one 8 MiB stream achieved 1.49 MiB/s including connection setup; four simultaneous 8 MiB streams achieved 3.00 MiB/s aggregate. This suggests parallel streams can help on this path, but it is a small sample, not a sustained disk-write benchmark or a guaranteed speedup.

For large model transfers, avoid compression and prefer resumable staging. Ordinary rsync uses one stream; transferring separate files concurrently will not accelerate a single dominant weight blob. To parallelize that blob, stage distinct chunks in separate remote files, join in exact order, and verify full SHA-256 before publishing the final blob and manifest. Never direct concurrent rsync writers at the same destination file or use `--delete` on a shared model cache. Confirm site transfer policy and avoid excessive concurrency. Preserve strict SSH host-key verification when selecting a resolved IP; hostname aliases must remain bound to their already trusted key.


## Registry manifest connectivity ✅ (2026-10-11)

A read-only check from `login02.head.cm.pragya.iitd.ac.in` fetched the official `qwen3.8:27b` manifest with HTTP 200 in about 0.57 seconds using the initialized shell's proxy settings. The same URL with `curl --noproxy '*'` failed to connect. This establishes proxy-dependent registry access on that login node, not on the user's current compute node. `ollama pull` downloads through the server process: changing proxy variables only in the client terminal does not update an already running server. Configure working `HTTPS_PROXY`/`https_proxy` and localhost exclusions before starting the user-owned server; do not restart another user's or a site-wide server. Never include proxy credentials in the guide. See the [official FAQ](https://docs.ollama.com/faq) for proxy configuration; it cautions against setting `HTTP_PROXY` for Ollama.

## Curl blob workaround ⚠️ (user report, 2026-10-12)

The user reports that the exact `qwen3.8:27b` manifest and CDN files were reachable with curl through the research proxy, while Ollama 0.40.3 stalled at zero bytes on its first blob and opened a direct connection to a Cloudflare address. This is reported evidence of a client/download-path difference, not independent confirmation that Ollama universally ignores `HTTPS_PROXY`. The source of the bypass (client behavior, redirects, environment or network policy) remains unresolved; no packet capture or proxy logs were available. The user reports checking model/tag validity, CDN access, User-Agent, HTTP/2 and storage headroom.

A private `dl.sh` reportedly stages 128 MB pieces via parallel curl connections, resumes pieces, joins them, checks full blob hashes and publishes verified content under `$OLLAMA_MODELS/blobs`. The script has not been inspected or independently exercised here; it is not yet a validated repository utility. The user reports similar roughly 9–10 MB/s aggregate throughput with 24 and 64 connections, suggesting a shared bottleneck but not proving it is specifically the proxy. Avoid excessive concurrency when no measured gain results.

The user also reports overlapping old/new retry loops writing the same piece files and causing corruption. Use one writer per piece, separate per-run staging, and tracked process IDs or process groups; broad `pkill -f` patterns can match and kill their own invoking shell. Stop old writers before resuming, verify range coverage and exact assembled size, then check each manifest-referenced blob's SHA-256. Publish the manifest only after every referenced blob (including config/projector layers) verifies. Keep partial pieces separate from published blobs and do not delete them until verification completes. Confirm loading/inference only inside a PBS GPU allocation; download progress is not proof of a usable model.

## Official downloads without client-to-cluster rsync ⚠️

✅ A follow-up manifest request from login02 explicitly using the user-supplied research proxy `http://10.10.88.6:3128` returned HTTP 200 in about 0.60 seconds. ⚠️ The user suspects another session authenticated that shared node's egress IP; the authentication identity/mechanism and permission to reuse that session were not checked. Reachability does not prove authorization or durable authentication. Use the account's authorized proxy login procedure and do not depend on another person's session remaining valid.


The user reports working internet on a Pragya login node. Official runtime sources are [Ollama Linux manual installation](https://docs.ollama.com/linux) and the [release assets](https://github.com/ollama/ollama/releases/tag/v0.40.3). The official x86-64 asset is `ollama-linux-amd64.tar.zst`; a user-local extraction keeps both `bin/` and `lib/` together without sudo or a login-node service. The v0.40.3 release API reports SHA-256 `ce6f8b671a699bf1ebafb28d60dbbabf4f37b30b499145fa308a8ba72de021d6` for this archive. A separately transferred v0.40.3 runtime was already hash-verified under the tested account's `/flash` directory; do not reinstall unnecessarily.

Download models on the login node without running inference by fetching the official registry manifest (`https://registry.ollama.ai/v2/library/qwen3.8/manifests/27b`) and its referenced blobs (`/v2/library/qwen3.8/blobs/<sha256:digest>`). Verify every declared size and SHA-256 before placing the manifest at `$OLLAMA_MODELS/manifests/registry.ollama.ai/library/qwen3.8/27b`. Download/resume into separate partial files and publish content atomically; preserve other cached models. This HTTP-only path does not require starting `ollama serve` on the login node. ⚠️ This registry download workflow has not yet been exercised on Pragya's internet connection; successful local registry use does not verify compute-node internet or GPU compatibility.

For standard `ollama pull`, a running Ollama server is required. Keep `ollama serve` and inference inside a PBS allocation unless site administrators explicitly permit a download-only login-node service. User-reported login-node internet does not establish compute-node internet. See [Ollama FAQ](https://docs.ollama.com/faq) for proxy and `OLLAMA_MODELS` configuration.

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
Scripts named `proxy.sh` do exactly that in a loop. Older copies exit on `Already logged in`;
the locally reviewed revision below keeps retrying. That response alone does not establish that
your own session is active or that downloads will continue working.

### Retry on an existing proxy session ⚠️ (local code review, 2026-10-19)

The current `~/proxy.sh` on the local `strider` host prints
`Already logged in (another session); retrying in 30s` instead of exiting. Its login function
sleeps for 20 seconds; when the response lacks `logged in successfully`, the outer loop sleeps
another 10 seconds before requesting a new session and trying again. The effective delay on
that path is about 30 seconds plus request time. After a successful login, it refreshes every
120 seconds and returns to the login loop if a refresh fails.

This keeps the helper available to retry when the existing session ends. It does not guarantee
connectivity while waiting. These details were checked against the local script, not exercised
on Pragya or Padum; older `~/cert/proxy.sh` copies may differ. Use your own authorized login
and verify connectivity separately. The credential-bearing script is not included here.

### Proxy script review (2026-10-02)

The account-local `~/cert/proxy.sh` follows the login/session-refresh pattern described by the community
[HPC-Details repository](https://github.com/mahesh-keswani/HPC-Details). I reviewed the local copy without
including its credential values here. It stores credentials in the script and uses `curl -k`, which skips
TLS certificate validation. It is therefore not copied into this repository. Keep credentials out of
version control and use the IITD CA certificate to validate the proxy connection; do not copy `-k` into
new scripts. The exact upstream script revision could not be fetched in this environment, so a line-by-line
comparison remains pending.

### GitHub SSH access from the Pragya login node ✅ (user report, 2026-10-02)

On the Pragya machine, `ssh -T git@github.com` succeeded over the normal SSH route using an existing
`~/.ssh/id_rsa` key already registered with GitHub; no proxy or port-443 workaround was needed. This is
specific to that machine and key. Do not infer that SSH works from every IITD host or from the environment
used to edit this repository. For a host where direct SSH is blocked, see the [cross-host GitHub guidance](../faq.md#why-does-github-ssh-work-from-one-iitd-machine-but-not-another).

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
