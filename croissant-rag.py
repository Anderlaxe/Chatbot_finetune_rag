## Main module to execute Croissant LLM RAG model without fine-tuning

###############
### Imports ###
###############

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)
import time

#################
### Main code ###
#################

model_id = "croissantllm/CroissantLLMChat-v0.1"
tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    # load_in_4bit=True, 
    # torch_dtype=torch.float16
    )
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_id)

with open("stage_op.md", "r") as f:
    stage_op = f.read()

test_questions = ["Comment est évalué le stage d'exécution ?"]


for question in test_questions:
    start_time = time.time()
    rag_and_quest = f"Tu es le chatbot de l'université. Voici les documents à ta disposition : \n {stage_op}. A partir de ces informations, réponds à la question suivante. La réponse doit être la plus courte possible, arrête-toi juste après l'idée principale. Voici la question : \n {question}"
    model_inputs = tokenizer(rag_and_quest, return_tensors="pt")     

    model.eval()
    with torch.no_grad():
      model_out = model.generate(model_inputs['input_ids'], max_new_tokens=50)
      print(tokenizer.decode(model_out[0], skip_special_tokens = True))
      end_time = time.time()
      print("Time difference : ", end_time-start_time)