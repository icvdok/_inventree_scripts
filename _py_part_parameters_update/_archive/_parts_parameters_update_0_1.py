import requests
import os
import logging
from dotenv import load_dotenv
import csv

# Define ANSI escape codes for colors
RED = "\033[91m"
RESET = "\033[0m"

# Custom logging formatter to add color
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.ERROR:
            record.msg = f"{RED}{record.msg}{RESET}"
        return super().format(record)

# Set up logging
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

load_dotenv()

url = os.getenv('BASE_URL')
token = os.getenv('INVENTREE_API_TOKEN')

if not url:
    logger.error("BASE_URL is not set in the environment variables.")
    exit(1)

headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

# Option 1
def get_parameters_templates_by_category(category_pk):
    endpoint = f"{url}part/category/parameters/?category={category_pk}"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        parameters = response.json()
        filtered_params = []
        for param in parameters:
            filtered_param = {
                'parameter_template': param.get('parameter_template'),
                'parameter_template_detail': param.get('parameter_template_detail'),
                'default_value': param.get('default_value')
            }
            filtered_params.append(filtered_param)
        return filtered_params
    else:
        logger.error(f"Failed to retrieve parameters: {response.status_code} - {response.text}")
        return None

def get_parts_by_category(category_pk):
    endpoint = f"{url}part/?category={category_pk}"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        parts = response.json()
        parts_list = [{'part name': part['name'], 'part pk': part['pk']} for part in parts]
        return parts_list
    else:
        logger.error(f"Failed to retrieve parts: {response.status_code} - {response.text}")
        return None

def get_current_parameters(part_pk):
    endpoint = f"{url}part/category/parameters/{part_pk}/"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to retrieve current parameters for part {part_pk}: {response.status_code} - {response.text}")
        return None

