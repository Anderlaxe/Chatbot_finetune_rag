###############
### Imports ###
###############

### Python imports ###

import os
from tqdm import tqdm

### Module imports ###

from tools.tools_basis import (
    save_json_file
)
from tools.tools_constants import (
    PATH_SCRAPPING,
    PATH_TRAIN_SET_TEXT
)

#################
### Functions ###
#################

def split_content(content):
    list_info = []
    LIMIT_CHARACTERS = 400 # limit of characters before ending the sentence
    counter_character = 0
    temp_content = ""

    for global_counter_character in range(len(content)):
        character = content[global_counter_character]

        # Split the content to the points
        if counter_character >= LIMIT_CHARACTERS and character in [".", "?", "!", "\n"]:

            try:
                next_character = content[global_counter_character+1]
            except:
                next_character = ""
            try:
                previous_characters = temp_content[-3:]
            except:
                previous_characters = ""

            # Avoid spliting for etc. and ...
            if not(character == "." and (previous_characters == "etc" or next_character == "." or previous_characters[-1] == ".")):
                counter_character = 0
                temp_content += character
                while temp_content[0] in ["\n", " "]:
                    temp_content = temp_content[1:]
                list_info.append({"info": temp_content})
                temp_content = ""

            else:
                counter_character += 1
                temp_content += character

        else:
            counter_character += 1
            temp_content += character

    return list_info

#################
### Main code ###
#################

validation_proportion = 0.2
dict_notes = {"dataset": []}

for file_name in tqdm(os.listdir(PATH_SCRAPPING)):
    if "reg_fise_1" in file_name or "reg_fise_2" in file_name or "reg_fise_3" in file_name:
        file = open(file=PATH_SCRAPPING+file_name, encoding="utf-8")
        file_content = file.read()
        list_info = split_content(file_content) 
        for dict_info in list_info:
            dict_notes["dataset"].append(dict_info)

# Save the train dictionary
save_json_file(file_path=PATH_TRAIN_SET_TEXT, dict_to_save=dict_notes)
