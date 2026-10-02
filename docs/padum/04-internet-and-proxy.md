# 4. Internet and proxy (unverified)

⚠️ Proxy setup reports conflict and none has been tested for Padum. Confirm with an account holder or HPC support before configuring credentials.

The [HPC-IIT-Delhi guide](https://github.com/kanha95/HPC-IIT-Delhi) describes an IITD certificate and a local `iitdproxy.py` login helper, followed by a numeric proxy IP. [HPC-101](https://github.com/Aries-IITD/HPC-101) describes a `proxy.sh` helper and proxy hostnames based on program codes. [HPC-Details](https://github.com/mahesh-keswani/HPC-Details) also contains proxy and network tips and was used as a source for the Pragya proxy investigation. This suggests some shared IITD proxy infrastructure, but does not establish which settings work on Padum. Address formats, program-code mapping, and current authentication flow need verification; see [open questions](08-open-questions.md).

Never paste a Kerberos password into a shared script, repository, or command history. Keep any credential file private (`chmod 600`) and follow current institute guidance. The source repositories explicitly warn against leaving passwords in scripts.

The Pragya proxy page documents a different set of direct tests; do not assume its host, performance, or compute-node behavior applies to Padum.
