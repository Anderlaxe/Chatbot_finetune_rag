## Main module to execute Mixtral 8x7B RAG model without fine-tuning

###############
### Imports ###
###############

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)
import time
# from peft import PeftModel

#################
### Main code ###
#################

model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    load_in_4bit=True, 
    torch_dtype=torch.float16
    )
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_id)
if torch.cuda.is_available():
    model.to("cuda")

with open("scraping/contents/stage_op.md", "r") as f:
    stage_op = f.read()

test_questions = ["Comment est évalué le stage d'exécution ?"]


for question in test_questions:
    start_time = time.time()
    rag_and_quest = f"Tu es le chatbot de l'université. Voici les documents à ta disposition : \n {stage_op}. A partir de ces informations, réponds à la question suivante de manière précise et concise : \n {question}"
    model_inputs = tokenizer(rag_and_quest, return_tensors="pt")    
    if torch.cuda.is_available():
        input_ids = model_inputs['input_ids'].to("cuda") 
    else:
        input_ids = model_inputs['input_ids']

    model.eval()
    with torch.no_grad():
      model_out = model.generate(input_ids, max_new_tokens=100)
      print("END OF ASKING QUESTIONS")
      print(tokenizer.decode(model_out[0], skip_special_tokens = True))
      end_time = time.time()
      print("Time difference : ", end_time-start_time)