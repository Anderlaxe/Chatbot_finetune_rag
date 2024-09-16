import psycopg2, os, base64, openai
from dotenv import load_dotenv
import json

load_dotenv()

# Update connection strings information

host = os.getenv("AZURE_POSTGRESQL_HOST")
dbname = os.getenv("AZURE_POSTGRESQL_DBNAME")
user = base64.b64decode(os.getenv("AZURE_POSTGRESQL_USER")).decode("utf-8")
password = base64.b64decode(os.getenv("AZURE_POSTGRESQL_PASSWORD")).decode("utf-8")
sslmode = os.getenv("AZURE_POSTGRESQL_SSLMODE")

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
emb_deployment = os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT")

# Connect to the OpenAI API

client = openai.AzureOpenAI(
  azure_endpoint=endpoint, 
  api_key=api_key, 
  api_version="2023-05-15"
)

# Connect to the database

conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
conn = psycopg2.connect(conn_string)
print("Connection established")

cursor = conn.cursor()

# Drop previous table of same name if one exists

cursor.execute("DROP TABLE IF EXISTS dataset;")
print("Finished dropping table (if existed)")


# Create a table
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
cursor.execute("CREATE TABLE dataset (id serial PRIMARY KEY, name VARCHAR(50), link TEXT, content TEXT, embeddings vector(1536));")
print("Finished creating table")

# Insert data into the table

with open("../scrapping/contents/database.json", "r", encoding="utf-8") as f:
  data = json.load(f)
  for entry in data:
    print("Inserting data for: ", entry["filename"])
    embeddings = client.embeddings.create(
      model=emb_deployment,
      input=entry["content"]
    )

    if len(embeddings.data) > 0:
      cursor.execute("INSERT INTO dataset (name, link, content, embeddings) VALUES (%s, %s, %s, %s);", (entry["filename"][:-3], entry["link"] or "", entry["content"], embeddings.data[0].embedding))
    
                                

# Clean up

conn.commit()
print("Data committed")
cursor.close()
conn.close()