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
df = pd.read_csv(csv_file)

# Replace NaN values with empty strings or appropriate defaults
df = df.fillna('').infer_objects(copy=False)

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
        'existing_image': row['image']  # Keep the image field here
    }

    try:
        # Create the part in InvenTree
        part = Part.create(api, part_data)
        print(f"Created part: {part.name}")

    except Exception as e:
        print(f"Error creating part at row {index}: {e}")
        print(f"Part data: {part_data}")

print("Parts import completed successfully!")
