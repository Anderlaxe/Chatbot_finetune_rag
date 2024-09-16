import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import a csv file with pandas
df = pd.read_csv('azure/results_gpt_judge/results_mixtral.csv')
# print(df.head())
print(df.describe())

# Open a txt file 
with open('azure/results_gpt_judge/output_mixtral.txt', 'r') as file:
    read_all = file.read()
    list_qa = read_all.split('---')

list_qa = list_qa[1:]

dico = {
    'question' : [],
    'answer' : [],
}

for qa in list_qa:
    qa = qa.split('\n')
    qa = qa[1:]
    try:
        if qa[0][:8] == 'question' and qa[1][:6] == 'answer':
            dico['question'].append(qa[0][11:])
            dico['answer'].append(qa[1][9:])
    except:
        pass

short_answer = []
for k in range(len(dico['answer'])):
    if len(dico['answer'][k]) < 5:
        # print(dico['question'][k])
        short_answer.append(k)
print("Nombre de réponses trop courtes :", len(short_answer))

error_answer = []
for k in range(len(dico['answer'])):
    if 'Erreur' in dico['answer'][k]:
        # print(dico['question'][k])
        error_answer.append(k)
print("Nombre d'erreurs : ", len(error_answer))

hs_answer = []
for k in range(len(dico['answer'])):
    if 'désolé' in dico['answer'][k]:
        # print(dico['question'][k])
        hs_answer.append(k)
print("Nombre de questions hors sujet : ", len(hs_answer))

delete = short_answer + error_answer + hs_answer
df = df.drop(delete)

print(df.describe())

# Display a histogram of the values of similarity  and uncertainty round to 1 decimal 
df['similarity_round'] = df['similarity'].apply(lambda x: round(x, 1))
df['uncertainty_round'] = df['uncertainty'].apply(lambda x: round(x, 1))
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.hist(df['similarity_round'], bins=10)
plt.title('Similarity')
plt.subplot(1, 2, 2)
plt.hist(df['uncertainty_round'], bins=10)
plt.title('Uncertainty')    
plt.show()
