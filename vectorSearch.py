import numpy as np
from pymongo import MongoClient
from openai import AzureOpenAI

# ==== CONFIG ====
MONGODB_URI = "mongodb://<cosmos-mongo-user>:<password>@<cosmos-mongo-uri>/test?retrywrites=false"
DB_NAME = "graphrag"
COLLECTION_NAME = "documents"

AZURE_OPENAI_KEY = "<your-openai-key>"
AZURE_OPENAI_ENDPOINT = "<your-endpoint>"
DEPLOYMENT_NAME = "text-embedding-ada-002"

# ==== CONNECT TO MONGODB IN COSMOS ====
client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# ==== INIT AZURE OPENAI ====
openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2023-05-15",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)


def get_embedding(text: str) -> list:
    res = openai_client.embeddings.create(
        input=[text],
        model=DEPLOYMENT_NAME
    )
    return res.data[0].embedding


def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

# ==== STEP 1: INSERT DOCUMENTS WITH EMBEDDINGS ====


def insert_document(doc_id, text, metadata={}):
    embedding = get_embedding(text)
    document = {
        "_id": doc_id,
        "text": text,
        "embedding": embedding,
        "metadata": metadata
    }
    collection.insert_one(document)
    print(f"Inserted doc {doc_id}")

# ==== STEP 2: VECTOR SEARCH (Manual Cosine Similarity) ====


def search_similar_documents(query, top_k=5):
    query_embedding = get_embedding(query)

    results = []
    for doc in collection.find():
        score = cosine_similarity(query_embedding, doc['embedding'])
        results.append((score, doc))

    top_results = sorted(results, key=lambda x: x[0], reverse=True)[:top_k]

    print(f"\n🔍 Top {top_k} results for query: '{query}'")
    for idx, (score, doc) in enumerate(top_results):
        print(f"\nResult #{idx+1} (score={score:.4f})")
        print(f"Doc ID: {doc['_id']}")
        print(f"Text: {doc['text'][:300]}...")
        print(f"Metadata: {doc.get('metadata', {})}")

# ==== EXAMPLE USAGE ====

# 1. Insert sample
# insert_document("CR-101", "Payment gateway integration is pending review", {"type": "CR"})
# insert_document("JIRA-202", "Fix bug in checkout payment flow", {"type": "JIRA"})


# 2. Search
search_similar_documents("What are the issues in payment processing?", top_k=5)
