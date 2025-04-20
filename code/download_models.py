import requests
import csv
from datetime import datetime

def download_models():
    # API endpoint
    url = "https://openrouter.ai/api/v1/models"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Prepare CSV file
        with open('models.csv', 'w', newline='') as csvfile:
            fieldnames = ['id', 'created_date', 'context_length', 'pricing_prompt', 
                         'pricing_request', 'max_completion_tokens', 'is_moderated']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Process each model
            for model in data.get('data', []):
                # Convert Unix timestamp to YYYYMMDD format
                created_date = datetime.fromtimestamp(model['created']).strftime('%Y%m%d')
                
                # Extract pricing information
                pricing = model.get('pricing', {})
                pricing_prompt = pricing.get('prompt', '0')
                pricing_request = pricing.get('request', '0')
                
                # Extract top provider information
                top_provider = model.get('top_provider', {})
                max_completion_tokens = top_provider.get('max_completion_tokens', '')
                is_moderated = top_provider.get('is_moderated', False)
                
                # Write row
                writer.writerow({
                    'id': model['id'],
                    'created_date': created_date,
                    'context_length': model.get('context_length', ''),
                    'pricing_prompt': pricing_prompt,
                    'pricing_request': pricing_request,
                    'max_completion_tokens': max_completion_tokens,
                    'is_moderated': is_moderated
                })
        
        print("Models data has been successfully downloaded and saved to models.csv")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading models data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_models() 