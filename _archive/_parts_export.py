# Lo script genera un csv che contiene di tutte le parts con il numero pk e info relative alla categoria
from datetime import datetime
from inventree.api import InvenTreeAPI
from inventree.part import PartCategory
from inventree.part import Part

SERVER_ADDRESS = 'https://inventory.cortinet.ch'
#token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111'

api = InvenTreeAPI(SERVER_ADDRESS, token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111')

# Assuming `api` is already defined and authenticated

category = PartCategory(api, 1)
parts = Part(api,1)


# counter
count=0
# Generate the timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# Create the filename with the timestamp
filename = f'parts_list_{timestamp}.csv'


# Print the count of categories
print(parts.count(api))

with open(filename, 'w', encoding='utf-8') as file:

    file.write('Item,PK,Category,Name,Description,Image\n')
    # List and print category information
    for partinfo in parts.list(api):
        print(f'{partinfo.name} - {partinfo.description}')
        fields_str = f'{count},{partinfo.pk},{partinfo.name},{partinfo.description},{partinfo.image}\n'
        file.write(fields_str)
        count = count + 1
    else:
        print('error')

print (f'{partinfo.count(api)} parts found')