"""
This script is designed to create a selection list with choices in InvenTree using the InvenTree API. 
It performs the following steps:

1. Load Environment Variables:
   - The script uses the `dotenv` library to load environment variables from a `.env` file. 
   - These variables include the InvenTree API URL (`BASE_URL`) and the API token (`INVENTREE_API_TOKEN`).

2. Define Headers for Authentication:
   - The script sets up the headers required for authentication with the InvenTree API using the API token.

3. Define Function to Create a Selection List with Choices:
   - The `create_selection_list_with_choices` function sends a POST request to the InvenTree API to create a selection list along with its choices.
   - The function takes the selection list name, description, and a list of choices as input.
   - It constructs the payload with the provided data and sends the request to the `/api/selection/` endpoint.
   - If the request is successful (HTTP status code 201), it prints a success message and returns the response JSON.
   - If the request fails, it prints an error message along with the response status code and JSON.

4. Prompt User for Selection List Details:
   - The script prompts the user to enter the name and description of the selection list.

5. Read Choices from CSV File:
   - The script reads a CSV file named `selection_list.csv` containing the choices for the selection list.
   - The CSV file is expected to have columns: `Value`, `Label`, and `Description`.
   - It reads each row from the CSV file and constructs a dictionary for each choice with the keys: `value`, `label`, `description`, and `active`.
   - These dictionaries are appended to a list of choices.

6. Report What Will Be Created:
   - The script prints a summary of the selection list and its choices that will be created.
   - This includes the name, description, and details of each choice.

7. Ask for User Confirmation:
   - The script prompts the user to confirm whether they want to proceed with creating the selection list.
   - If the user confirms (inputs "yes"), the script calls the `create_selection_list_with_choices` function to create the selection list with the choices.
   - If the user does not confirm (inputs anything other than "yes"), the script prints a message indicating that the operation is cancelled.

Overall, this script automates the process of creating a selection list with choices in InvenTree, making it easier to manage and update selection lists based on data from a CSV file.
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

# Function to create a selection list with choices
def create_selection_list_with_choices(name, description, choices):
    url = f'{api_url}selection/'
    payload = {
        'name': name,
        'description': description,
        'active': True,
        'choices': choices
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print('Selection list created successfully with choices!')
        return response.json()
    else:
        print(f'Failed to create selection list: {response.status_code}')
        print(response.json())
        return None

# Prompt user for the selection list name and description
selection_list_name = input("Enter the name of the selection list: ")
selection_list_description = input("Enter the description of the selection list: ")

# Read the CSV file and prepare choices
csv_file = 'selection_list.csv'
choices = []

with open(csv_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        choice = {
            'value': row['Value'],
            'label': row['Label'],
            'description': row['Description'],
            'active': True
        }
        choices.append(choice)

# Report what will be created
print(f"\nThe script will create the following selection list:\n")
print(f"Name: {selection_list_name}")
print(f"Description: {selection_list_description}")
print(f"Choices:")
for choice in choices:
    print(f"  - Value: {choice['value']}, Label: {choice['label']}, Description: {choice['description']}")

# Ask for confirmation
confirmation = input("\nDo you want to proceed with creating this selection list? (yes/no): ")

if confirmation.lower() == 'yes':
    # Create the selection list with choices
    selection_list = create_selection_list_with_choices(selection_list_name, selection_list_description, choices)
    print(selection_list)
else:
    print("Operation cancelled.")