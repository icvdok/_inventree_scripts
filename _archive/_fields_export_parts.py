import requests

# Define the URL and token
url = 'https://inventory.cortinet.ch/api/part/'
token = 'inv-afa139f7acd00678b74c1bb0697cb4e1335132ba-20250111'

# Set up the headers with the token
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

# Make the OPTIONS request with headers
response = requests.options(url, headers=headers)

# Check the status code
if response.status_code == 200:
    # Print the metadata
    print(response.json())
    with open('parts_fields_export.json', 'w', encoding='utf-8') as file:
        file.write(response.text)
    print("JSON exported successfully!")
else:
    print(f"Failed to retrieve metadata: {response.status_code}")