import os
import sys
import csv
import requests
from datetime import datetime
import re
from collections import defaultdict

def get_api_key():
    api_key = os.environ.get("OPR_APIKEY")
    if not api_key:
        raise ValueError("OPR_APIKEY environment variable not set")
    return api_key

def read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found")

def call_openrouter(prompt, model, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Framework Extractor"
    }
    data = {
        "model": model.strip(),
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        raise Exception(f"API error for model {model}: {str(e)}")
    except KeyError:
        raise Exception(f"Unexpected API response format for model {model}")

def extract_frameworks(response_text, api_key):
    # Read the prompt extract template
    prompt_template = read_file("prompt_extract.txt")
    
    # Combine template with response
    full_prompt = f"{prompt_template}\n{response_text}"
    
    # Call OpenRouter with grok-3-beta
    result = call_openrouter(full_prompt, "x-ai/grok-3-beta", api_key)
    
    # Extract JSON array from the result
    try:
        # Find the JSON array in the response
        start = result.find('[')
        end = result.rfind(']') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")
        frameworks = eval(result[start:end])  # Safe since we're only evaluating JSON array
        # Convert all framework names to lowercase
        frameworks = [f.lower() for f in frameworks]
        return frameworks
    except Exception as e:
        print(f"Error parsing frameworks from response: {str(e)}")
        return []

def extract_model_name(filename):
    # Remove the timestamp part (e.g., _20250416_115603)
    # The pattern matches _ followed by 8 digits, underscore, and 6 digits
    return re.sub(r'_\d{8}_\d{6}\.md$', '', filename)

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_frameworks.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    if not os.path.isdir(data_dir):
        print(f"Error: {data_dir} is not a valid directory")
        sys.exit(1)

    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    # Create output CSV files inside the data directory with _ prefix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frameworks_file = os.path.join(data_dir, f"_frameworks_{timestamp}.csv")
    stats_file = os.path.join(data_dir, f"_frameworks_stats_{timestamp}.csv")
    
    # Dictionary to store framework counts
    framework_counts = defaultdict(float)
    
    with open(frameworks_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(['Execution', 'Frameworks'])
        
        # Process each model response file
        for filename in os.listdir(data_dir):
            if not filename.endswith('.md') or filename.startswith('_'):
                continue
                
            try:
                # Read the model response
                file_path = os.path.join(data_dir, filename)
                response_text = read_file(file_path)
                
                # Extract frameworks
                frameworks = extract_frameworks(response_text, api_key)
                
                # Write to CSV
                writer.writerow([filename, frameworks])
                print(f"Processed {filename}")
                
                # Update framework counts with weighted values
                if frameworks:
                    weight = 1.0 / len(frameworks)
                    for framework in frameworks:
                        framework_counts[framework] += weight
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

    # Write framework statistics to CSV
    with open(stats_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(['Framework', 'Count'])
        # Sort frameworks by count in descending order
        for framework, count in sorted(framework_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([framework, count])

    print(f"\nResults saved to:")
    print(f"- Framework details: {frameworks_file}")
    print(f"- Framework statistics: {stats_file}")

if __name__ == "__main__":
    main() 