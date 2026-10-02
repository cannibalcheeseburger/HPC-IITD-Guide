import json
import sys
import os
import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
import uuid
from collections import defaultdict

# --- CONFIGURATION ---
# I have added the new node types based on the test_pbs.json file provided.
# This is the only section you need to edit if you add new hardware in the future.
# 'hostname_prefix': 'desired_node_type_name'
NODE_TYPE_MAPPING = {
    # GPU Nodes
    'scai': 'amd_epyc_gpu',
    'aice': 'icelake_a100_gpu',
    'vsky': 'skylake_v100_gpu',
    'khas': 'haswell_k40_gpu',

    # CPU Nodes
    'cice': 'icelake_cpu',
    'csky': 'skylake_cpu',
    'chas': 'haswell_cpu',
    'cgen': 'amd_genoa_cpu',

    # Special Nodes (can be identified by full hostname if needed)
    'amd001': 'amd_large_mem_cpu'
}


def classify_nodes(data, mapping):
    """
    Groups nodes by type based on the hostname prefix in their 'Mom' field.

    Args:
        data (dict): The full JSON data from pbsnodes.
        mapping (dict): The NODE_TYPE_MAPPING dictionary.

    Returns:
        dict: A dictionary where keys are node types and values are
              data structures containing only the nodes of that type.
    """
    nodes_by_type = defaultdict(lambda: {'nodes': {}})
    for node_name, node_details in data.get('nodes', {}).items():
        mom = node_details.get('Mom')
        if not mom:
            continue

        # Find which category this node belongs to
        for prefix, node_type in mapping.items():
            if prefix in mom:
                nodes_by_type[node_type]['nodes'][node_name] = node_details
                break # Move to the next node once classified

    return nodes_by_type

def process_node(node, node_data):
    """
    Processes a single node to extract job information.
    The node_type is no longer needed as an argument because nodes are pre-filtered.
    """
    detail = node_data['nodes'][node]

    # Use the first three letters of the Mom name as a prefix for temp files
    # This avoids needing to pass the node_type down.
    prefix = detail['Mom'][:3]

    if 'state' in detail and 'down' in detail['state'] or 'offline' in detail['state']:
        return None

    try:
        jobs = detail['jobs']
    except KeyError:
        # Node is free or has no jobs listed, which is fine.
        return None

    results = []
    for job in jobs:
        unique_id = str(uuid.uuid4())
        filename = f"{prefix}_{unique_id}.json"

        # Run qstat to get job details in JSON format
        os.system(f"qstat -f {job} -F json > {filename}")

        try:
            with open(filename, 'r') as f:
                # Handle potentially empty files if qstat fails
                content = f.read()
                if not content:
                    continue
                A = json.loads(content)

            # Ensure the job details are actually in the JSON output
            if 'Jobs' not in A or job not in A['Jobs']:
                continue

            job_details = A['Jobs'][job]

            try:
                # Not all jobs will request GPUs, so handle this gracefully
                gpu_count = int(job_details.get('Resource_List', {}).get('ngpus', 0))
                cpu_count = int(job_details.get('Resource_List', {}).get('ncpus', 0))
                walltime = job_details.get('Resource_List', {}).get('walltime', '00:00:00')

                results.append({
                    'Job ID': job,
                    'Node': detail['Mom'].split('.')[0],
                    'Owner': job_details.get('Job_Owner', 'N/A').split('@')[0],
                    'StartTime': job_details.get('stime', 'N/A'),
                    'EndTime': walltime,
                    'Resources (cpu, gpu)': (cpu_count, gpu_count)
                })
            except (KeyError, ValueError) as e:
                # This catches errors if Resource_List or other keys are missing
                print(f"Skipping job {job} due to missing or invalid key: {e}")
                continue

        except json.JSONDecodeError:
            print(f"Error decoding JSON for job {job} in file {filename}")
        finally:
            # Always attempt to remove the temporary file
            if os.path.exists(filename):
                os.remove(filename)

    return results

def process_node_type(node_type, type_specific_data):
    """
    Processes all nodes of a specific type.
    """
    with Pool(cpu_count()) as pool:
        # Use partial to pass the pre-filtered data for this specific node type
        results = pool.map(partial(process_node, node_data=type_specific_data), type_specific_data['nodes'].keys())

    # Flatten the list of lists and remove None entries
    results = [item for sublist in results if sublist is not None for item in sublist]

    print(f'--- REPORT FOR {node_type.upper()} NODES ---')
    if not results:
        print('No running jobs found on this node type.')
        print('-' * 40)
        return None

    df = pd.DataFrame(results)

    # Gracefully handle jobs without a start time
    df_with_time = df[df['StartTime'] != 'N/A'].copy()
    if not df_with_time.empty:
        df_with_time['endDate'] = pd.to_datetime(df_with_time['StartTime']) + pd.to_timedelta(df_with_time['EndTime'])
        sorted_df = df_with_time.sort_values('endDate').drop_duplicates('Job ID').reset_index(drop=True)
    else:
        sorted_df = df # Fallback to unsorted if no start times are available

    print(f'Jobs Ending Soonest:')
    print(sorted_df.head(10).to_string())
    print()

    U2G = defaultdict(int)
    for _, row in sorted_df.iterrows():
        try:
            _, G = row['Resources (cpu, gpu)']
            usr = row['Owner']
            if int(G) > 0:
                U2G[usr] += int(G)
        except (ValueError, TypeError):
            continue

    print(f'GPU Usage Summary:')
    if U2G:
        for user, gpus in sorted(U2G.items()):
            print(f"- {user}: {gpus} GPUs")
    else:
        print("- No users are currently using GPUs on these nodes.")
    print('-' * 40)
    print()

    return sorted_df

def print_available_resources(data):
    """
    Prints nodes that are free and have available GPUs.
    """
    print('--- AVAILABLE FREE RESOURCES ---')
    found_free = False
    for node, detail in data.get('nodes', {}).items():
        if 'resources_available' in detail and detail.get('state') == 'free':
            # Check for GPUs first
            avail_gpus = int(detail['resources_available'].get('ngpus', 0))
            assigned_gpus = int(detail.get('resources_assigned', {}).get('ngpus', 0))
            free_gpus = avail_gpus - assigned_gpus

            # Also check for CPUs
            avail_cpus = int(detail['resources_available'].get('ncpus', 0))
            assigned_cpus = int(detail.get('resources_assigned', {}).get('ncpus', 0))
            free_cpus = avail_cpus - assigned_cpus

            if free_cpus > 0:
                found_free = True
                print(f"Node: {detail.get('Mom', node)}")
                print(f"  State: {detail.get('state')}")
                print(f"  CPU available: {free_cpus}")
                if avail_gpus > 0:
                    print(f"  GPU available: {free_gpus}")
                print()

    if not found_free:
        print("No nodes are currently in a 'free' state with available resources.")
    print('-' * 40)
    print()


if __name__ == '__main__':
    try:
        with open('./test_pbs.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: 'test_pbs.json' not found. Please run 'check_free_nodes.sh' first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode 'test_pbs.json'. The file might be corrupted or empty.")
        sys.exit(1)

    # Print a summary of free nodes first
    print_available_resources(data)

    # Dynamically classify all nodes based on the mapping
    classified_data = classify_nodes(data, NODE_TYPE_MAPPING)

    if not classified_data:
        print("Could not classify any nodes based on the provided NODE_TYPE_MAPPING.")
        print("Please check the hostnames in 'test_pbs.json' and update the mapping in the script.")
    else:
        # Process each discovered node type
        for node_type, type_specific_data in sorted(classified_data.items()):
            process_node_type(node_type, type_specific_data)
