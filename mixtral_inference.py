import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = "!"

model = AutoModelForCausalLM.from_pretrained(model_id) #, load_in_4bit=True)
# model.to("cuda")
lora_path = "mixtral-lora-instruct-cs/checkpoint-1098"


model = PeftModel.from_pretrained(model, lora_path) 
# model = model.merge_and_unload()
text = "Qu'est-ce que le S8 ?"
inputs = tokenizer(text, return_tensors="pt")
input_ids=inputs['input_ids'].to("cuda")
outputs = model.generate(input_ids, max_new_tokens=20)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))