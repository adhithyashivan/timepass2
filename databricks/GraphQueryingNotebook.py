# Databricks notebook source
# MAGIC %pip install gremlinpython openai

# COMMAND ----------

import openai
from gremlin_python.process.traversal import TextP
from gremlin_python.driver import client, serializer

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

# COMMAND ----------

jira_id = 'JIRA-301'  # Replace with input

query = f"""
g.V().has('id', '{jira_id}')
  .bothE().otherV().path().by(valueMap(true))
"""
results = gremlin_client.submit(query).all().result()

for r in results:
    print(r)

# COMMAND ----------

cr_id = 'CR-205'  # Replace with any CR ID

query = f"""
g.V().has('id', '{cr_id}')
  .in('MENTIONS')  // Jira nodes
  .bothE().otherV().path().by(valueMap(true))
"""
results = gremlin_client.submit(query).all().result()

for r in results:
    print(r)

# COMMAND ----------


keyword = 'login'  # Replace with input

query = f"""
g.V().or(
    has('doc_topic', TextP.containing('{keyword}')),
    has('jira_summary', TextP.containing('{keyword}')),
    has('cr_title', TextP.containing('{keyword}'))
).bothE().otherV().path().by(valueMap(true))
"""
results = gremlin_client.submit(query).all().result()

for r in results:
    print(r)

# COMMAND ----------

graph_context = ""
for r in results:
    graph_context += f"{r}\n"

prompt = f"""
Given the following graph context, answer the user's question:

{graph_context}

User question: <replace with user's question>
Answer:
"""

# COMMAND ----------

print("Vertices:", gremlin_client.submit("g.V().count()").all().result())
print("Edges:", gremlin_client.submit("g.E().count()").all().result())

# COMMAND ----------

gremlin_client.submit("g.V().hasLabel('CR').valueMap(true)").all().result()

# COMMAND ----------

gremlin_client.submit("g.E().valueMap(true)").all().result()

# COMMAND ----------


def build_graph_context(jira_id=None, cr_id=None, keyword=None):
    if jira_id:
        query = f"""g.V().has('id', '{jira_id}').bothE().otherV().path().by(valueMap(true))"""
    elif cr_id:
        query = f"""g.V().has('id', '{cr_id}').in('MENTIONS').bothE().otherV().path().by(valueMap(true))"""
    elif keyword:
        query = f"""g.V().or(
                        has('doc_topic', textContains('{keyword}')),
                        has('jira_summary', textContains('{keyword}')),
                        has('cr_title', textContains('{keyword}'))
                    ).bothE().otherV().path().by(valueMap(true))"""
    else:
        return "No valid input provided."

    results = gremlin_client.submit(query).all().result()

    # Flatten and format
    context = ""
    for r in results:
        if isinstance(r, dict):
            for k, v in r.items():
                context += f"{k}: {v}\n"
            context += "\n---\n"
        elif isinstance(r, list):  # In case of a path object
            for node in r:
                if isinstance(node, dict):
                    for k, v in node.items():
                        context += f"{k}: {v}\n"
                    context += "\n---\n"

    # Add Global Context: All Jira/CR/Confluence
    context += "\n=== Global Jira Data ===\n"
    all_jira = gremlin_client.submit(
        "g.V().hasLabel('Jira').valueMap(true)").all().result()
    for r in all_jira:
        for k, v in r.items():
            context += f"{k}: {v}\n"
        context += "\n---\n"

    context += "\n=== Global CR Data ===\n"
    all_cr = gremlin_client.submit(
        "g.V().hasLabel('CR').valueMap(true)").all().result()
    for r in all_cr:
        for k, v in r.items():
            context += f"{k}: {v}\n"
        context += "\n---\n"

    context += "\n=== Global Confluence Data ===\n"
    all_conf = gremlin_client.submit(
        "g.V().hasLabel('Confluence').valueMap(true)").all().result()
    for r in all_conf:
        for k, v in r.items():
            context += f"{k}: {v}\n"
        context += "\n---\n"

    return context

# COMMAND ----------


client = openai.AzureOpenAI(
    REMOVED_SECRET,
    api_version="2023-12-01-preview",
    azure_endpoint="https://hackathongraphragopenai.openai.azure.com/"
)

# COMMAND ----------

user_question = "When was this jira created??"

context = build_graph_context(jira_id="JIRA-302")
print(context)
final_prompt = f"""
You are a helpful assistant answering questions based on the following GraphRAG context:
Get the complete context as provided below and answer the user's question. 
{context}

User's question: {user_question}
Answer:
"""

# Send to OpenAI
response = client.chat.completions.create(
    model="gpt-4-completion",
    messages=[{"role": "user", "content": final_prompt}],
    max_tokens=1000
)

print(response.choices[0].message.content)

# COMMAND ----------

# from fastapi import FastAPI, Query
# from pydantic import BaseModel
# import asyncio
# import nest_asyncio
# import openai

# client = openai.AzureOpenAI(
# REMOVED_SECRET,
# api_version="2023-12-01-preview",
# azure_endpoint="https://hackathongraphragopenai.openai.azure.com/"
# )

# # For Databricks notebook
# nest_asyncio.apply()

# app = FastAPI(title="GraphRAG API")

# @app.get("/")
# def read_root():
#     return {"message": "GraphRAG API is up and running!"}

# from typing import Optional

# @app.get("/query")
# async def query_graph(
#     jira_id: Optional[str] = Query(None),
#     cr_id: Optional[str] = Query(None),
#     keyword: Optional[str] = Query(None),
# ):

#     # Run Graph Query
#     context = build_graph_context(jira_id=jira_id, cr_id=cr_id, keyword=keyword)

#     # Prepare prompt for OpenAI
#     user_question = f"Give me details about {jira_id or cr_id or keyword}"
#     final_prompt = f"""
#     You are a helpful assistant answering questions based on the following GraphRAG context:
#     {context}

#     User's question: {user_question}
#     Answer:
#     """

#     # Call Azure OpenAI (use azure-openai client)
#     response = client.chat.completions.create(
#         model="gpt-4-turbo",
#         messages=[{"role": "user", "content": final_prompt}],
#         max_tokens=1000
#     )

#     return {"answer": response.choices[0].message.content}

# import uvicorn

# uvicorn.run(app, host="0.0.0.0", port=8000)