def create_csv(parameters, parts):
    parameter_template_names = [
        f"{param['parameter_template_detail']['name']}%{param['parameter_template']}%{param['parameter_template_detail'].get('selectionlist', 'False') or 'False'}%{param['parameter_template_detail'].get('checkbox', False)}"
        for param in parameters
    ]
    header_row = ['part name', 'part pk'] + parameter_template_names
    with open('parameters.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header_row)
        logger.info(f"CSV header row: {header_row}")
        for part in parts:
            row = [part['part name'], part['part pk']]
            current_parameters = get_current_parameters(part['part pk'])
            if current_parameters:
                for param in parameters:
                    param_value = next((p['data'] for p in current_parameters if p['template'] == param['parameter_template']), '')
                    row.append(param_value)
            writer.writerow(row)
            logger.info(f"CSV row for part {part['part pk']}: {row}")

#Option2
def get_selection_lists():
    logging.info("f_get_selection_lists function executed")
    endpoint = f"{url}selection/"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        selection_lists = response.json()
        selection_list_map = {}
        for selection_list in selection_lists:
            pk = selection_list['pk']
            values = [choice['value'] for choice in selection_list['choices']]
            selection_list_map[pk] = values
        return selection_list_map
    else:
        logging.error(f"Failed to retrieve selection lists: {response.status_code} - {response.text}")
        return None

def validate_selection_list(selectionlist_pk, value, selection_list_map):
    logging.info("f_validate_selection_list function executed")
    try:
        selectionlist_pk = int(selectionlist_pk)
    except ValueError:
        logging.error(f"Invalid selection list pk: {selectionlist_pk}")
        return False
    if selectionlist_pk in selection_list_map:
        if value in selection_list_map[selectionlist_pk]:
            return True
        else:
            logging.error(f"Value '{value}' not found in selection list pk: {selectionlist_pk}")
            return False
    else:
        logging.error(f"Selection list pk '{selectionlist_pk}' not found in the selection list map.")
        return False

def validate_boolean_value(value):
    logging.info("f_validate_boolean_value function executed")
    if value.lower() in ['true', 'false']:
        return True
    else:
        logging.error(f"Invalid boolean value: {value}")
        return False

def validate_csv_data():
    logging.info("f_validate_csv_data executed")
    selection_list_map = get_selection_lists()
    if not selection_list_map:
        logging.error("Failed to retrieve selection lists. Aborting validation.")
        return False, ["Failed to retrieve selection lists."]
    
    validation_registry = {}
    error_messages = []
    
    with open('parameters.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            part_pk = row['part pk']
            validation_registry[part_pk] = True
            for key, value in row.items():
                if key not in ['part name', 'part pk']:
                    parameter_template_info = key.split('%')
                    parameter_template_name = parameter_template_info[0]
                    parameter_template_pk = parameter_template_info[1]
                    selectionlist_pk = parameter_template_info[2]
                    parameter_boolean = parameter_template_info[3]
                    
                    if selectionlist_pk == 'False':
                        logging.info("no selection list")
                    else:
                        check_selection = validate_selection_list(selectionlist_pk, value, selection_list_map)
                        logging.info(f"check selection results= {check_selection}")
                        if not check_selection:
                            validation_registry[part_pk] = False
                            error_messages.append(f"Part pk: {part_pk}, Parameter template: {parameter_template_name}, Value: {value} - Invalid selection list value.")
                    
                    if parameter_boolean == 'True':
                        boolean_check = validate_boolean_value(value)
                        logging.info(f"boolean check results= {boolean_check}")
                        if not boolean_check:
                            validation_registry[part_pk] = False
                            error_messages.append(f"Part pk: {part_pk}, Parameter template: {parameter_template_name}, Value: {value} - Invalid boolean value.")
    
    all_valid = all(validation_registry.values())
    if all_valid:
        logging.info("All data in the CSV file is valid.")
    else:
        logging.error("Some data in the CSV file is invalid. Aborting update.")
    
    return all_valid, error_messages
#Option3
def part_category_parameters_update():
    logging.info("f_part_category_parameters_update executed")
    selection_list_map = get_selection_lists()
    if not selection_list_map:
        logging.error("Failed to retrieve selection lists. Aborting parameter update.")
        return
    
    with open('parameters.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            part_pk = row['part pk']
            for key, value in row.items():
                if key not in ['part name', 'part pk']:
                    parameter_template_info = key.split('%')
                    parameter_template_name = parameter_template_info[0]
                    parameter_template_pk = parameter_template_info[1]
                    selectionlist_pk = parameter_template_info[2]
                    
                    # Check if the parameter already exists for the part
                    endpoint = f"{url}part/parameter/?part={part_pk}&template={parameter_template_pk}"
                    response = requests.get(endpoint, headers=headers)
                    if response.status_code == 200:
                        existing_parameters = response.json()
                        if existing_parameters:
                            # Update the existing parameter
                            parameter_pk = existing_parameters[0]['pk']
                            endpoint = f"{url}part/parameter/{parameter_pk}/"
                            payload = {
                                'part': part_pk,
                                'template': parameter_template_pk,
                                'data': value,
                                'selectionlist': selectionlist_pk if selectionlist_pk != 'False' else None
                            }
                            response = requests.put(endpoint, headers=headers, json=payload)
                            if response.status_code == 200:
                                logging.info(f"Successfully updated part pk: {part_pk}, Parameter template: {parameter_template_name}, Value: {value}")
                            else:
                                logging.error(f"Failed to update part pk: {part_pk}, Parameter template: {parameter_template_name}, Value: {value} - {response.status_code} - {response.text}")
                        else:
                            logging.error(f"No existing parameter found for part pk: {part_pk}, Parameter template: {parameter_template_name}. Skipping update.")
                    else:
                        logging.error(f"Failed to retrieve existing parameters for part pk: {part_pk}, Parameter template: {parameter_template_name} - {response.status_code} - {response.text}")

#Option4
def normalize_parameters(category_pk):

    return 

def main():
    validation_result = None
    error_messages = []

while True:
    print("Select an option:")
    print("1. Extract parameter template file")
    print("2. Validate the information in the CSV file")
    print("3. Process the data and update the parts")
    print("4. Normalize the parameters of the parts according to the category parameters")
    print("5. Exit")
    
    choice = input("Enter your choice (1, 2, 3, 4, or 5): ")
    
    if choice == '1':
        category_pk = 82
        parameters = get_parameters_templates_by_category(category_pk)
        parts = get_parts_by_category(category_pk)
        if parameters and parts:
            create_csv(parameters, parts)
            print("CSV file with header row and parts data has been created successfully.")
        else:
            print("No parameters or parts found or failed to retrieve data.")
    
    elif choice == '2':
        validation_result, error_messages = validate_csv_data()
        if validation_result:
            print("Validation successful. You can now proceed to update the parts.")
        else:
            print("Validation failed. Please check the CSV file for errors.")
            for error in error_messages:
                print(error)
    
    elif choice == '3':
        if validation_result is None:
            print("Please validate the CSV file first by selecting option 2.")
        elif validation_result:
            part_category_parameters_update()
        else:
            print("Validation failed. Please re-execute option 2 after fixing the errors.")
    elif choice == '4':

    elif choice == '5':
        print("Exiting the script. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter 1, 2, 3, 4 or 5.")

if __name__ == "__main__":
    main()