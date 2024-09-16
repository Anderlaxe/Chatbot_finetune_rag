"""
Python script to clear the output of the chatbot.
"""

###############
### Imports ###
###############

### Local imports ###

from tools.tools_constants import (
    PATH_DATABASE,
    PATH_RESULTS
)
from tools.tools_results import (
    transform_raw_results
)

#################
### Main code ###
#################

transform_raw_results(
    path_raw_results=PATH_RESULTS + "cs_full_embeddings/cs-intel-rde-split-chunks_full_embeddings.txt",
    path_clear_results=PATH_DATABASE + "test_base_results_mistral_intel_rde.json")
