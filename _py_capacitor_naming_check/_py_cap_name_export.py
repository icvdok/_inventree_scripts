import csv
import logging
from inventree.api import InvenTreeAPI
from inventree.part import Part
import os
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
        writer.writerow(['pk', 'name', 'description'])
        for part in parts:
            writer.writerow([part.pk, part.name, part.description])
    logging.info(f"Parts exported to {file_path}")

def main(api, category_pk, csv_file_path):
    """
    Main function to export parts to a CSV file.
    """
    parts = get_parts_in_category(api, category_pk)
    export_parts_to_csv(parts, csv_file_path)

if __name__ == "__main__":
    category_pk = 82
    csv_file_path = 'parts_update.csv'
    main(api, category_pk, csv_file_path)