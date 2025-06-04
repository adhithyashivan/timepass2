# Databricks notebook source
# MAGIC %pip install openai
# MAGIC %pip install azure-search-documents
# MAGIC %pip install databricks-vectorsearch
# MAGIC
# MAGIC

# COMMAND ----------

from gremlin_python.driver import client, serializer
import numpy as np
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField, VectorSearch, VectorSearchAlgorithmConfiguration, HnswAlgorithmConfiguration
import re
import json
import requests
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from azure.search.documents.indexes import SearchIndexClient
import time
from tqdm import tqdm
import openai
import uuid
from pyspark.sql import SparkSession
import pandas as pd

spark = SparkSession.builder.appName("GraphRAG-Vectorization").getOrCreate()

blob_container = "rawdata"
blob_account = "barclayshackathontest"
sas_token = "sp=racwdl&st=2025-05-31T17:31:00Z&se=2025-06-07T01:31:00Z&spr=https&sv=2024-11-04&sr=c&sig=JKsY%2BTJgtgeCctNHwkqFgc0USNz8fV8YWa%2F3Y1FFCSk%3D"

spark.conf.set(
    f"fs.azure.sas.{blob_container}.{blob_account}.blob.core.windows.net",
    sas_token
)

# Load CSVs
cr_main_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/CR_Main_csv.csv").toPandas()
ctask_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/CR_CTasks_csv.csv").toPandas()
jira_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/JIRA_Issues_Detailed_csv.csv").toPandas()
activity_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/JIRA_Activities_csv.csv").toPandas()
confluence_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/Confluence_Pages_Detailed_csv.csv").toPandas()

print("Data loaded.")

# COMMAND ----------


def flatten_row(row):
    return ' | '.join([f"{col}: {str(row[col])}" for col in row.index if pd.notna(row[col])])


def chunk_dataframe(df, node_type, id_field):
    chunks = []
    for _, row in df.iterrows():
        text = flatten_row(row)
        chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "node_id": row[id_field],
            "node_type": node_type,
            "text": text
        })
    return chunks


# Generate chunks from all datasets
cr_chunks = chunk_dataframe(cr_main_df, "CR", "CR_ID")
ctask_chunks = chunk_dataframe(ctask_df, "CTASK", "CTASK_ID")
jira_chunks = chunk_dataframe(jira_df, "JIRA", "JIRA_ID")
activity_chunks = chunk_dataframe(activity_df, "ACTIVITY", "Activity_ID")
confluence_chunks = chunk_dataframe(
    confluence_df, "CONFLUENCE", "Confluence_ID")

all_chunks = cr_chunks + ctask_chunks + \
    jira_chunks + activity_chunks + confluence_chunks
print(f"Total chunks: {len(all_chunks)}")

# COMMAND ----------


client = openai.AzureOpenAI(
    REMOVED_SECRET,
    api_version="2023-12-01-preview",
    azure_endpoint="https://hackathongraphragopenai.openai.azure.com/"
)

deployment_name = "text-embedding-ada-002-hackathon"

# COMMAND ----------


BATCH_SIZE = 10
embedding_results = []

for i in tqdm(range(0, len(all_chunks), BATCH_SIZE)):
    batch = all_chunks[i:i + BATCH_SIZE]
    texts = [item["text"] for item in batch]

    try:
        response = client.embeddings.create(
            model=deployment_name,
            input=texts
        )
        embeddings = [e.embedding for e in response.data]
        for j, item in enumerate(batch):
            item["embedding"] = embeddings[j]
            embedding_results.append(item)
    except Exception as e:
        print(f"Failed batch {i}-{i + BATCH_SIZE}: {e}")
        time.sleep(5)

# COMMAND ----------


# COMMAND ----------

# AI Search Schema
{
    "fields": [
        {"name": "chunk_id", "type": "Edm.String", "key": True},
        {"name": "node_id", "type": "Edm.String"},
        {"name": "node_type", "type": "Edm.String"},
        {"name": "text", "type": "Edm.String"},
        {"name": "embedding", "type": "Collection(Edm.Single)",
         "dimensions": 1536, "vectorSearchConfiguration": "vector-config"}
    ]
}

