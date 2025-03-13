import csv
import requests
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Retrieve API details from environment variables
api_url = os.getenv('BASE_URL')
api_token = os.getenv('INVENTREE_API_TOKEN')

if not api_url or not api_token:
    logging.error("API URL or Token not found in environment variables.")
    exit(1)

# Ensure the API URL ends with a slash
if not api_url.endswith('/'):
    api_url += '/'

# Headers for authentication
headers = {
    'Authorization': f'Token {api_token}',
    'Content-Type': 'application/json'
}

# Function to create a part in InvenTree
def create_part(part_data):
    url = f'{api_url}part/'
    response = requests.post(url, headers=headers, json=part_data)
    
    if response.status_code == 201:
        logging.info(f'Part "{part_data["name"]}" created successfully!')
        return response.json()
    else:
        logging.error(f'Failed to create part "{part_data["name"]}": {response.status_code}')
        logging.error(response.json())
        return None

# Read the CSV file and prepare part data
csv_file = 'parts.csv'

try:
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        parts_to_create = []
        for row in csv_reader:
            try:
                part_data = {
                    'name': row['name'],
                    'minimum_stock': int(row['minimum_stock']),
                    'description': row['description'],
                    'category': int(row['category']),
                    'active': row['active'].lower() == 'true',
                    'component': row['component'].lower() == 'true',
                    'purchaseable': row['purchaseable'].lower() == 'true',
                    'copy_category_parameters': row['copy_category_parameters'].lower() == 'true',
                    'existing_image': row['existing_image'],
                    'supplier_pk': row['supplier_pk'],  # Add supplier primary key
                    'supplier_part_number': row['supplier_part_number'],  # Add supplier part number
                    'supplier_link': row['supplier_link'],  # Add supplier link
                    'supplier_pack_quantity': int(row['supplier_pack_quantity'])  # Add supplier pack quantity
                }
                parts_to_create.append(part_data)
            except KeyError as e:
                logging.error(f"Missing key in CSV file: {e}")

        # List all parts to be created
        logging.info("\nThe script will create the following parts:\n")
        for part in parts_to_create:
            logging.info(f"Name: {part['name']}")
            logging.info(f"Minimum Stock: {part['minimum_stock']}")
            logging.info(f"Description: {part['description']}")
            logging.info(f"Category: {part['category']}")
            logging.info(f"Active: {part['active']}")
            logging.info(f"Component: {part['component']}")
            logging.info(f"Purchaseable: {part['purchaseable']}")
            logging.info(f"Copy Category Parameters: {part['copy_category_parameters']}")
            logging.info(f"Existing Image: {part['existing_image']}")
            logging.info(f"Supplier PK: {part['supplier_pk']}")
            logging.info(f"Supplier Part Number: {part['supplier_part_number']}")
            logging.info(f"Supplier Link: {part['supplier_link']}")
            logging.info(f"Supplier Pack Quantity: {part['supplier_pack_quantity']}")
            logging.info("\n")

        # Ask for confirmation
        confirmation = input("\nDo you want to proceed with creating these parts? (yes/no): ")

        if confirmation.lower() == 'yes':
            for part in parts_to_create:
                create_part(part)
        else:
            logging.info("Operation cancelled.")
except FileNotFoundError:
    logging.error(f"CSV file '{csv_file}' not found.")