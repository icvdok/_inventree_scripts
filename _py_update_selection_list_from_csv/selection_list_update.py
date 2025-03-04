"""
This script is designed to interact with the InvenTree API to manage selection lists. 
It performs the following steps:

1. Load Environment Variables:
   - The script uses the `dotenv` library to load environment variables from a `.env` file. 
   - These variables include the InvenTree API URL (`BASE_URL`) and the API token (`INVENTREE_API_TOKEN`).

2. Define Headers for Authentication:
   - The script sets up the headers required for authentication with the InvenTree API using the API token.

3. Define Function to Get Existing Selection Lists:
   - The `get_selection_lists` function sends a GET request to the InvenTree API to retrieve existing selection lists.
   - If the request is successful (HTTP status code 200), it returns the response JSON containing the selection lists.
   - If the request fails, it prints an error message along with the response status code and JSON.

4. Define Function to Add Choices to an Existing Selection List:
   - The `add_choices_to_selection_list` function sends a GET request to the InvenTree API to retrieve the details of an existing selection list.
   - If the request is successful (HTTP status code 200), it retrieves the existing choices and updates them with the new choices.
   - It constructs the payload with the updated data and sends a PUT request to the `/api/selection/{selection_list_id}/` endpoint.
   - If the request is successful (HTTP status code 200), it prints a success message and returns the response JSON.
   - If the request fails, it prints an error message along with the response status code and JSON.

5. Get Existing Selection Lists:
   - The script calls the `get_selection_lists` function to retrieve existing selection lists.

6. Ask the User to Select a Selection List:
   - The script displays the existing selection lists and asks the user to select one.

7. Read New Choices from CSV File:
   - The script reads a CSV file named `selection_list.csv` containing the new choices for the selection list.
   - The CSV file is expected to have columns: `Value`, `Label`, and `Description`.
   - It reads each row from the CSV file and constructs a dictionary for each choice with the keys: `value`, `label`, `description`, and `active`.
   - These dictionaries are appended to a list of new choices.

8. Report What Will Be Added:
   - The script prints a summary of the new choices that will be added to the selected selection list.

9. Ask for User Confirmation:
   - The script asks the user to confirm whether they want to proceed with adding the new choices.
   - If the user confirms (inputs "yes"), the script calls the `add_choices_to_selection_list` function to add the new choices to the selected selection list.
   - If the user does not confirm (inputs anything other than "yes"), the script prints a message indicating that the operation is cancelled.

Overall, this script automates the process of managing selection lists in InvenTree, making it easier to add new choices to existing selection lists based on data from a CSV file.
"""
import csv
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve API details from environment variables
api_url = os.getenv('BASE_URL')
api_token = os.getenv('INVENTREE_API_TOKEN')

# Headers for authentication
headers = {
    'Authorization': f'Token {api_token}',
    'Content-Type': 'application/json'
}

# Function to get existing selection lists from InvenTree
def get_selection_lists():
    url = f'{api_url}selection/'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Failed to retrieve selection lists: {response.status_code}')
        print(response.json())
        return None

# Function to add choices to an existing selection list
def add_choices_to_selection_list(selection_list_id, choices):
    url = f'{api_url}selection/{selection_list_id}/'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        existing_list = response.json()
        existing_choices = existing_list.get('choices', [])
        updated_choices = existing_choices + choices
        
        payload = {
            'name': existing_list['name'],
            'description': existing_list['description'],
            'active': existing_list['active'],
            'choices': updated_choices
        }
        
        response = requests.put(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print('Choices added successfully!')
            return response.json()
        else:
            print(f'Failed to add choices: {response.status_code}')
            print(response.json())
            return None
    else:
        print(f'Failed to retrieve the selection list: {response.status_code}')
        print(response.json())
        return None

# Get existing selection lists
selection_lists = get_selection_lists()

if selection_lists:
    # Display the selection lists and ask the user to select one
    print("Existing selection lists:")
    for i, selection_list in enumerate(selection_lists):
        print(f"{i + 1}. {selection_list['name']}")

    selected_index = int(input("Select a selection list by number: ")) - 1
    selected_selection_list = selection_lists[selected_index]

    # Read the CSV file and prepare new choices
    csv_file = 'list.csv'
    new_choices = []

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            choice = {
                'value': row['Value'],
                'label': row['Label'],
                'description': row['Description'],
                'active': True
            }
            new_choices.append(choice)

    # Report what will be added
    print(f"\nThe script will add the following choices to the selection list '{selected_selection_list['name']}':\n")
    for choice in new_choices:
        print(f"  - Value: {choice['value']}, Label: {choice['label']}, Description: {choice['description']}")

    # Ask for confirmation
    confirmation = input("\nDo you want to proceed with adding these choices? (yes/no): ")

    if confirmation.lower() == 'yes':
        # Add choices to the selected selection list
        updated_selection_list = add_choices_to_selection_list(selected_selection_list['pk'], new_choices)
        print(updated_selection_list)
    else:
        print("Operation cancelled.")
else:
    print("No selection lists found.")