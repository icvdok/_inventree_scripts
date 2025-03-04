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

# List all parts to be created
logging.info("\nThe script will create the following parts:\n")
for index, row in df.iterrows():
    logging.info(f"Name: {row['name']}")
    logging.info(f"Description: {row['description']}")
    logging.info(f"Category: {row['category']}")
    logging.info(f"IPN: {row['IPN']}")
    logging.info(f"Revision: {row['revision']}")
    logging.info(f"Keywords: {row['keywords']}")
    logging.info(f"Units: {row['units']}")
    logging.info(f"Link: {row['link']}")
    logging.info(f"Active: {row['active']}")
    logging.info(f"Virtual: {row['virtual']}")
    logging.info(f"Assembly: {row['assembly']}")
    logging.info(f"Component: {row['component']}")
    logging.info(f"Purchaseable: {row['purchaseable']}")
    logging.info(f"Salable: {row['salable']}")
    logging.info(f"Trackable: {row['trackable']}")
    logging.info(f"Notes: {row['notes']}")
    logging.info(f"Variant Of: {row['variant_of']}")
    logging.info(f"Is Template: {row['is_template']}")
    logging.info(f"Responsible: {row['responsible']}")
    logging.info(f"Default Location: {row['default_location']}")
    logging.info(f"Default Supplier: {row['default_supplier']}")
    logging.info(f"Default Expiry: {row['default_expiry']}")
    logging.info(f"Minimum Stock: {row['minimum_stock']}")
    logging.info(f"BOM: {row['bom']}")
    logging.info(f"Parameters: {row['parameters']}")
    logging.info(f"Attachments: {row['attachments']}")
    logging.info(f"Owner: {row['owner']}")
    logging.info(f"Existing Image: {row['image']}")
    logging.info(f"Supplier PK: {row['supplier_pk']}")
    logging.info(f"Supplier Part Number: {row['supplier_part_number']}")
    logging.info(f"Supplier Link: {row['supplier_link']}")
    logging.info(f"Supplier Pack Quantity: {row['supplier_pack_quantity']}")
    logging.info("\n")

# Ask for confirmation
confirmation = input("\nDo you want to proceed with creating these parts? (yes/no): ")

if confirmation.lower() == 'yes':
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
            'supplier_link': row['supplier_link'],  # Add supplier link
            'supplier_pack_quantity': int(row['supplier_pack_quantity']) if row['supplier_pack_quantity'] != '' else 0  # Add supplier pack quantity
        }

        try:
            # Create the part in InvenTree
            part = Part.create(api, part_data)
            logging.info(f"Created part: {part.name} - {part.pk}")

            # Add supplier information if available and valid
            if row['supplier_pk'] and row['supplier_part_number'] and row['supplier_part_number'] != '0':
                supplier_data = {
                    'part': part.pk,
                    'supplier': row['supplier_pk'],
                    'SKU': row['supplier_part_number'],
                    'link': row['supplier_link'],  # Include supplier link
                    'pack_quantity': int(row['supplier_pack_quantity']) if row['supplier_pack_quantity'] != '' else 0  # Add supplier pack quantity
                }

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
else:
    logging.info("Operation cancelled.")