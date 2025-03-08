import requests
import json
import csv

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

# Load the CSV file from _data_files folder with UTF-8 encoding
file_path = '_data_files/locations.csv'
location_names = []

with open(file_path, mode='r', encoding='utf-8-sig') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        # Get the location name from the first column
        location_names.append(row[0])

# Function to get location ID by name
def get_location_id(location_name):
    url = f'{base_url}stock/location/'
    response = requests.get(url, headers=headers, params={'name': location_name})
    print(f'API Response for "{location_name}": {response.json()}')  # Print the API response
    if response.status_code == 200:
        locations = response.json()
        if locations:
            return locations[0]['pk']
    return None

# Set simulate to True to deactivate actual deletion
simulate = False

# Open the log file
with open('simulation_log.txt', mode='w') as log_file:
    # Delete each location by name
    for location_name in location_names:
        location_id = get_location_id(location_name)
        if location_id:
            if simulate:
                log_file.write(f'[SIMULATION] Location "{location_name}" would be deleted.\n')
                print(f'[SIMULATION] Location "{location_name}" would be deleted.')
            else:
                url = f'{base_url}stock/location/{location_id}/'
                response = requests.delete(url, headers=headers)
                if response.status_code == 204:
                    log_file.write(f'Location "{location_name}" deleted successfully.\n')
                    print(f'Location "{location_name}" deleted successfully.')
                else:
                    log_file.write(f'Failed to delete location "{location_name}". Status code: {response.status_code}\n')
                    log_file.write(f'{response.json()}\n')
                    print(f'Failed to delete location "{location_name}". Status code: {response.status_code}')
                    print(response.json())
        else:
            log_file.write(f'Location "{location_name}" not found.\n')
            print(f'Location "{location_name}" not found.')
