import psycopg2, os, base64, openai
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("AZURE_POSTGRESQL_HOST")
dbname = os.getenv("AZURE_POSTGRESQL_DBNAME")
user = base64.b64decode(os.getenv("AZURE_POSTGRESQL_USER")).decode("utf-8")
password = base64.b64decode(os.getenv("AZURE_POSTGRESQL_PASSWORD")).decode("utf-8")
sslmode = os.getenv("AZURE_POSTGRESQL_SSLMODE")

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
emb_deployment = os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT")
gpt4_32k_deployment = os.getenv("AZURE_OPENAI_GPT4_32K_DEPLOYMENT")

DEFAULT_SYSTEM_PROMPT = """Tu es un assistant conversationnel de l'université. 
                    Tu peux répondre à des questions sur l'école, ses formations, ses activités, etc.
                    Tu peux aussi aider à trouver des informations sur le site de l'école.
                    Tu es poli et respectueux, et tu ne partages pas d'informations personnelles sur les utilisateurs.
                    Tu es un outil de communication et d'information, et tu es là pour aider les utilisateurs.
                    Tu es un assistant conversationnel de l'université nommé "BotCS".
                    Tes réponses sont succinctes, claires et précises, et tu ne laisses pas de place à l'erreur."""

class RAGResponse():
  def __init__(self, name: str, link: str | None, content: str) -> None:
    self.name = name
    self.link = link
    self.content = content


def addContext(query: str, context: list[RAGResponse]) -> str:

  if len(context) == 0:
    return f"""La question que je me posais était: '{query}'.
      Malheureusement, il n'y a pas de source fiable pour répondre à cette question.
      Réponds donc que tu ne peux pas répondre à la question, et propose à moi de te poser une autre question.
      Ne mentionne pas cette introduction dans ta réponse.
      """

  formattedDocs = ""
  for doc in context:
    formattedDocs += "<doc>\n"
    if doc.link:
      formattedDocs += f"<source>{doc.link}</source>\n"
    formattedDocs += doc.content + "\n</doc>\n"


  context_str = f"""Voici quelques documents qui sont en rapport avec la question suivante:
  '{query}'

  Ils sont écrits en français et en markdown, et tu peux identifier leur début et leur fin par la présence de tags <doc> et </doc>.
  Il est aussi possible qu'ils contiennent un tag <source> qui adresse leur source.

  Voici les documents:
  {formattedDocs}

  Tu dois répondre à la question en utilisant ces documents, et uniquement ces documents. 
  Il est impératif que toutes les informations que tu donnes soient issues de ces documents.
  Si tu as besoin de plus d'informations, tu peux me demander de te poser une autre question.
  Si tu ne comprends pas la question, tu dois le dire.
  Si la réponse semble ne pas être dans les documents, mais qu'une source fiable est mentionnée, tu peux rediriger l'utilisateur vers cette source, sans utiliser le tag <source>.
  Si la réponse à la question est "je ne sais pas", tu dois le dire.
  Ta réponse devra être en français et en markdown.
  Si tu as utilisé un document disposant d'une source, tu dois ajouter un tag <source> à la fin de ta réponse, suivi de cette source précisément. N'inclus pas de balises <doc> ou </doc> dans ta réponse, et n'inclus pas de balises <source> si cela n'est pas nécessaire.

  Réponds à la question posée, sans mentionner cette introduction, et sans mentionner que tu disposes de documents.
  L'information dans les documents fait partie de tes connaissances, et tu dois répondre à la question comme si tu savais la réponse. Il est inutile de faire référence aux documents, tu peux plutôt donner une réponse directe à la question posée, ou évoquer ces éléments comme provenant de tes connaissances.
  """

  return context_str



class RAG():
  def __init__(self) -> None:
    self.client = openai.AzureOpenAI(
      azure_endpoint=endpoint, 
      api_key=api_key, 
      api_version="2023-05-15"
    )

    # Connect to the database

    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    self.conn = psycopg2.connect(conn_string)

    self.cursor = self.conn.cursor()
  
  def get_data(self, question: str) -> list[RAGResponse]:
    embeddings = self.client.embeddings.create(
      model=emb_deployment,
      input=question
    )

    result: list[RAGResponse] = []

    if len(embeddings.data) > 0:
      self.cursor.execute("SELECT * FROM dataset WHERE embeddings <=> %s > 0.1 ORDER BY embeddings <=> %s LIMIT 3;", (str(embeddings.data[0].embedding), str(embeddings.data[0].embedding),))
      rows = self.cursor.fetchall()
      for row in rows:
        result.append(RAGResponse(row[1], row[2], row[3]))
    
    return result
  
  def close(self):
    self.cursor.close()
    self.conn.close()
  
  def __del__(self):
    self.close()


class BotCS():
  def __init__(self, system_prompt = DEFAULT_SYSTEM_PROMPT):
    self.system_prompt = system_prompt
    self.message = [{"role":"system","content":self.system_prompt}]
    self.chat_history = []

    self.client = openai.AzureOpenAI(
      azure_endpoint=endpoint, 
      api_key=api_key, 
      api_version="2023-05-15"
    )

    self.rag = RAG()

  def request(self, new_query):

    rag_response = self.rag.get_data(new_query)
    query_with_context = addContext(new_query, rag_response)

    if len(self.chat_history) > 5:
        self.chat_history = self.chat_history[-5:]

    for human, assistant in self.chat_history:
        self.message.append({"role":"user", "content":human})
        self.message.append({"role":"assistant", "content":assistant})
    
    if new_query != '':
        self.message.append({"role":"user", "content":query_with_context})

    response = self.client.chat.completions.create(
      model=gpt4_32k_deployment,
      messages=self.message
    )

    self.message = [{"role":"system","content":self.system_prompt}]

    self.chat_history.append([new_query, response.choices[0].message.content])

    return response.choices[0].message.content
  

  def close(self):
    self.rag.close()

  def __del__(self):
    self.close()


# Example usage
if __name__ == "__main__":
  chatbot = BotCS()

  print("BotCS>: Bonjour, je suis BotCS, l'assistant conversationnel de l'université. Comment puis-je vous aider ?")
  while True:
    query = input("You>: ")
    if query == "exit":
      break
    response = chatbot.request(query)
    print("BotCS>:", response)