# COMMAND ----------


endpoint = "https://graphrag-aisearch-hackathon.search.windows.net"
key = "DcKMyEEXGlGebvWMixtMYm4xMKjtKUyhnNxQzRNxqkAzSeBgRV4M"
index_name = "graphrag-index"

client = SearchIndexClient(endpoint, AzureKeyCredential(key))

# Define vector config
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw-config", kind="hnsw", parameters={"m": 4, "efConstruction": 400})
    ],
    profiles=[
        VectorSearchProfile(name="vector-config",
                            algorithm_configuration_name="hnsw-config")
    ]
)

# Define index schema
index = SearchIndex(
    name=index_name,
    fields=[
        SimpleField(name="chunk_id", type="Edm.String", key=True),
        SimpleField(name="node_id", type="Edm.String", filterable=True),
        SimpleField(name="node_type", type="Edm.String", filterable=True),
        SearchableField(name="text", type="Edm.String"),
        SearchableField(
            name="embedding",
            dimensions=1536,
            vector_search_profile="vector-config"
        )
    ],
    vector_search=vector_search
)

# Create index
client.create_index(index)
print("✅ Azure AI Search index created with vector config.")

# COMMAND ----------


search_client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

# Example upload from `embedding_results`
docs = [{
    "chunk_id": item["chunk_id"],
    "node_id": item["node_id"],
    "node_type": item["node_type"],
    "text": item["text"],
    "embedding": str(item["embedding"])  # Ensure embedding is a string
} for item in embedding_results]

search_client.upload_documents(docs)
print("✅ Uploaded all embedding chunks to Azure AI Search.")

# COMMAND ----------

deployment_name = "text-embedding-ada-002-hackathon"
client = AzureOpenAI(
    REMOVED_SECRET,
    api_version="2023-05-15",
    azure_endpoint="https://hackathongraphragopenai.openai.azure.com/"
)


def get_azure_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=[text],
        model=deployment_name  # This is your DEPLOYMENT NAME, not model name!
    )
    return response.data[0].embedding


# Example usage
user_query = "What CRs are related to payment processing issues?"
query_embedding = get_azure_embedding(user_query)

# COMMAND ----------


# Config
search_endpoint = "https://graphrag-aisearch-hackathon.search.windows.net"
index_name = "graphrag-index"
REMOVED_SECRET
search_url = f"{search_endpoint}/indexes/{index_name}/docs/search?api-version=2023-11-01"

# Generate embedding from your function
embedded_query = get_azure_embedding(
    "What CRs are related to payment processing issues?")

# ✅ Corrected payload
vector_search_payload = {
    "vectors": [
        {
            "value": embedded_query,
            "fields": "embedding",
            "k": 5
        }
    ]
}

headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# Perform vector search
response = requests.post(search_url, headers=headers,
                         data=json.dumps(vector_search_payload))

# Parse response
if response.status_code == 200:
    results = response.json()["value"]
    print("Top 5 results for user query:")
    for idx, result in enumerate(results):
        print(f"\nResult #{idx+1}")
        print(f"Node ID: {result.get('node_id')}")
        print(f"Node Type: {result.get('node_type')}")
        print(f"Text: {result.get('text', '')[:300]}...")
else:
    print(f"Vector search failed: {response.status_code}")
    print(response.text)

# COMMAND ----------

response = client.embeddings.create(
    input=["Your text goes here", "Your text goes here and there"],
    model=deployment_name  # This must match your Azure OpenAI deployment name
)

embedding_vector = response.data[0]

print(embedding_vector)

# COMMAND ----------


BATCH_SIZE = 10
embedding_results = []


def get_embeddings_azure(texts):
    response = client.embeddings.create(
        input=texts,
        model=deployment_name
    )
    return [e["embedding"] for e in response["data"]]


