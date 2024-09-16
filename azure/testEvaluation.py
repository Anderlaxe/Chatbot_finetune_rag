from botCS import BotCS
from gptJudge import GPTJudge
import json, tqdm

dataset = []

with open('../database/test_base.json') as f:
    data = json.load(f)
    dataset = data['dataset']

to_skip = 0
with open('results.csv', 'r') as results:
  to_skip = len(results.readlines()) - 1
if to_skip == 0:
  with open('results.csv', 'w') as results:
    results.write("question,embeddings,similarity,uncertainty\n")

judge = GPTJudge()
for info in tqdm.tqdm(dataset[to_skip:]):
    bot = BotCS()

    question = info['question']
    print("--- " + question)
    reference = info['answer']
    if (reference == ''):
        if info['error']['message']:
            reference = info['error']['message']
    
    comparison = bot.request(question)
    score = judge.embeddings_score(reference, comparison)
    similarities = judge.similarity_scores(reference, comparison)

    with open('results.csv', 'a') as results:
      results.write(f""""{question}",{score},{similarities[0]},{similarities[1]}\n""")
    
    del bot


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

