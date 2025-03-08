# Lo script genera un csv che contiene di tutte le company di tipo supplier con il numero pk
from datetime import datetime
from inventree.api import InvenTreeAPI
from inventree.company import Company

SERVER_ADDRESS = 'https://inventory.cortinet.ch'
#token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111'

api = InvenTreeAPI(SERVER_ADDRESS, token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111')

# Assuming `api` is already defined and authenticated

company = Company(api, 1)

# counter
count=0
# Generate the timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# Create the filename with the timestamp
filename = f'company_list_{timestamp}.csv'

with open(filename, 'w', encoding='utf-8') as file:

    file.write('Item,PK,Name\n')
    # List and print category information
    for compinfo in company.list(api):
        if compinfo.is_supplier == True:
            print(f'{compinfo.name} - {compinfo.description}')
            fields_str = f'{count},{compinfo.pk},{compinfo.name}\n'
            file.write(fields_str)
            count = count + 1
        #else:
            #print(f'{compinfo.name} - is not a supplier')

print (f'{compinfo.count(api)} companies found')
print (f'{count} supplier found')