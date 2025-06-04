from fastapi import FastAPI, Query
from pydantic import BaseModel
import asyncio
import nest_asyncio
import openai

client = openai.AzureOpenAI(
REMOVED_SECRET,
api_version="2023-12-01-preview",
azure_endpoint="https://hackathongraphragopenai.openai.azure.com/"
)

# For Databricks notebook
nest_asyncio.apply()

app = FastAPI(title="GraphRAG API")

@app.get("/")
def read_root():
    return {"message": "GraphRAG API is up and running!"}

from typing import Optional

@app.get("/query")
async def query_graph(
    jira_id: Optional[str] = Query(None),
    cr_id: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
):

    # Run Graph Query
    context = build_graph_context(jira_id=jira_id, cr_id=cr_id, keyword=keyword)

    # Prepare prompt for OpenAI
    user_question = f"Give me details about {jira_id or cr_id or keyword}"
    final_prompt = f"""
    You are a helpful assistant answering questions based on the following GraphRAG context:
    {context}
    
    User's question: {user_question}
    Answer:
    """

    # Call Azure OpenAI (use azure-openai client)
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=1000
    )

    return {"answer": response.choices[0].message.content}

import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)