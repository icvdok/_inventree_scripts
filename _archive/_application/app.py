from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

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
        return {
            'simulation': True,
            'message': f'New location "{new_location_name}" with description "{description}" and location type index "{location_type_index}" would be created under parent location ID {parent_location_id}.'
        }
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
            return {
                'simulation': False,
                'message': f'New location "{new_location_name}" with description "{description}" and location type index "{location_type_index}" created successfully under parent location ID {parent_location_id}.'
            }
        else:
            return {
                'simulation': False,
                'message': f'Failed to create new location. Status code: {response.status_code}',
                'details': response.json()
            }

@app.route('/create_locations', methods=['POST'])
def create_locations():
    data = request.json
    num_new_locations = data.get('num_new_locations')
    parent_location_name = data.get('parent_location_name')
    simulate = data.get('simulate', False)

    # Get all locations
    locations = get_all_locations()

    # Find the highest progressive number
    highest_number = find_highest_progressive_number(locations)

    # Get the parent location ID by name
    parent_location_id = get_location_id_by_name(parent_location_name)

    if parent_location_id:
        results = []
        # Create the specified number of new locations
        for i in range(1, num_new_locations + 1):
            result = create_new_location(highest_number + i, parent_location_id, simulate)
            results.append(result)
        return jsonify(results)
    else:
        return jsonify({'error': f'Parent location "{parent_location_name}" not found.'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)