import pandas as pd
import logging
from inventree.api import InvenTreeAPI
from inventree.part import Part
import os
from dotenv import load_dotenv
from datetime import datetime
import shutil

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

def duplicate_file_with_timestamp(file_path, subfolder):
    """
    Duplicates the file with a timestamp in the name and stores it in the specified subfolder.
    """
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(file_path)
    new_file_name = f"{os.path.splitext(base_name)[0]}_{timestamp}{os.path.splitext(base_name)[1]}"
    new_file_path = os.path.join(subfolder, new_file_name)
    
    shutil.copy2(file_path, new_file_path)
    logging.info(f"File duplicated to {new_file_path}")

def main(csv_file_path, api):
    """
    Main function to update parts based on the CSV file.
    """
    parts_info = collect_info_from_csv(csv_file_path)
    changes = []
    
    for index, row in parts_info.iterrows():
        part = Part(api, pk=row['pk'])
        
        changes.append({
            'pk': part.pk,
            'existing_name': part.name,
            'existing_description': part.description,
            'new_name': row['new_name'],
            'new_description': row['description']
        })
    
    print("The following changes will be made:")
    for change in changes:
        print(f"Part ID: {change['pk']}")
        print(f"  Existing name: {change['existing_name']}")
        print(f"  Existing description: {change['existing_description']}")
        print(f"  New name: {change['new_name']}")
        print(f"  New description: {change['new_description']}")
        print()
    
    confirmation = input("Do you want to apply all these changes? (yes/no): ")
    
    if confirmation.lower() == 'yes':
        for change in changes:
            part = Part(api, pk=change['pk'])
            part_data = {
                'name': change['new_name'],
                'description': change['new_description']
            }
            update_part_information(part, part_data)
        
        logging.info("Update process completed")
        
        # Duplicate the CSV file with a timestamp and store it in the _executed subfolder
        duplicate_file_with_timestamp(csv_file_path, '_executed')
    else:
        logging.info("Update process aborted by user")

if __name__ == "__main__":
    csv_file_path = 'led_update.csv'
    main(csv_file_path, api)