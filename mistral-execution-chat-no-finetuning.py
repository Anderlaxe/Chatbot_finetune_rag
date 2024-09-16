"""
Main module to execute Mistral without finetuning.
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

### Local imports ###

from tools.tools_basis import (
    save_txt_file
)
from tools.tools_constants import (
    BASE_MODEL_ID,
    ACCESS_TOKEN,
    DELIMITATION_CHARACTER,
    LANGUAGE,
    MODE_CHAT,
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

test_questions = provide_test_base()

import time
start_time = time.time()
output = ""
for question in test_questions:
    model_input = tokenizer(question, return_tensors="pt").to("cuda")

    base_model.eval()
    with torch.no_grad():
        output += "\n" + DELIMITATION_CHARACTER + "\n"
        output += eval_tokenizer.decode(
            base_model.generate(**model_input, max_new_tokens=200)[0],
            skip_special_tokens=True)
end_time = time.time()
print("END OF ASKING QUESTIONS")
print(end_time, start_time, end_time-start_time)

output_dir = "results/chat_no_finetuning/"
# Make 
try:
    os.mkdir(output_dir)
except:
    pass

# Save the results
save_txt_file(
    file_path=output_dir + MODE_CHAT + "_" + LANGUAGE + "no_finetuning.txt",
    content=output)
