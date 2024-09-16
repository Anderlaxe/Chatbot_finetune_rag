###############
### Imports ###
###############

### Python imports ###

import sys
sys.path.append("./")

### Local imports ###

from tools.tools_basis import (
    load_json_file,
    save_json_file
)
from tools.tools_constants import (
    PATH_CS_CLEAR_DATABASE,
    PATH_CS_CLEAR_DATABASE_RDE,
    PATH_CS_SCRAPPING_DATABASE
)

#################
### Functions ###
#################

def remove_null_values(data):
    if data["link"] is None:
        data["link"] = ""
    if data["filename"] is None:
        data["filename"] = ""
    return data

def remove_too_small_content(data):
    content = data["content"]
    bool_to_remove = False
    if len(content) <= 110:
        bool_to_remove = True
    return bool_to_remove

def remove_repeat_content(data, list_new_content):
    return data["content"] in list_new_content

def clear_content(data):

    while "--" in data["content"]:
        data["content"] = data["content"].replace("--", "")
    while "==" in data["content"]:
        data["content"] = data["content"].replace("==", "")
    while "    " in data["content"]:
        data["content"] = data["content"].replace("    ", "")
    while "  " in data["content"]:
        data["content"] = data["content"].replace("  ", " ")

    return data

def filtering_function_rde(item):
    return "reg_fise" in item["filename"]

#################
### Main code ###
#################

# Load the test database
database: list = load_json_file(file_path=PATH_CS_SCRAPPING_DATABASE)

# Change the test base, by removing null value and too small content
list_to_remove = []
list_new_content = []
for counter in range(len(database)):
    data = database[counter]
    bool_to_remove_too_small = remove_too_small_content(data)
    bool_to_remove_repeat = remove_repeat_content(data, list_new_content)
    bool_to_remove = bool_to_remove_repeat or bool_to_remove_too_small

    if not bool_to_remove:
        data = remove_null_values(data)
        list_new_content.append(data["content"])
        data = clear_content(data)
        database[counter] = data
    else:
        list_to_remove.append(data)

for data in list_to_remove:
    database.remove(data)

filter_rde = filter(filtering_function_rde, database)
database_rde = list(filter_rde)

# Save the test database
save_json_file(file_path=PATH_CS_CLEAR_DATABASE, dict_to_save=database)
save_json_file(file_path=PATH_CS_CLEAR_DATABASE_RDE, dict_to_save=database_rde)
