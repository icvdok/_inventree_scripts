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

# Function to get all locations
def get_all_locations():
    url = f'{base_url}stock/location/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

# Function to find the highest progressive number
def find_highest_progressive_number(locations):
    highest_number = 0
    for location in locations:
        name = location['name']
        if name.startswith('gb_'):
            try:
                number = int(name.split('_')[1])
                if number > highest_number:
                    highest_number = number
            except ValueError:
                continue
    return highest_number

# Function to get location ID by name
def get_location_id_by_name(location_name):
    url = f'{base_url}stock/location/'
    response = requests.get(url, headers=headers, params={'name': location_name})
    if response.status_code == 200:
        locations = response.json()
        if locations:
            return locations[0]['pk']
    return None

# Function to create a new location with the next available number
def create_new_location(next_number, parent_location_id, simulate):
    new_location_name = f'gb_{next_number}'
    description = 'gridfinity_bin'
    location_type_index = 4  # Use the pk for '_gridfinity_bin'
    if simulate:
        print(f'[SIMULATION] New location "{new_location_name}" with description "{description}" and location type index "{location_type_index}" would be created under parent location ID {parent_location_id}.')
    else:
        url = f'{base_url}stock/location/'
        data = {
            'name': new_location_name,
            'description': description,
            'parent': parent_location_id,
            'location_type': location_type_index  # Updated field name
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f'New location "{new_location_name}" with description "{description}" and location type index "{location_type_index}" created successfully under parent location ID {parent_location_id}.')
        else:
            print(f'Failed to create new location. Status code: {response.status_code}')
            print(response.json())

# Prompt the user to enter the number of new locations to create
num_new_locations = int(input('Enter the number of new locations to create: '))

# Prompt the user to enter the parent location name
parent_location_name = input('Enter the parent location name: ')

# Prompt the user to enter whether to run in simulation mode
simulate_input = input('Run in simulation mode? (yes/no): ').strip().lower()
simulate = simulate_input == 'yes'

# Get all locations
locations = get_all_locations()

# Find the highest progressive number
highest_number = find_highest_progressive_number(locations)

# Get the parent location ID by name
parent_location_id = get_location_id_by_name(parent_location_name)

if parent_location_id:
    # Create the specified number of new locations
    for i in range(1, num_new_locations + 1):
        create_new_location(highest_number + i, parent_location_id, simulate)
else:
    print(f'Parent location "{parent_location_name}" not found.')