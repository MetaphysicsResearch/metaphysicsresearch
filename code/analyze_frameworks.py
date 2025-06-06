import pandas as pd
import glob
import os
import sys
from collections import Counter
import re
import ast

# Define the framework hierarchy with lowercase keys
FRAMEWORK_HIERARCHY = {
    # Physicalism
    'eliminative materialism': ('PHY', 'REP'),
    'identity theory': ('PHY', 'REP'),
    'illusionism': ('PHY', 'REP'),
    'reductive physicalism': ('PHY', 'REP'),
    'functionalism': ('PHY', 'NRP'),
    'non-reductive physicalism': ('PHY', 'NRP'),
    'physicalist emergentism': ('PHY', 'NRP'),
    
    # Monism Beyond Physicalism
    'analytic idealism': ('MBP', 'CFM'),
    'cosmopsychism': ('MBP', 'CFM'),
    'russellian panpsychism': ('MBP', 'CFM'),
    'dual-aspect monism': ('MBP', 'NAM'),
    'neutral monism': ('MBP', 'NAM'),
    
    # Relational and Process Ontologies
    'ontic structural realism': ('RPO', None),
    'relational quantum ontology': ('RPO', None),
    'whiteheadian process metaphysics': ('RPO', None),
    
    # Dualism
    'property dualism': ('DUA', None),
    'substance dualism': ('DUA', None)
}

# Define 3-letter codes for each framework
FRAMEWORK_CODES = {
    'eliminative materialism': 'elm',
    'identity theory': 'idt',
    'illusionism': 'ill',
    'reductive physicalism': 'rph',
    'functionalism': 'fun',
    'non-reductive physicalism': 'nrp',
    'physicalist emergentism': 'pem',
    'analytic idealism': 'aid',
    'cosmopsychism': 'cos',
    'russellian panpsychism': 'rpp',
    'dual-aspect monism': 'dam',
    'neutral monism': 'nem',
    'ontic structural realism': 'osr',
    'relational quantum ontology': 'rqo',
    'whiteheadian process metaphysics': 'wpm',
    'property dualism': 'pdu',
    'substance dualism': 'sdu'
}

def extract_lab_name(execution_str):
    """Extract lab name from execution string."""
    # Extract the part before the first underscore
    match = re.match(r'([a-z-]+)_', execution_str)
    if match:
        lab = match.group(1)
        # Clean up the lab name
        lab = lab.replace('-', ' ').title().replace(' ', '-')
        return lab
    return 'unknown'

def extract_model_name(execution_str):
    """Extract full model name from execution string."""
    # Extract everything before the timestamp (_YYYYMMDD_HHMMSS.md)
    match = re.match(r'(.+)_\d{8}_\d{6}\.md$', execution_str)
    if match:
        model = match.group(1)
        # Clean up the model name (replace _, title case, replace space with -)
        model = model.replace('_', '-') # Replace underscores first
        model = model.replace('-', ' ').title().replace(' ', '-') # Title case and hyphenate
        return model
    return 'unknown'

