# Original Padum availability project

Imported from the user-owned `~/HPC-availibility` on 2026-10-02. These files preserve the original implementation for reference; use `bash check_free_nodes.sh` from the repository root for the maintained report. The archived wrapper writes files in its current directory and the archived Python script queries individual jobs. Hardware labels are inherited, unverified claims.

## Original usage notes

# Usage:
- `Requirements: python3, pandas`
- `bash check_free_nodes.sh`
- The following content will be printed:
    - for all nodes in HPC if resource available:
        - `Node name`:
            - `Num. CPU cores available`
            - `Num. GPU available`
    - For AMD and Icelake Nodes:
        - Top 10 jobs will be listed sorted by end-time in ascending order with following keys
        - `Job ID -- Node Name -- Owner -- Job Start Time -- Total Requested Time -- Resources Allocated -- End Timestamp`
