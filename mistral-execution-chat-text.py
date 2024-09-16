"""
Main module to execute Mistral after finetuning.
"""

###############
### Imports ###
###############

### Python imports ###

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)
from peft import PeftModel

### Local imports ###

from tools.tools_basis import (
    save_txt_file
)
from tools.tools_constants import (
    BASE_MODEL_ID,
    ACCESS_TOKEN,
    DELIMITATION_CHARACTER,
    PATH_RAW_RESULTS_CHAT_TEXT,
    PATH_RESULTS,
    MODE_CHAT_TEXT,
    PATH_SAVE_MODEL_CHAT_TEXT,
    NUMBER_EPOCHS
)
from tools.tools_dataset import (
    provide_test_base
)
from tools.tools_models import (
    bnb_config,
    tokenizer
)

#################
### Main code ###
#################

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    token=ACCESS_TOKEN
)

tokenizer.pad_token = tokenizer.eos_token

eval_tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL_ID,
    add_bos_token=True,
    trust_remote_code=True,
)

ft_model = PeftModel.from_pretrained(
    base_model,
    PATH_SAVE_MODEL_CHAT_TEXT + "/checkpoint-" + str(NUMBER_EPOCHS)
)

test_questions = provide_test_base()

output = ""
for question in test_questions:
    model_input = tokenizer(question, return_tensors="pt").to("cuda")

    ft_model.eval()
    with torch.no_grad():
        output += "\n" + DELIMITATION_CHARACTER + "\n"
        output += eval_tokenizer.decode(
            ft_model.generate(**model_input, max_new_tokens=200)[0],
            skip_special_tokens=True)

# Make 
try:
    os.mkdir(PATH_RESULTS + "/" + MODE_CHAT_TEXT)
except:
    pass

# Save the results
save_txt_file(
    file_path=PATH_RAW_RESULTS_CHAT_TEXT,
    content=output)
