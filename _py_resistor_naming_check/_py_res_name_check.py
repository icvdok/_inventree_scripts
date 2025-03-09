import csv
import logging
import re
import requests
from inventree.api import InvenTreeAPI
from inventree.part import Part
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Retrieve API details from environment variables
api_url = os.getenv('BASE_URL')
token = os.getenv('INVENTREE_API_TOKEN')

if not token:
    raise ValueError("API token not found in secrets file.")

# Headers for authentication
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

# Initialize the InvenTree API
api = InvenTreeAPI(api_url, token=token)

def check_file_accessibility(file_path):
    """
    Checks if the file is accessible for writing.
    """
    try:
        with open(file_path, 'w') as file:
            pass
    except PermissionError:
        logging.error(f"Permission denied: {file_path}. Please close the file if it is open and try again.")
        return False
    return True

def get_parts_in_category(api, category_pk):
    """
    Retrieves all parts in the specified category.
    """
    logging.info(f"Retrieving parts in category {category_pk}")
    parts = Part.list(api, category=category_pk)
    logging.info(f"Retrieved {len(parts)} parts")
    return parts

def export_parts_to_csv(parts, file_path):
    """
    Exports the parts to a CSV file with columns: pk, name, description.
    """
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['pk', 'name', 'description','new_name'])
        for part in parts:
            writer.writerow([part.pk, part.name, part.description])
    logging.info(f"Parts exported to {file_path}")

def get_selection_choices(api_url, headers, selection_list_pk):
    """
    Function to get choices from a specific selection list in InvenTree.
    """
    url = f'{api_url}selection/{selection_list_pk}/'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('choices', [])
    else:
        logging.error(f'Failed to retrieve selection choices: {response.status_code}')
        return []

def check_naming_convention(part_name, api_url, headers):
    """
    Checks if the part name follows the specified naming convention.
    Rules:
    1. Part name should start with 'R_'.
    2. The second segment should be a valid resistance value (e.g., 10k, 1M, 470).
    3. The third segment should be a valid resistor type (e.g., MF, CF, WW, MO).
    4. The fourth segment should be a valid mounting type (e.g., SMD, TH).
    """
    # Split the part name by underscore
    parts = part_name.split('_')
    
    # Log all split parts of the name
    logging.info(f"Split parts of '{part_name}': {parts}")
    
    # Check 1: Part name should start with 'R_'
    check1 = parts[0] == 'R'
    
    # Check 2: The second segment should be a valid resistance value
    resistance_pattern = re.compile(r'^\d+(\.\d+)?(ROhm|kOhm|MOhm|mOhm)$')
    second_segment = parts[1]
    check2 = bool(resistance_pattern.match(second_segment))
    logging.info(f"Check 2 result: {check2}")

    # Check 3: The third segment should be a valid resistor type
    selection_list_pk_type = 15  # Assuming pk=15 for resistor types
    choices_type = get_selection_choices(api_url, headers, selection_list_pk_type)
    #logging.info(f"Choices for resistor types: {[choice['value'] for choice in choices_type]}")
    check3 = len(parts) > 2 and parts[2] in [choice['value'] for choice in choices_type]
    
    # Check 4: The fourth segment should be a valid mounting type
    selection_list_pk_mounting = 17  # Assuming pk=17 for mounting types
    choices_mounting = get_selection_choices(api_url, headers, selection_list_pk_mounting)
    check4 = len(parts) > 3 and parts[3] in [choice['value'] for choice in choices_mounting]
    
    # Log the results of each check
    logging.info(f"Check results for '{part_name}': {[check1, check2, check3, check4]}")
    
    # If all checks are true, the part name is compliant
    if check1 and check2 and check3 and check4:
        return True
    else:
        return False

def main(api, category_pk, csv_file_path):
    """
    Main function to export parts to a CSV file.
    """
    # Check if the file is accessible
    if not check_file_accessibility(csv_file_path):
        return
    
    # Empty the previous CSV file if it exists
    if os.path.exists(csv_file_path):
        open(csv_file_path, 'w').close()
    
    mode = input("Select execution mode (1: all parts export, 2: parts not in line with the naming convention): ")
    
    parts = get_parts_in_category(api, category_pk)
    
    if mode == '1':
        export_parts_to_csv(parts, csv_file_path)
    elif mode == '2':
        parts_to_export = [part for part in parts if not check_naming_convention(part.name, api_url, headers)]
        export_parts_to_csv(parts_to_export, csv_file_path)
    else:
        logging.error("Invalid mode selected. Please select either 1 or 2.")

if __name__ == "__main__":
    category_pk = 81
    csv_file_path = 'resistor_update.csv'
    main(api, category_pk, csv_file_path)