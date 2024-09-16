import psycopg2, os, base64, openai
from dotenv import load_dotenv
from numpy import dot
from numpy.linalg import norm

load_dotenv()

host = os.getenv("AZURE_POSTGRESQL_HOST")
dbname = os.getenv("AZURE_POSTGRESQL_DBNAME")
user = base64.b64decode(os.getenv("AZURE_POSTGRESQL_USER")).decode("utf-8")
password = base64.b64decode(os.getenv("AZURE_POSTGRESQL_PASSWORD")).decode("utf-8")
sslmode = os.getenv("AZURE_POSTGRESQL_SSLMODE")

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
emb_deployment = os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT")
gpt4_deployment = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT")

class GPTJudge():
  def __init__(self) -> None:
    self.client = openai.AzureOpenAI(
      azure_endpoint=endpoint, 
      api_key=api_key, 
      api_version="2023-05-15"
    )
  
  def embeddings_score(self, reference: str, comparison: str) -> float:
    embeddings_reference = self.client.embeddings.create(
      model=emb_deployment,
      input=reference
    )
    emb_ref = embeddings_reference.data[0].embedding

    embeddings_comparison = self.client.embeddings.create(
      model=emb_deployment,
      input=comparison
    )
    emb_comp = embeddings_comparison.data[0].embedding

    return dot(emb_ref, emb_comp)/(norm(emb_ref)*norm(emb_comp))
  
  def similarity_scores(self, reference: str, comparison: str) -> tuple[float, float]:
    example = """<result>[{"info": "Il fait beau", "source": 1}, {"info": "Il fait chaud", "source": 2}, {"info": "Il fait beau et chaud", "source": 3}]</result>"""
    message = [
      {
        "role": "system",
        "content": """Tu es un GPT Judge. 
        Cela signifie que tu es capable de comparer deux textes et de donner une note de similarité entre eux.
        Tu es impartial et rigoureux, tu respecte scrupuleusement les consignes et tu ne laisses pas de place à l'erreur.
        Tu as une grande capacité de concentration et tu es capable de travailler sur le sens et les informations présentes dans les textes, ainsi que d'effectuer des raisonnements logiques.
        Tes réponses sont précises, et motivées par des éléments concrets et vérifiables, et tu démontres ton raisonnement avant même de donner une réponse.
        """
      },
      {
        "role": "user",
        "content": f"""Voici deux courts textes que je voudrais comparer.
        Le premier texte est le suivant: "{reference}".
        Le second texte est le suivant: "{comparison}".

        Analyse les informations présentes dans chacun de ces textes, de manière succincte, mais en prenant bien soin de traiter chaque information présente dans les texte. Il est extrêmement important que tu sois exhaustif.

        Maintenant, tu vas suivre ces consignes très précisément, pour que ton message puisse être automatiquement compris par un programme. Tu vas rédiger une liste unique, qui compile l'ensemble des informations identifiées dans les deux textes. Il est crucial que tu respectes un format très strict. Cette liste doit commencer et se finir par des crochets []. Chaque élément de la liste doit être un objet JSON, identifié par des crochets. Chaque objet doit contenir 2 champs: "info" et "source". Le champ "info" doit contenir une information identifiée dans les textes, et le champ "source" doit contenir un entier, qui indique la provenance de l'information. Si l'information provient du premier texte, tu dois mettre 1, si elle provient du second texte, tu dois mettre 2. Si l'information est présente dans les deux textes, tu dois mettre 3.
        Entoure cette liste par des tags <result> et </result> pour que le programme puisse l'identifier.
        Par exemple : {example}.

        Tu peux faire preuve de discernement et de synthèse pour identifier si une information est présente dans les deux textes ou non. Si une information est sémantiquement similaire à une autre, mais qu'elle n'est pas écrite de la même manière, tu peux indiquer 3. Ne sois pas trop rigoureux avec le sens précis des mots, il est important de prendre en compte le sens général des phrases.

        Tu peux maintenant commencer à rédiger ta liste.
        """
      }
    ]

    response = self.client.chat.completions.create(
      model=gpt4_deployment,
      messages=message
    )

    reponse_text = response.choices[0].message.content

    response_list = reponse_text.split("<result>")[1].split("</result>")[0]

    response_doc = eval(response_list)
    print(response_doc)

    reflen, complen, inter, diff = 0, 0, 0, 0
    for doc in response_doc:
      if doc["source"] == 1:
        reflen += 1
      elif doc["source"] == 2:
        complen += 1
        diff += 1
      elif doc["source"] == 3:
        reflen += 1
        complen += 1
        inter += 1
    
    if reflen == 0:
      reflen = 1
    if complen == 0:
      complen = 1
    
    similarity_score = inter/(reflen)
    uncertainty = diff/(complen)

    return similarity_score, uncertainty

# Example usage
if __name__ == "__main__":
  judge = GPTJudge()

  reference = """Il est possible de changer de LV2 entre la première et la deuxième année sous certaines conditions. Pour cela veuilez contacter le département langues de la scolarité.
  """

  comparison = """Pour changer de Langue Vivante 2 (LV2) entre la première année (1A) et la deuxième année (2A), il faut adresser une demande de changement au Département des Langues et Cultures (DLC) trois semaines avant la première semaine de cours du septième semestre (S7). Il est important que cette demande soit basée sur un projet mûrement réfléchi, comme par exemple, un S8 à l'étranger. Le DLC étudiera la demande en tenant compte du projet, des compétences de l'élève en langues vivantes et des effectifs.

  En cas de difficulté rencontrée en 2ème année, il est possible de revenir à sa LV2 initiale en S9. L'élève s'engage à obtenir le niveau requis pour la diplomation sur l'une ou l'autre des LV2 s'il y a eu un changement en cours de scolarité.

  Aussi, une demande de changement de LV2 pourrait être faite après un retour de césure, de semestre ou de stage à l'étranger. Le DLC étudiera cette demande en fonction du niveau de l'élève dans sa LV2 d'origine (1A ou 2A), et de son niveau dans la langue qu'il souhaite suivre en 3A. Il est à noter que pour tout changement de LV2 en troisième année, un niveau B1 minimum est requis.

  Enfin, les élèves peuvent suivre une autre langue en qualité d'auditeur libre, en fonction des places disponibles. Cela concerne les élèves ayant obtenu un Test de connaissance du français (TDC) en Français Langue Étrangère (FLE) ou bien ceux projetant une mobilité internationale. Les élèves devront alors compléter la charte correspondante lors de l'inscription."""

  print(judge.similarity_scores(reference, comparison))
  print(judge.embeddings_score(reference, comparison))
