#informazioni di base dell'istanza Inventree
import requests

# Define the URL and token
url = 'https://inventory.cortinet.ch/api/'
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
    # Print the response content
    print(response.json())
else:
    print(f"Failed to retrieve data: {response.status_code}")