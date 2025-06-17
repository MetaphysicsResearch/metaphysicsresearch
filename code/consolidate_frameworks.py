import os
import glob
import pandas as pd
from datetime import datetime

def consolidate_frameworks(input_dir):
    # Find all _frameworks_*.csv files in the input directory
    framework_files = sorted(glob.glob(os.path.join(input_dir, '_frameworks_*.csv')))
    
    # Dictionary to store model -> {file: frameworks} mapping
    model_data = {}
    
    # Process each file
    for file_path in framework_files:
        # Get the base filename without path
        file_name = os.path.basename(file_path)
        
        # Read the CSV file
        df = pd.read_csv(file_path, sep=';')
        
        # Process each row
        for _, row in df.iterrows():
            # Extract model name from execution (remove timestamp and .md)
            execution = row['Execution']
            model = '_'.join(execution.split('_')[:-2])
            
            # Convert frameworks string to list
            frameworks = eval(row['Frameworks'])
            
            # Initialize model entry if not exists
            if model not in model_data:
                model_data[model] = {}
            
            # Store frameworks for this file
            model_data[model][file_name] = frameworks
    
    # Create output DataFrame
    output_data = []
    for model, file_frameworks in model_data.items():
        row_data = {'Model': model}
        # Add frameworks from each file as separate columns
        for file_name in framework_files:
            base_file = os.path.basename(file_name)
            row_data[base_file] = file_frameworks.get(base_file, [])
        output_data.append(row_data)
    
    # Create DataFrame and sort by model name
    output_df = pd.DataFrame(output_data)
    output_df = output_df.sort_values('Model')
    
    # Generate output filename with current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(input_dir, f'_table_{timestamp}.csv')
    
    # Save to CSV with tab separator
    output_df.to_csv(output_file, sep=';', index=False)
    print(f"Consolidated data saved to: {output_file}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python consolidate_frameworks.py <input_directory>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    consolidate_frameworks(input_dir) 