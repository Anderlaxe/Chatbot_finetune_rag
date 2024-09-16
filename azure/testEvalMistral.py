from botCS import BotCS
from gptJudge import GPTJudge
import json, tqdm

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from getDataMistral import get_embedding

dataset = []

with open('benchmark_ai_chatbot_cs/database/test_base.json') as f:
    data = json.load(f)
    dataset = data['dataset']

# Model
model_id = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_id, load_in_4bit=True)

# If cuda available, use cuda
if torch.cuda.is_available():
    model.to("cuda")

# Inference
def inference(model, doc, question):
    text = f"Tu es le chatbot de l'université. Voici les documents à ta disposition : \n {doc}. A partir de ces informations, réponds à la question suivante de manière précise et concise. Si la question ne concerne pas l'université, répond que la question est hors sujet. Voici la question : \n {question}"
    inputs = tokenizer(text, return_tensors="pt")
    if torch.cuda.is_available():
        input_ids=inputs['input_ids'].to("cuda")
        outputs = model.generate(input_ids, max_new_tokens=150)
    else:
        input_ids=inputs['input_ids']
        outputs = model.generate(input_ids, max_new_tokens=150)

        
    try:
      return tokenizer.decode(outputs[0], skip_special_tokens=True).split('[/INST]')[1]
    except:
      return "Erreur, la réponse ne correspond pas au format attendu"


to_skip = 0
with open('benchmark_ai_chatbot_cs/azure/results_mistral.csv', 'r') as results:
  to_skip = len(results.readlines()) - 1
if to_skip == 0:
  with open('benchmark_ai_chatbot_cs/azure/results_mistral.csv', 'w') as results:
    results.write("question,embeddings,similarity,uncertainty\n")

judge = GPTJudge()
for info in tqdm.tqdm(dataset):

    question = info['question']
    print("question :  " + question)

    doc = get_embedding(input = question)
    answer = inference(model = model, doc = doc, question = question)
    print("answer : " + answer)
    print("---")
    
    reference = info['answer']
    if (reference == ''):
        if info['error']['message']:
            reference = info['error']['message']
    
    score = judge.embeddings_score(reference, answer)
    similarities = judge.similarity_scores(reference, answer)

    with open('benchmark_ai_chatbot_cs/azure/results_mistral.csv', 'a') as results:
      results.write(f""""{question}",{score},{similarities[0]},{similarities[1]}\n""")


"""
Output example:

--- Combien de temps dure le stage de fin d'études ? 
[
  {
    'info': "Le stage de fin d'étude a une durée de 23 semaines",
    'source': 3
  }, 
  {
    'info': "Le stage de fin d'études a lieu à l'université",
    'source': 2
  },
  {
    'info': 'Le stage se réalise en entreprise ou en laboratoire de recherche à un poste de niveau ingénieur',
    'source': 2
  },
  {
    'info': "Le choix du sujet du stage est validé après consultation du maître de stage dans l'entreprise",
    'source': 2
  },
  {
    'info': 'Les responsables de la mention et de la filière valident le sujet du stage',
    'source': 2
  },
  {
    'info': "Un mémoire de fin d'études est rédigé à la fin du stage",
    'source': 2
  },
  {
    'info': "Le mémoire de fin d'études est présenté devant un jury pour sa validation",
    'source': 2
  }
]
"""

