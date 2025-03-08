# Lo script genera un csv che contiene dati circa le categorie che classificano le parts

from datetime import datetime
from inventree.api import InvenTreeAPI
from inventree.part import PartCategory

SERVER_ADDRESS = 'https://inventory.cortinet.ch'
#token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111'

api = InvenTreeAPI(SERVER_ADDRESS, token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111')

# Assuming `api` is already defined and authenticated
category = PartCategory(api, 1)
# counter
count=0
# Generate the timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# Create the filename with the timestamp
filename = f'category_fields_{timestamp}.csv'


# Print the count of categories
print(category.count(api))

with open(filename, 'w', encoding='utf-8') as file:

    file.write('Item,PK,Parent,Level,Name,Description\n')
    # List and print category information
    for categoryinfo in category.list(api):
        print(f'{categoryinfo.name} - {categoryinfo.description}')
        fields_str = f'{count},{categoryinfo.pk},{categoryinfo.parent},{categoryinfo.level},{categoryinfo.name},{categoryinfo.description}\n'
        file.write(fields_str)
        count = count + 1
    else:
        print('error')

print (f'{category.count(api)} categories found')