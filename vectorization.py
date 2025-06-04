import os
import requests
from openai import AzureOpenAI

# === 1. CONFIGURATION ===

# Azure OpenAI
AZURE_OPENAI_KEY = "your-openai-key"
AZURE_OPENAI_ENDPOINT = "https://your-openai-resource.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT = "your-embedding-deployment"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"

# Azure AI Search
AZURE_SEARCH_ENDPOINT = "https://your-search-resource.search.windows.net"
AZURE_SEARCH_API_KEY = "your-search-api-key"
AZURE_SEARCH_INDEX_NAME = "your-index-name"

# Embedding size for model e.g., 1536 for text-embedding-ada-002
EMBEDDING_DIM = 1536

# Sample documents
documents = [
    {"id": "doc1", "content": "Azure AI Search is a cloud search service with vector support."},
    {"id": "doc2", "content": "OpenAI embeddings help you find similar content using vector search."}
]

# === 2. CREATE VECTOR INDEX ===


def create_vector_index():
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX_NAME}?api-version=2023-07-01-Preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_API_KEY
    }

    index_schema = {
        "name": AZURE_SEARCH_INDEX_NAME,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "content", "type": "Edm.String"},
            {
                "name": "contentVector",
                "type": "Collection(Edm.Single)",
                "dimensions": EMBEDDING_DIM,
                "vectorSearchConfiguration": "vector-config"
            }
        ],
        "vectorSearch": {
            "algorithmConfigurations": [
                {
                    "name": "vector-config",
                    "kind": "hnsw",
                    "hnswParameters": {
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine"
                    }
                }
            ]
        }
    }

    response = requests.put(url, headers=headers, json=index_schema)

    if response.status_code in [200, 201, 204]:
        print("✅ Index created or updated successfully.")
    else:
        print(f"❌ Failed to create index: {response.status_code}")
        print(response.text)
        exit(1)

# === 3. GET EMBEDDINGS ===


def get_embedding(text):
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )

    response = client.embeddings.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding

# === 4. UPLOAD DOCUMENTS WITH VECTORS ===


def upload_documents(docs):
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX_NAME}/docs/index?api-version=2023-07-01-Preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_API_KEY
    }

    payload = {"value": docs}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("📤 Documents indexed successfully!")
    else:
        print(f"❌ Failed to index documents: {response.status_code}")
        print(response.text)

# === 5. MAIN FLOW ===


def main():
    create_vector_index()

    docs_to_upload = []
    for doc in documents:
        print(f"🔍 Generating embedding for: {doc['id']}")
        vector = get_embedding(doc["content"])
        docs_to_upload.append({
            "@search.action": "upload",
            "id": doc["id"],
            "content": doc["content"],
            "contentVector": vector
        })
    upload_documents(docs_to_upload)


if __name__ == "__main__":
    main()
