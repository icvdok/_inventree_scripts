#Esporta tutte le parts ed i relativi fields disponibili in formato JSON
import requests
from datetime import datetime

# Define the URL and token
url = 'https://inventory.cortinet.ch/api/part/'
token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111'

# Set up the headers with the token
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

# Make the GET request with headers
response = requests.get(url, headers=headers)

# Check the status code
if response.status_code == 200:
    # Generate the timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create the filename with the timestamp
    filename = f'parts_fields_{timestamp}.json'

    # Save the response content to a file with utf-8 encoding
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(response.text)
    print("Data exported successfully!")
else:
    print(f"Failed to retrieve data: {response.status_code}")