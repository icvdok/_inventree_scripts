import pandas as pd
import requests
from inventree.api import InvenTreeAPI
from inventree.part import Part
from inventree.company import SupplierPart
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Retrieve API details from environment variables
url = os.getenv('BASE_URL')
token = os.getenv('INVENTREE_API_TOKEN')

if not token:
    raise ValueError("API token not found in secrets file.")

# Initialize the InvenTree API
api = InvenTreeAPI(url, token=token)

def collect_info_from_csv(file_path):
    """
    Reads the CSV file and returns a DataFrame with the part information.
    """
    logging.info("Reading CSV file")
    df = pd.read_csv(file_path)
    df = df.fillna('').infer_objects(copy=False)
    logging.info("CSV file read successfully")
    return df

def match_inventree_parts(api, name):
    """
    Searches for a part in InvenTree with the given name.
    Returns the part if found, otherwise returns None.
    """
    logging.info(f"Searching for part with name: {name}")
    parts = Part.list(api, name=name)
    for part in parts:
        if part.name == name:
            logging.info(f"Part found: {part.name} (ID: {part.pk})")
            return part
    logging.info("No matching part found")
    return None

def update_part_information(part, part_data):
    """
    Updates the part information with the provided data.
    Returns the updated part if successful, otherwise returns None.
    """
    try:
        part.save(part_data)
        logging.info(f"Updated part: {part.name} - {part.pk}")
        return part
    except Exception as e:
        logging.error(f"Error updating part: {e}")
        return None

def update_supplier_information(api, part, supplier_data):
    """
    Updates or creates the supplier information for the given part.
    Returns the supplier part if successful, otherwise returns None.
    """
    try:
        supplier_parts = SupplierPart.list(api, part=part.pk, supplier=supplier_data['supplier'])
        if supplier_parts:
            supplier_part = supplier_parts[0]
            supplier_part.save(supplier_data)
            logging.info(f"Updated supplier part: {supplier_part.SKU} for part: {part.name}")
        else:
            supplier_part = SupplierPart.create(api, supplier_data)
            logging.info(f"Added supplier part: {supplier_part.SKU} for part: {part.name}")
        return supplier_part
    except Exception as e:
        logging.error(f"Error updating supplier part: {e}")
        return None

def main(csv_file_path, api, api_url, token):
    """
    Main function to update parts and supplier information based on the CSV file.
    """
    logging.info("Starting the update process")
    parts_info = collect_info_from_csv(csv_file_path)
    
    parts_to_update = []
    for index, row in parts_info.iterrows():
        if not row['name']:
            logging.error(f"Invalid part name at row {index}")
            continue
        
        part = match_inventree_parts(api, row['name'])
        
        if part:
            parts_to_update.append((part, row))
    
    if parts_to_update:
        print("The following parts will be updated:")
        for part, row in parts_to_update:
            print(f"- {part.name} (ID: {part.pk})")
        
        # Ask for confirmation once before updating all parts
        confirmation = input("Do you want to update all parts listed above? (yes/no): ")
        if confirmation.lower() != 'yes':
            logging.info("Update process aborted by user")
            return
        
        for part, row in parts_to_update:
            part_data = {
                'name': row['name'],
                'description': row['description'],
                'category': row['category'],
                'IPN': row['IPN'],
                'revision': row['revision'],
                'keywords': row['keywords'],
                'units': row['units'],
                'link': row['link'],
                'active': bool(row['active']),
                'virtual': bool(row['virtual']),
                'assembly': bool(row['assembly']),
                'component': bool(row['component']),
                'purchaseable': bool(row['purchaseable']),
                'salable': bool(row['salable']),
                'trackable': bool(row['trackable']),
                'notes': row['notes'],
                'variant_of': row['variant_of'],
                'is_template': bool(row['is_template']),
                'responsible': row['responsible'],
                'default_location': row['default_location'],
                'default_supplier': row['default_supplier'],
                'default_expiry': int(row['default_expiry']) if row['default_expiry'] != '' else 0,
                'minimum_stock': int(row['minimum_stock']) if row['minimum_stock'] != '' else 0,
                'bom': row['bom'],
                'parameters': row['parameters'],
                'attachments': row['attachments'],
                'owner': row['owner'],
                'existing_image': row['image']
            }
            updated_part = update_part_information(part, part_data)
            
            if updated_part:
                supplier_data = {
                    'part': updated_part.pk,
                    'supplier': row['supplier_pk'],
                    'SKU': row['supplier_part_number'],
                    'link': row['supplier_link'],
                    'pack_quantity': int(row['supplier_pack_quantity']) if row['supplier_pack_quantity'] != '' else 0
                }
                update_supplier_information(api, updated_part, supplier_data)
    
    logging.info("Update process completed")

if __name__ == "__main__":
    csv_file_path = 'import.csv'
    main(csv_file_path, api, url, token)