def process_frameworks_data(directory):
    # Find all framework files
    framework_files = glob.glob(os.path.join(directory, '_frameworks_*.csv'))
    
    if not framework_files:
        print(f"No framework files found in {directory}")
        sys.exit(1)
    
    print(f"Found {len(framework_files)} framework files")
    
    # Initialize data structures
    all_frameworks = []
    lab_frameworks = {}
    execution_data = {}  # New dictionary to store execution data
    
    # Process each file
    for file_path in sorted(framework_files):  # Sort files to ensure chronological order
        try:
            print(f"Processing {file_path}")
            df = pd.read_csv(file_path, sep=';')  # Use semicolon as separator
            print(f"DataFrame shape: {df.shape}")
            
            # Initialize frameworks for this execution
            execution_frameworks = {}
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    execution = row['Execution']
                    frameworks = row['Frameworks']
                    
                    model_name = extract_model_name(execution)
                    print(f"Model name: {model_name}")
                    
                    # Safely evaluate the string representation of list
                    frameworks_list = ast.literal_eval(frameworks)
                    print(f"Found frameworks: {frameworks_list}")
                    all_frameworks.extend(frameworks_list)
                    
                    # Add to lab-specific count
                    lab_name = extract_lab_name(execution)
                    if lab_name not in lab_frameworks:
                        lab_frameworks[lab_name] = []
                    lab_frameworks[lab_name].extend(frameworks_list)
                    
                    # Store frameworks for this model in this execution
                    if model_name not in execution_frameworks:
                        execution_frameworks[model_name] = set()
                    execution_frameworks[model_name].update(frameworks_list)
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
            
            # After processing all rows in the file, store the unique frameworks for each model
            for model_name, frameworks in execution_frameworks.items():
                if model_name not in execution_data:
                    execution_data[model_name] = []
                # Convert frameworks to 3-letter codes and sort them
                framework_codes = sorted([FRAMEWORK_CODES.get(f.lower(), f) for f in frameworks])
                execution_data[model_name].append(framework_codes)
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    if not all_frameworks:
        print("No frameworks were found in any file!")
        sys.exit(1)
    
    print(f"Total frameworks found: {len(all_frameworks)}")
    print(f"Unique frameworks: {set(all_frameworks)}")
    
    # Create overall framework counts
    framework_counts = Counter(all_frameworks)
    overall_df = pd.DataFrame({
        'Framework': list(framework_counts.keys()),
        'Count': list(framework_counts.values())
    })
    overall_df['Count%'] = (overall_df['Count'] / overall_df['Count'].sum() * 100).round(2)
    overall_df = overall_df.sort_values('Count', ascending=False)
    
    # Create lab-specific framework counts
    lab_data = {}
    for lab, frameworks in lab_frameworks.items():
        lab_data[lab] = Counter(frameworks)
    
    # Create a DataFrame with all frameworks and labs
    all_unique_frameworks = sorted(set(all_frameworks))
    lab_df = pd.DataFrame(index=all_unique_frameworks)
    
    for lab in lab_data:
        lab_df[lab] = [lab_data[lab].get(framework, 0) for framework in all_unique_frameworks]
    
    # Calculate percentages for each lab
    for lab in lab_data:
        total = lab_df[lab].sum()
        if total > 0:  # Avoid division by zero
            lab_df[f'{lab}_%'] = (lab_df[lab] / total * 100).round(2)
    
    lab_df = lab_df.reset_index().rename(columns={'index': 'Framework'})
    
    # Create cluster-based analysis
    cluster_data = {
        'Framework': [],
        'Cluster': [],
        'Subcluster': [],
        'Count': [],
        'Count%': []
    }
    
    # Add lab-specific columns
    for lab in lab_data:
        cluster_data[lab] = []
        cluster_data[f'{lab}_%'] = []
    
    # Process each framework
    unmatched_frameworks = []
    for framework in all_unique_frameworks:
        # Convert framework to lowercase for matching
        framework_lower = framework.lower()
        if framework_lower in FRAMEWORK_HIERARCHY:
            cluster, subcluster = FRAMEWORK_HIERARCHY[framework_lower]
            cluster_data['Framework'].append(framework)  # Keep original case for display
            cluster_data['Cluster'].append(cluster)
            cluster_data['Subcluster'].append(subcluster if subcluster else '')
            cluster_data['Count'].append(framework_counts[framework])
            cluster_data['Count%'].append(overall_df[overall_df['Framework'] == framework]['Count%'].iloc[0])
            
            # Add lab-specific data
            for lab in lab_data:
                count = lab_df[lab_df['Framework'] == framework][lab].iloc[0]
                cluster_data[lab].append(count)
                cluster_data[f'{lab}_%'].append(lab_df[lab_df['Framework'] == framework][f'{lab}_%'].iloc[0])
        else:
            unmatched_frameworks.append((framework, framework_counts[framework]))
    
    # Print unmatched frameworks
    if unmatched_frameworks:
        print("\nUnmatched frameworks (not in any cluster):")
        print("Framework\tCount")
        for framework, count in sorted(unmatched_frameworks, key=lambda x: x[1], reverse=True):
            print(f"{framework}\t{count}")
    
    # Create cluster DataFrame
    cluster_df = pd.DataFrame(cluster_data)
    
    # Define all possible clusters and subclusters
    ALL_CLUSTERS = ['PHY', 'MBP', 'RPO', 'DUA']
    ALL_SUBCLUSTERS = {
        'PHY': ['REP', 'NRP'],
        'MBP': ['CFM', 'NAM'],
        'RPO': [None],
        'DUA': [None]
    }
    
    # Add empty clusters and subclusters to cluster_totals
    for cluster in ALL_CLUSTERS:
        if cluster not in cluster_df['Cluster'].values:
            empty_row = {'Cluster': cluster, 'Count': 0}
            for lab in lab_data:
                empty_row[lab] = 0
            cluster_df = pd.concat([cluster_df, pd.DataFrame([empty_row])], ignore_index=True)
    
    # Add empty clusters and subclusters to subcluster_totals
    for cluster in ALL_CLUSTERS:
        for subcluster in ALL_SUBCLUSTERS[cluster]:
            if subcluster is None:
                subcluster = ''
            mask = (cluster_df['Cluster'] == cluster) & (cluster_df['Subcluster'] == subcluster)
            if not mask.any():
                empty_row = {'Cluster': cluster, 'Subcluster': subcluster, 'Count': 0}
                for lab in lab_data:
                    empty_row[lab] = 0
                cluster_df = pd.concat([cluster_df, pd.DataFrame([empty_row])], ignore_index=True)
    
    # Sort the DataFrames
    cluster_df = cluster_df.sort_values('Cluster')
    cluster_totals = cluster_df.groupby('Cluster').agg({
        'Count': 'sum',
        **{lab: 'sum' for lab in lab_data}
    }).reset_index()
    
    # Calculate subcluster totals
    subcluster_totals = cluster_df.groupby(['Cluster', 'Subcluster']).agg({
        'Count': 'sum',
        **{lab: 'sum' for lab in lab_data}
    }).reset_index()
    
    # Add Count% to cluster_totals
    total_count = cluster_totals['Count'].sum()
    cluster_totals['Count%'] = (cluster_totals['Count'] / total_count * 100).round(2)
    
    # Add Count% to subcluster_totals
    subcluster_totals['Count%'] = (subcluster_totals['Count'] / total_count * 100).round(2)
    
    # Print empty clusters and subclusters
    print("\nEmpty clusters and subclusters:")
    for cluster in ['PHY', 'MBP', 'RPO', 'DUA']:
        cluster_data = cluster_df[cluster_df['Cluster'] == cluster]
        if cluster_data.empty:
            print(f"Empty cluster: {cluster}")
        else:
            for subcluster in ['REP', 'NRP', 'CFM', 'NAM']:
                subcluster_data = cluster_data[cluster_data['Subcluster'] == subcluster]
                if subcluster_data.empty:
                    print(f"Empty subcluster: {cluster} -> {subcluster}")
    
    # Add totals to cluster_df
    # Row totals
    cluster_df['Total'] = cluster_df['Count']
    for lab in lab_data:
        cluster_df['Total'] += cluster_df[lab]
    
    # Column totals
    totals_row = pd.DataFrame([{
        'Framework': 'TOTAL',
        'Cluster': '',
        'Subcluster': '',
        'Count': cluster_df['Count'].sum(),
        'Count%': 100.0,
        **{lab: cluster_df[lab].sum() for lab in lab_data},
        **{f'{lab}_%': 100.0 for lab in lab_data},
        'Total': cluster_df['Total'].sum()
    }])
    cluster_df = pd.concat([cluster_df, totals_row], ignore_index=True)
    
    # Add totals to cluster_totals
    totals_row = pd.DataFrame([{
        'Cluster': 'TOTAL',
        'Count': cluster_totals['Count'].sum(),
        'Count%': 100.0,
        **{lab: cluster_totals[lab].sum() for lab in lab_data}
    }])
    cluster_totals = pd.concat([cluster_totals, totals_row], ignore_index=True)
    
    # Add totals to subcluster_totals
    totals_row = pd.DataFrame([{
        'Cluster': 'TOTAL',
        'Subcluster': '',
        'Count': subcluster_totals['Count'].sum(),
        'Count%': 100.0,
        **{lab: subcluster_totals[lab].sum() for lab in lab_data}
    }])
    subcluster_totals = pd.concat([subcluster_totals, totals_row], ignore_index=True)
    
    # Sort the DataFrames
    cluster_totals = cluster_totals.sort_values('Cluster')
    subcluster_totals = subcluster_totals.sort_values(['Cluster', 'Subcluster'])
    
    # Define output directory
    output_dir = directory
    
    # Create execution-based DataFrame
    num_executions = len(framework_files)  # Use number of files as number of executions
    execution_df = pd.DataFrame(columns=['AI Model'] + [f'Exec {i+1}' for i in range(num_executions)])
    
    for model in execution_data:
        row_data = {'AI Model': model}
        for i, frameworks in enumerate(execution_data[model]):
            row_data[f'Exec {i+1}'] = ', '.join(frameworks)
        execution_df = pd.concat([execution_df, pd.DataFrame([row_data])], ignore_index=True)
    
    # Create framework code mapping DataFrame
    code_mapping_df = pd.DataFrame({
        'Framework': list(FRAMEWORK_CODES.keys()),
        'Code': list(FRAMEWORK_CODES.values())
    })
    
    # Save all files
    overall_df.to_csv(os.path.join(output_dir, '_framework_overall_counts.csv'), index=False)
    lab_df.to_csv(os.path.join(output_dir, '_framework_lab_counts.csv'), index=False)
    cluster_df.to_csv(os.path.join(output_dir, '_framework_cluster_counts.csv'), index=False)
    cluster_totals.to_csv(os.path.join(output_dir, '_framework_cluster_totals.csv'), index=False)
    subcluster_totals.to_csv(os.path.join(output_dir, '_framework_subcluster_totals.csv'), index=False)
    execution_df.to_csv(os.path.join(output_dir, '_framework_executions.csv'), index=False)
    code_mapping_df.to_csv(os.path.join(output_dir, '_framework_codes.csv'), index=False)
    
    print("\nExecution-based counts:")
    print(execution_df)
    print("\nFramework code mapping:")
    print(code_mapping_df)
    
    print(f"\nResults saved to {output_dir}/_framework_*.csv files")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_frameworks.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    process_frameworks_data(directory) 