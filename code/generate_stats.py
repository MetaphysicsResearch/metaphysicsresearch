import os
import sys
import csv
from collections import defaultdict
from datetime import datetime

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_stats.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    if not os.path.isdir(data_dir):
        print(f"Error: {data_dir} is not a valid directory")
        sys.exit(1)

    # Find the most recent frameworks CSV file
    frameworks_files = [f for f in os.listdir(data_dir) if f.startswith('_frameworks_') and f.endswith('.csv')]
    if not frameworks_files:
        print("Error: No frameworks CSV file found in the directory")
        sys.exit(1)
    
    # Get the most recent file
    latest_file = max(frameworks_files, key=lambda x: os.path.getmtime(os.path.join(data_dir, x)))
    frameworks_file = os.path.join(data_dir, latest_file)
    
    # Dictionary to store framework counts
    framework_counts = defaultdict(float)
    
    # Read the frameworks CSV and calculate statistics
    with open(frameworks_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        next(reader)  # Skip header row
        
        for row in reader:
            if len(row) < 2:
                continue
                
            frameworks = eval(row[1])  # Convert string representation of list back to list
            if frameworks:
                weight = 1.0 / len(frameworks)
                for framework in frameworks:
                    framework_counts[framework] += weight

    # Create output CSV file for statistics
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_file = os.path.join(data_dir, f"_frameworks_stats_{timestamp}.csv")
    
    # Write framework statistics to CSV
    with open(stats_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(['Framework', 'Count'])
        # Sort frameworks by count in descending order
        for framework, count in sorted(framework_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([framework, count])

    print(f"\nStatistics saved to: {stats_file}")

if __name__ == "__main__":
    main() 