# Batch embedding for all chunks
for i in tqdm(range(0, len(all_chunks), BATCH_SIZE)):
    batch = all_chunks[i:i + BATCH_SIZE]
    texts = [item["text"] for item in batch]

    try:
        embeddings = get_embeddings_azure(texts)
        for j, item in enumerate(batch):
            item["embedding"] = embeddings[j]
            embedding_results.append(item)
    except Exception as e:
        print(f"Embedding batch failed at {i}: {e}")
        continue

# COMMAND ----------

text-embedding-ada-002-hackathon

# COMMAND ----------


def chunk_text(text, max_tokens=200):
    # Naive split by sentence
    sentences = re.split(r'(?<=[.!?]) +', text or "")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len((current_chunk + sentence).split()) <= max_tokens:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


# Explode each doc_content into multiple rows (node_id, node_type, text_chunk)
rows = []
for _, row in confluence_df.iterrows():
    chunks = chunk_text(row["doc_content"])
    for i, chunk in enumerate(chunks):
        rows.append({
            "node_id": row["Confluence_ID"],
            "node_type": "Confluence",
            "text": chunk,
            "chunk_id": f"{row['Confluence_ID']}_chunk_{i}"
        })

chunks_df = pd.DataFrame(rows)


# --------------Until Here-----------------------------


openai.api_type = "azure"
openai.api_base = "https://<your-resource-name>.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "<your-api-key>"

deployment_name = "<your-embedding-deployment-name>"


