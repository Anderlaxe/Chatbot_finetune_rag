"""
Module to convert the Google Form into a json file with all questions.

Constants
---------
PATH_DATABASE : str
    Path to the folder database.

PATH_FORM_RESULTS : str
    Path to the csv file containing the results of the form.

PATH_JSON_QUESTIONS : str
    Path to the json file containing all the questions.

COLUMNS_TO_KEEP : list[str]
    List of the columns to keep in the database. It corresponds to the columns with questions.

Functions
---------
save_json_file
    Save the content of the given dictionnary inside the specified json file.

open_csv_database
    Read the csv file of the form results and keep only the useful columns.

create_dict_questions
    Create the dictionary containing all questions of the form.
"""

###############
### Imports ###
###############

### Python imports ###

import pandas as pd
import sys
sys.path.append("./")

### Local imports ###

from tools.tools_basis import (
    save_json_file
)

#################
### Constants ###
#################

PATH_DATABASE = "database/"
PATH_FORM_RESULTS = PATH_DATABASE + "form_results.csv"
PATH_JSON_QUESTIONS = PATH_DATABASE + "test_base.json"

COLUMNS_TO_KEEP = [
    "Ta première question / Your first question",
    "Ta deuxième question / Your second question",
    "Ta dernière question / Your last question"
]

#################
### Functions ###
#################

def open_csv_database():
    """
    Read the csv file of the form results and keep only the useful columns.

    Parameters
    ----------
    None

    Returns
    -------
    database : pandas.core.frame.DataFrame
        Database of the csv with only the needed columns.
    """

    database = pd.read_csv(PATH_FORM_RESULTS)
    database = database[COLUMNS_TO_KEEP]
    return database

def create_dict_questions(database):
    """
    Create the dictionary containing all questions of the form.

    Parameters
    ----------
    database : pandas.core.frame.DataFrame
        Database of the csv with only the needed columns.

    Returns
    -------
    None
    """

    dict_questions = {"dataset": []}

    # Create the dictionary with all questions
    for column in database:
        row = database[column]
        for i, element in enumerate(row):
            element = str(element)
            if i != 0 and element != "nan":
                current_dict = {
                    "question": element,
                    "answer": "",
                    "error": {
                        "type": "",
                        "message": ""
                    }
                }
                dict_questions["dataset"].append(current_dict)


    # Save the dictionary with all questions
    save_json_file(
        file_path=PATH_JSON_QUESTIONS,
        dict_to_save=dict_questions
    )

#################
### Main code ###
#################

form_results = open_csv_database()
create_dict_questions(database=form_results)
