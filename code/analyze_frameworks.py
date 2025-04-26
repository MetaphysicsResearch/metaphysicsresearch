import pandas as pd
import glob
import os
import sys
from collections import Counter
import re
import ast

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
    
    # Process each file
    for file_path in framework_files:
        try:
            print(f"Processing {file_path}")
            df = pd.read_csv(file_path, sep=';')  # Use semicolon as separator
            print(f"DataFrame shape: {df.shape}")
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    execution = row['Execution']
                    frameworks = row['Frameworks']
                    
                    lab_name = extract_lab_name(execution)
                    print(f"Lab name: {lab_name}")
                    
                    # Safely evaluate the string representation of list
                    frameworks_list = ast.literal_eval(frameworks)
                    print(f"Found frameworks: {frameworks_list}")
                    all_frameworks.extend(frameworks_list)
                    
                    # Add to lab-specific count
                    if lab_name not in lab_frameworks:
                        lab_frameworks[lab_name] = []
                    lab_frameworks[lab_name].extend(frameworks_list)
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
                
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
    
    lab_df = lab_df.reset_index().rename(columns={'index': 'Framework'})
    
    # Save results
    output_dir = directory
    overall_df.to_csv(os.path.join(output_dir, 'framework_overall_counts.csv'), index=False)
    lab_df.to_csv(os.path.join(output_dir, 'framework_lab_counts.csv'), index=False)
    
    print("\nResults summary:")
    print("\nOverall counts:")
    print(overall_df)
    print("\nLab-specific counts:")
    print(lab_df)
    
    print(f"\nResults saved to {output_dir}/framework_overall_counts.csv and {output_dir}/framework_lab_counts.csv")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_frameworks.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    process_frameworks_data(directory) 