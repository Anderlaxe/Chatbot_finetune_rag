import psycopg2, os, base64, openai
from dotenv import load_dotenv

def get_embedding(input):
    resu = ""
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
    # print("Connection established")

    cursor = conn.cursor()

    embeddings = client.embeddings.create(
    model=emb_deployment,
    input=input
    )

    if len(embeddings.data) > 0:
        cursor.execute("SELECT * FROM dataset WHERE embeddings <=> %s > 0.1 ORDER BY embeddings <=> %s LIMIT 3;", (str(embeddings.data[0].embedding), str(embeddings.data[0].embedding),))
        rows = cursor.fetchall()
    for row in rows:
        resu += str(row[3])
        resu += "\n"
    
    return resu
