import os
import sys
import requests
from datetime import datetime
import shutil

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

def write_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

def call_openrouter(prompt, model, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",  # Required by OpenRouter
        "X-Title": "Prompt Executor"  # Optional, for OpenRouter analytics
    }
    data = {
        "model": model.strip(),
        "messages": [{"role": "user", "content": prompt}],
        # "temperature": 0 # Lets use OpenRouter default 1 instead of 0
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        raise Exception(f"API error for model {model}: {str(e)}")
    except KeyError:
        raise Exception(f"Unexpected API response format for model {model}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python execute_prompt.py <prompt_file> <models_file>")
        sys.exit(1)

    prompt_file = sys.argv[1]
    models_file = sys.argv[2]
    
    # Read input files
    try:
        prompt = read_file(prompt_file)
        models = read_file(models_file).strip().split('\n')
    except Exception as e:
        print(f"Error reading input files: {str(e)}")
        sys.exit(1)
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"data/data{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy input files to output directory
    try:
        shutil.copy(prompt_file, os.path.join(output_dir, f"_prompt.txt"))
        shutil.copy(models_file, os.path.join(output_dir, f"_models.conf"))
    except Exception as e:
        print(f"Error copying input files: {str(e)}")
        sys.exit(1)
    
    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    
    # Process each model
    for model in models:
        model = model.strip()
        if not model or model.startswith("#"):
            continue
            
        try:
            # Call OpenRouter API
            result = call_openrouter(prompt, model, api_key)
            
            # Generate output filename
            model_safe = model.replace('/', '_').replace(':', '_')
            timestamp_fine = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"{model_safe}_{timestamp_fine}.md")
            
            # Save result
            write_file(output_file, result)
            print(f"Saved result for {model} to {output_file}")
            
        except Exception as e:
            print(f"Error processing {model}: {str(e)}")
            continue

if __name__ == "__main__":
    main()