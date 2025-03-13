import pandas as pd
from inventree.api import InvenTreeAPI
from inventree.part import Part
from inventree.company import SupplierPart
import os
import logging
import csv
from dotenv import load_dotenv
from datetime import datetime

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

# Define the data structure for part fields
part_fields = [
    'name', 'description', 'category', 'active', 'assembly', 'component', 'purchaseable', 
    'notes', 'minimum_stock', 'parameters', 'attachments', 
    'existing_image', 'supplier_pk', 'supplier_part_number', 'supplier_link', 
    'supplier_pack_quantity'
]

def create_csv_template():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_filename = f"parts_{timestamp}.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(part_fields)
        logging.info(f"CSV template '{csv_filename}' with header row has been created successfully.")
    print(f"CSV template '{csv_filename}' with header row has been created successfully.")
    return csv_filename

def create_parts_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = df.fillna('').infer_objects(copy=False)

    errors_occurred = False

    logging.info("\nThe script will create the following parts:\n")
    for index, row in df.iterrows():
        for field in part_fields:
            logging.info(f"{field.capitalize().replace('_', ' ')}: {row[field]}")
        logging.info("\n")

    confirmation = input("\nDo you want to proceed with creating these parts? (yes/no): ")

    if confirmation.lower() == 'yes':
        for index, row in df.iterrows():
            part_data = {field: row[field] for field in part_fields if field in row}
            
            try:
                part = Part.create(api, part_data)
                logging.info(f"Created part: {part.name} - {part.pk}")

                if row['supplier_pk'] and row['supplier_part_number'] and row['supplier_part_number'] != '0':
                    supplier_data = {
                        'part': part.pk,
                        'supplier': row['supplier_pk'],
                        'SKU': row['supplier_part_number'],
                        'link': row['supplier_link'],
                        'pack_quantity': int(row['supplier_pack_quantity']) if row['supplier_pack_quantity'] != '' else 0
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

def main():
    while True:
        print("Select an option:")
        print("1. Create CSV template")
        print("2. Create parts from CSV file")
        print("3. Exit")
        
        choice = input("Enter your choice (1, 2, or 3): ")
        
        if choice == '1':
            create_csv_template()
        
        elif choice == '2':
            csv_file = input("Enter the CSV file name: ")
            create_parts_from_csv(csv_file)
        
        elif choice == '3':
            print("Exiting the script. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()