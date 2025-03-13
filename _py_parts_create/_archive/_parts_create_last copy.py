import pandas as pd
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
# Define the URL

if not token:
    raise ValueError("API token not found in secrets file.")

# Initialize the InvenTree API
api = InvenTreeAPI(url, token=token)

# Read the CSV file
csv_file = 'import_list.csv'
df = pd.read_csv(csv_file)

# Replace NaN values with empty strings or appropriate defaults
df = df.fillna('').infer_objects(copy=False)

# Track errors
errors_occurred = False

# Iterate over each row in the DataFrame and create parts
for index, row in df.iterrows():
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
        'existing_image': row['image'],  # Keep the image field here
        'supplier_pk': row['supplier_pk'],  # Add supplier primary key
        'supplier_part_number': row['supplier_part_number'],  # Add supplier part number
        'supplier_link': row['supplier_link']  # Add supplier link
    }

    try:
        # Create the part in InvenTree
        part = Part.create(api, part_data)
        logging.info(f"Created part: {part.name} - {part.pk}")

        # Debugging lines to check supplier fields
        logging.debug(f"Row {index} - Supplier PK: {row['supplier_pk']}, Supplier Part Number: {row['supplier_part_number']}, Supplier Link: {row['supplier_link']}")

        # Add supplier information if available and valid
        if row['supplier_pk'] and row['supplier_part_number'] and row['supplier_part_number'] != '0':
            supplier_data = {
                'part': part.pk,
                'supplier': row['supplier_pk'],
                'SKU': row['supplier_part_number'],
                'link': row['supplier_link'],  # Include supplier link
                'pack_quantity': int(row['supplier_pack_quantity']) if row['supplier_pack_quantity'] != '' else 0  # Add supplier pack quantity
            }
            logging.debug(f"Supplier data: {supplier_data}")  # Debugging line

            supplier_part = SupplierPart.create(api, supplier_data)
            logging.info(f"Added supplier part: {supplier_part.SKU} for part: {part.name}")

    except Exception as e:
        logging.error(f"Error creating part at row {index}: {e}")
        logging.error(f"Part data: {part_data}")
        errors_occurred = True

if errors_occurred:
    logging.info("Parts import executed with errors.")
else:
    logging.info("Parts import executed successfully!")
