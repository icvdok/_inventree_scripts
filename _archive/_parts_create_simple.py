import pandas as pd
from inventree.api import InvenTreeAPI
from inventree.part import Part

# Define the URL and token
url = 'https://inventory.cortinet.ch'
token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111'

# Initialize the InvenTree API
api = InvenTreeAPI(url, token=token)

# Read the CSV file
csv_file = 'import_list_t.csv'
parts_df = pd.read_csv(csv_file)

# Iterate over each row in the DataFrame and create parts
for index, row in parts_df.iterrows():
    part_data = {
        'name': row.get('name', ''),
        'description': row.get('description', ''),
        'category': row.get('category', 0),
        # Add other fields as needed
    }

    try:
        # Create the part in InvenTree
        part = Part.create(api, part_data)
        print(f"Created part: {part.name}")
    except Exception as e:
        print(f"Error creating part at row {index}: {e}")
        print(f"Part data: {part_data}")

print("Parts import completed successfully!")
