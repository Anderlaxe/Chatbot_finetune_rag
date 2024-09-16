from gptJudge import GPTJudge
import json, tqdm

dataset = []

with open('./database/test_base_results_mistral_intel.json') as f:
    data = json.load(f)
    dataset = data['dataset']

PATH_CSV = 'azure/results_mistral_intel.csv'

to_skip = 0
with open(PATH_CSV, 'r') as results:
  to_skip = len(results.readlines()) - 1
if to_skip == 0:
  with open(PATH_CSV, 'w') as results:
    results.write("question,embeddings,similarity,uncertainty\n")

judge = GPTJudge()
for info in tqdm.tqdm(dataset[to_skip:]):

    question = info['question']
    print("--- " + question)
    reference = info['answer']
    if (reference == ''):
        if info['error']['message']:
            reference = info['error']['message']
    
    comparison = info['answer_mistral']
    score = judge.embeddings_score(reference, comparison)
    similarities = judge.similarity_scores(reference, comparison)

    with open(PATH_CSV, 'a') as results:
      results.write(f""""{question}",{score},{similarities[0]},{similarities[1]}\n""")