def get_embedding(text):
    try:
        response = openai.Embedding.create(
            input=text,
            engine=deployment_name
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error embedding: {e}")
        return None


# Embed with sleep to avoid rate limit
embeddings = []
for i, row in chunks_df.iterrows():
    embedding = get_embedding(row["text"])
    embeddings.append(embedding)
    time.sleep(0.3)  # optional sleep to avoid hitting rate limit

chunks_df["embedding"] = embeddings


search_service_endpoint = "https://<your-search-service>.search.windows.net"
admin_key = "<your-admin-key>"
index_name = "graphrag-index"

index_client = SearchIndexClient(
    endpoint=search_service_endpoint,
    credential=AzureKeyCredential(admin_key)
)

# Define the index schema
fields = [
    SimpleField(name="chunk_id", type="Edm.String", key=True),
    SimpleField(name="node_id", type="Edm.String",
                filterable=True, sortable=True),
    SimpleField(name="node_type", type="Edm.String",
                filterable=True, sortable=True),
    SearchableField(name="text", type="Edm.String"),
    SimpleField(name="embedding", type="Collection(Edm.Single)", searchable=True,
                vector_search_dimensions=1536, vector_search_configuration="default")
]

vector_config = VectorSearch(algorithm_configurations=[
    VectorSearchAlgorithmConfiguration(
        name="default",
        kind="hnsw",
        hnsw=HnswAlgorithmConfiguration()
    )
])

index = SearchIndex(name=index_name, fields=fields,
                    vector_search=vector_config)

# Create the index
if not index_client.get_index(index_name):
    index_client.create_index(index)


search_client = SearchClient(
    endpoint=search_service_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(admin_key)
)

# Convert float64 embeddings to float32
chunks_df["embedding"] = chunks_df["embedding"].apply(
    lambda x: [float(np.float32(val)) for val in x])

# Prepare docs for upload
docs = []
for _, row in chunks_df.iterrows():
    docs.append({
        "chunk_id": row["chunk_id"],
        "node_id": row["node_id"],
        "node_type": row["node_type"],
        "text": row["text"],
        "embedding": row["embedding"]
    })

# Upload in batches
batch_size = 1000
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    search_client.upload_documents(documents=batch)

print("Embeddings uploaded to Azure AI Search ✅")

# COMMAND ----------

# Search Query


# Azure OpenAI Embedding Setup
openai_client = AzureOpenAI(
    azure_endpoint="https://<your-openai-endpoint>.openai.azure.com/",
    api_key="<your-openai-key>",
    api_version="2024-03-01-preview"
)


def embed_query(query):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    return response.data[0].embedding


# Azure AI Search Setup
search_client = SearchClient(
    endpoint="https://<your-search-service>.search.windows.net",
    index_name="graphrag-index",
    credential=AzureKeyCredential("<your-search-key>")
)

query = "What are the recent issues related to login failure?"
query_vector = embed_query(query)

# Perform vector search
results = search_client.search(
    search_text=None,
    vector=query_vector,
    top_k=5,
    vector_fields="embedding"
)

top_chunks = []
for r in results:
    top_chunks.append({
        "chunk_id": r["chunk_id"],
        "node_id": r["node_id"],
        "node_type": r["node_type"],
        "text": r["text"]
    })

print("Top chunks from vector search:")
for c in top_chunks:
    print(f"- {c['node_type']} {c['node_id']}:\n{c['text'][:200]}...\n")

# COMMAND ----------

# Build Context


def get_node_context(node_id):
    gremlin_query = f"""
    g.V().has('id', '{node_id}')
      .bothE().as('e').otherV().as('v')
      .select('e', 'v')
    """
    results = gremlin_client.submit(gremlin_query).all().result()

    context_lines = [f"--- Related to node {node_id} ---"]
    for r in results:
        edge = r["e"].label
        connected_id = r["v"].id
        connected_type = r["v"].label
        context_lines.append(f"{edge} → {connected_type} [{connected_id}]")
    return "\n".join(context_lines)


# Show enriched context for each top chunk
for chunk in top_chunks:
    print(
        f"\n### Context for {chunk['node_type']} {chunk['node_id']}:\n{chunk['text']}\n")
    print(get_node_context(chunk["node_id"]))

# COMMAND ----------


spark = SparkSession.builder.appName("GraphRAGIngestion").getOrCreate()

blob_container = "rawdata"
blob_account = "barclayshackathontest"
# Replace with actual SAS token
sas_token = "sp=racwdl&st=2025-05-31T17:31:00Z&se=2025-06-07T01:31:00Z&spr=https&sv=2024-11-04&sr=c&sig=JKsY%2BTJgtgeCctNHwkqFgc0USNz8fV8YWa%2F3Y1FFCSk%3D"

# Configure access
spark.conf.set(
    f"fs.azure.sas.{blob_container}.{blob_account}.blob.core.windows.net", sas_token)

# Load CSVs
cr_main_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/CR_Main_csv.csv").toPandas()
ctask_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/CR_CTasks_csv.csv").toPandas()
jira_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/JIRA_Issues_Detailed_csv.csv").toPandas()
activity_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/JIRA_Activities_csv.csv").toPandas()
confluence_df = spark.read.option("header", True).csv(
    f"wasbs://{blob_container}@{blob_account}.blob.core.windows.net/Confluence_Pages_Detailed_csv.csv").toPandas()

print("Data loaded from Blob Storage!")

# Cosmos DB Config
cosmos_endpoint = "wss://hackathon-cosmosdb.gremlin.cosmos.azure.com:443/"
cosmos_key = "REMOVED_SECRET"
database = "graphrag"
container = "hackathongraph"

gremlin_client = client.Client(
    f"{cosmos_endpoint}",
    "g",
    username=f"/dbs/{database}/colls/{container}",
    password=cosmos_key,
    message_serializer=serializer.GraphSONSerializersV2d0()
)

print("Connected to Cosmos DB Graph!")

# Helper Function to Format Properties


def safe_props(row, columns):
    prop_list = []
    for col in columns:
        value = str(row[col]).replace('"', '\\"')
        prop_list.append(f'.property("{col}", "{value}")')
    return ''.join(prop_list)

# Helper Function to Check if Vertex Exists


def vertex_exists(vertex_id):
    result = gremlin_client.submit(
        f"g.V().has('id', '{vertex_id}').count()").all().result()
    return result[0] > 0


# Create Team Nodes
unique_teams = set(cr_main_df['CR_Team_Assignment_Group']).union(set(
    jira_df['JIRA_Team'])).union(set(confluence_df['Confluence_Team_Association']))
for team in unique_teams:
    team_id = f"TEAM-{team.replace(' ', '_')}"
    if not vertex_exists(team_id):
        gremlin_client.submit(f"""
            g.addV('Team').property('id', '{team_id}').property('team_name', '{team}').property('vertexType', 'Team')
        """).all().result()

# Create CR Nodes + BELONGS_TO
for _, row in cr_main_df.iterrows():
    cr_id = row['CR_ID']
    team_id = f"TEAM-{row['CR_Team_Assignment_Group'].replace(' ', '_')}"
    props = safe_props(row, cr_main_df.columns)
    if not vertex_exists(cr_id):
        gremlin_client.submit(
            f"""g.addV('CR').property('id', '{cr_id}').property('vertexType', 'CR'){props}""").all().result()
    gremlin_client.submit(
        f"""g.V().has('id', '{cr_id}').addE('BELONGS_TO').to(g.V().has('id', '{team_id}'))""").all().result()

# Create JIRA Nodes + BELONGS_TO
for _, row in jira_df.iterrows():
    jira_id = row['JIRA_ID']
    team_id = f"TEAM-{row['JIRA_Team'].replace(' ', '_')}"
    props = safe_props(row, jira_df.columns)
    if not vertex_exists(jira_id):
        gremlin_client.submit(
            f"""g.addV('JIRA').property('id', '{jira_id}').property('vertexType', 'JIRA'){props}""").all().result()
    gremlin_client.submit(
        f"""g.V().has('id', '{jira_id}').addE('BELONGS_TO').to(g.V().has('id', '{team_id}'))""").all().result()

# Create Confluence Nodes + BELONGS_TO
for _, row in confluence_df.iterrows():
    conf_id = row['Confluence_ID']
    team_id = f"TEAM-{row['Confluence_Team_Association'].replace(' ', '_')}"
    props = safe_props(row, confluence_df.columns)
    if not vertex_exists(conf_id):
        gremlin_client.submit(
            f"""g.addV('Confluence').property('id', '{conf_id}').property('vertexType', 'Confluence'){props}""").all().result()
    gremlin_client.submit(
        f"""g.V().has('id', '{conf_id}').addE('BELONGS_TO').to(g.V().has('id', '{team_id}'))""").all().result()

# Create REFERS_TO, MENTIONS, and other edges
for _, row in cr_main_df.iterrows():
    if pd.notna(row['Linked_Jira_ID']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['CR_ID']}').addE('REFERS_TO').to(g.V().has('id', '{row['Linked_Jira_ID']}'))""").all().result()
    if pd.notna(row['Linked_Confluence_ID']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['CR_ID']}').addE('REFERS_TO').to(g.V().has('id', '{row['Linked_Confluence_ID']}'))""").all().result()

for _, row in jira_df.iterrows():
    if pd.notna(row['CR_ID_Link_From_CSV_Example']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['JIRA_ID']}').addE('MENTIONS').to(g.V().has('id', '{row['CR_ID_Link_From_CSV_Example']}'))""").all().result()
    if pd.notna(row['JIRA_Linked_Issue_ID_Target']) and pd.notna(row['JIRA_Link_Type']):
        gremlin_client.submit(
            f"""g.V().has('id', '{row['JIRA_ID']}').addE('{row['JIRA_Link_Type']}').to(g.V().has('id', '{row['JIRA_Linked_Issue_ID_Target']}'))""").all().result()

for _, row in confluence_df.iterrows():
    if pd.notna(row['Confluence_Linked_Jira_ID']):
        for j in str(row['Confluence_Linked_Jira_ID']).split(';'):
            if j:
                gremlin_client.submit(
                    f"""g.V().has('id', '{row['Confluence_ID']}').addE('REFERS_TO').to(g.V().has('id', '{j}'))""").all().result()
    if pd.notna(row['Confluence_Linked_CR_ID']):
        for c in str(row['Confluence_Linked_CR_ID']).split(';'):
            if c:
                gremlin_client.submit(
                    f"""g.V().has('id', '{row['Confluence_ID']}').addE('REFERS_TO').to(g.V().has('id', '{c}'))""").all().result()

print("Data loaded and hierarchical ingestion complete! 🚀")
