import os
import sys
import requests
from datetime import datetime
import shutil
import re


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


def call_openrouter(messages, model, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",  # Required by OpenRouter
        "X-Title": "Prompt Executor"
    }
    data = {
        "model": model.strip(),
        "messages": messages,
        "temperature": 0
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    choice = response.json()['choices'][0]['message']
    return choice['content'], choice['role']


def parse_prompts(prompt_content):
    # Split content into individual prompts
    prompt_pattern = r'PROMPT_(\d+):(.*?)(?=PROMPT_\d+:|$)'
    prompts = re.findall(prompt_pattern, prompt_content, re.DOTALL)
    return [(int(num), content.strip()) for num, content in prompts]


def main():
    if len(sys.argv) != 3:
        print("Usage: python execute_prompt.py <prompt_file> <models_file>")
        sys.exit(1)

    prompt_file = sys.argv[1]
    models_file = sys.argv[2]

    # Read input files
    prompt_content = read_file(prompt_file)
    prompts = parse_prompts(prompt_content)
    if not prompts:
        raise ValueError("No prompts found in the input file. Each prompt should start with PROMPT_n:")
    models = [m.strip() for m in read_file(models_file).splitlines() if m.strip() and not m.strip().startswith("#")]

    # Prepare output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"data/data_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    shutil.copy(prompt_file, os.path.join(output_dir, f"_prompt.txt"))
    shutil.copy(models_file, os.path.join(output_dir, f"_models.conf"))

    api_key = get_api_key()

    # For each model, maintain a full conversation history
    for model in models:
        print(f"\n=== Running prompts with model: {model} ===")
        # Initialize context/messages list
        messages = []

        for prompt_num, prompt in prompts:
            print(f"Processing PROMPT_{prompt_num}...")
            # Append user prompt to context
            messages.append({"role": "user", "content": prompt})

            try:
                # Call OpenRouter API with full thread
                response_content, role = call_openrouter(messages, model, api_key)
                # Append assistant response to context
                messages.append({"role": role, "content": response_content})

                # Write output to file
                safe_model = model.replace('/', '_').replace(':', '_')
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                outfile = os.path.join(
                    output_dir,
                    f"PROMPT_{prompt_num}_{safe_model}_{ts}.md"
                )
                write_file(outfile, response_content)
                print(f"Saved: {outfile}")

            except Exception as e:
                print(f"Error on PROMPT_{prompt_num} with {model}: {e}")

if __name__ == "__main__":
    main()
