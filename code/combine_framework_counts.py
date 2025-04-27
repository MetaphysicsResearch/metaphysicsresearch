import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('data/_framework_overall_counts.csv')

# Split the data into separate dataframes based on the 'Framework' column
# We'll look for rows where 'Framework' appears to identify the start of each table
tables = []
current_table = []
for _, row in df.iterrows():
    if row['Framework'] == 'Framework':
        if current_table:
            tables.append(pd.DataFrame(current_table))
        current_table = []
    else:
        current_table.append(row)
if current_table:
    tables.append(pd.DataFrame(current_table))

# Create a new dataframe with all unique frameworks
all_frameworks = set()
for table in tables:
    all_frameworks.update(table['Framework'].str.strip().unique())

# Create a new dataframe with all frameworks
combined_df = pd.DataFrame({'Framework': sorted(list(all_frameworks))})

# Add count columns for each prompt
for i, table in enumerate(tables, 1):
    # Clean up the framework names by stripping whitespace
    table['Framework'] = table['Framework'].str.strip()
    # Create a mapping of framework to count
    counts = dict(zip(table['Framework'], table['Count']))
    # Add the counts to the combined dataframe
    combined_df[f'Prompt{i}'] = combined_df['Framework'].map(counts)

# Replace NaN with 0
combined_df = combined_df.fillna(0)

# Convert count columns to integers
for col in combined_df.columns[1:]:
    combined_df[col] = combined_df[col].astype(int)

# Save the combined dataframe to a new CSV file
combined_df.to_csv('data/combined_framework_counts.csv', index=False)

print("Combined CSV file has been created successfully!") 