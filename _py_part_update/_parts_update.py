import pandas as pd
from inventree.api import InvenTreeAPI
from inventree.part import Part
from inventree.company import SupplierPart
import os
import logging
import csv
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

# Define the data structure for part fields
part_fields = [
    'pk', 'name', 'description', 'active', 'assembly', 'component', 'purchaseable', 
    'notes', 'minimum_stock', 'parameters', 'attachments', 
    'image', 'supplier_pk', 'supplier_part_number', 'supplier_link', 
    'supplier_pack_quantity'
]

def get_parts_by_category(category_pk):
    parts = Part.list(api, category=category_pk)
    parts_list = []
    for part in parts:
        part_data = {field: getattr(part, field, '') for field in part_fields}
        parts_list.append(part_data)
    return parts_list

def create_csv(parts, category_pk):
    header_row = part_fields
    csv_filename = f"{category_pk}.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header_row)
        #logging.info(f"CSV header row: {header_row}")
        for part in parts:
            row = [part.get(field, '') for field in part_fields]
            writer.writerow(row)
            #logging.info(f"CSV row for part {part['name']}: {row}")
    #print(f"CSV file '{csv_filename}' with header row and parts data has been created successfully.")

def collect_and_match_parts_from_csv(file_path, api):
    """
    Reads the CSV file and matches parts in InvenTree by pk number.
    Returns a list of matched parts and their data.
    """
    logging.info("Reading CSV file")
    df = pd.read_csv(file_path)
    df = df.fillna('').infer_objects(copy=False)
    logging.info("CSV file read successfully")

    if 'pk' not in df.columns:
        logging.error("CSV file does not contain 'pk' column.")
        return []

    matched_parts = []
    for _, row in df.iterrows():
        part_pk = row['pk']
        logging.info(f"Searching for part with pk: {part_pk}")
        part = Part(api, pk=part_pk)
        if part:
            logging.info(f"Part found: {part.name} (ID: {part.pk})")
            matched_parts.append((part, row))
        else:
            logging.info(f"No matching part found for pk: {part_pk}")

    return matched_parts

def update_part_information(part, part_data):
    """
    Updates the part information with the provided data.
    Returns the updated part if successful, otherwise returns None.
    """
    try:
        update_data = {field: part_data[field] for field in part_fields if field in part_data}
        # Keep the full path for the image field
        if 'image' in update_data:
            update_data['existing_image'] = update_data.pop('image')
        part.save(update_data)
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
        if not supplier_data['supplier'] or not supplier_data['SKU']:
            logging.info("Supplier or SKU field is blank. Skipping supplier update.")
            return None

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
    
def display_intro():
    intro_text = """
    Welcome to the InvenTree Part Update Script!

    This script allow you to update inventree parts.
    It ask for a specific category and export a csv template including all fields specified in the part_fields data structure. This fields will be adjusted and updated.
    - The matching procedure to match the right part in inventree with the csv file is based on the part pk.
    - Blank fields are skipped during the update procedure.
    
    Note: Parts fields can be adjusted on needs in the part_fields data structure
    
    This script allows you to:
    1. Extract a CSV file containing part information from a specified category.
    2. Modify the extracted CSV file as needed.
    3. Start the update procedure to update parts and supplier information based on the modified CSV file.

    Please follow the prompts to proceed with the desired action.
    """
    print(intro_text)
    
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main(api, api_url, token):
    """
    Main function to update parts and supplier information based on the CSV file.
    """
    clear_screen()
    display_intro()
    category_pk = input("Enter the category PK: ")

    while True:
        print("Select an option:")
        print("1. Extract parameter template file")
        print("2. Start the update procedure")
        print("3. Exit")
        
        choice = input("Enter your choice (1, 2, or 3): ")
        
        if choice == '1':
            parts_forcsv = get_parts_by_category(category_pk)
            create_csv(parts_forcsv, category_pk)
            print("CSV file with header row and parts data has been created successfully.")
            print("Please modify the CSV file as needed before proceeding to the update procedure.")
        
        elif choice == '2':
            csv_file_path = f"{category_pk}.csv"
            matched_parts = collect_and_match_parts_from_csv(csv_file_path, api)
            #for part, row in matched_parts:
            #    logging.info(f"Matched part: {part.name} with data: {row}")

            # Ask for confirmation before updating parts
            confirmation = input("Do you want to update the matched parts? (yes/no): ")
            if confirmation.lower() != 'yes':
                logging.info("Update process aborted by user.")
                return

            for part, row in matched_parts:
                updated_part = update_part_information(part, row)
                if updated_part:
                    supplier_data = {
                        'part': updated_part.pk,
                        'supplier': row['supplier_pk'],
                        'SKU': row['supplier_part_number'],
                        'link': row['supplier_link'],
                        'pack_quantity': int(row['supplier_pack_quantity']) if row['supplier_pack_quantity'] != '' else 0
                    }
                    update_supplier_information(api, updated_part, supplier_data)
        
        elif choice == '3':
            print("Exiting the script. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main(api, url, token)