import requests
import json

# Load the API token from the secrets.json file
with open('secrets.json') as f:
    secrets = json.load(f)
    api_token = secrets.get('INVENTREE_API_TOKEN')

# Replace this with your InvenTree server URL
base_url = 'https://inventory.cortinet.ch/api/'

# Set up the headers with your API token
headers = {
    'Authorization': f'Token {api_token}',
    'Content-Type': 'application/json'
}

# Function to get all stock location types
def get_stock_location_types():
    url = f'{base_url}stock/location-type/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

# Get all stock location types
location_types = get_stock_location_types()

print('Stock Location Types:', location_types)