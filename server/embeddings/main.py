import datetime
from openai import OpenAI
from pinecone import Pinecone
from google.cloud import firestore

from utils.Utilities import OPENAI_API_KEY, PINECONE_API_KEY
from utils.Utilities import api_key_required, CORS_HEADERS

PINECONE_INDEX = "puurlee-test"

# Initialize Firestore
db = firestore.Client()

oa = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)


def chunk_text(text, target_size=500):
    def divide_number(X, N):
        base_size = X // N  # Base size for each part
        remainder = X % N  # Extra units to distribute

        # First 'remainder' parts get (base_size + 1)
        parts = [N] * base_size
        for i in range(len(parts)):
            parts[i] += remainder // base_size

        # Distribute the last remaining over parts
        for i in range(X - sum(parts)):
            parts[i] += 1

        return parts

    chunk_sizes = divide_number(len(text), target_size)
    start = 0
    for c in chunk_sizes:
        end = min(start + c, len(text))
        yield text[start:end]
        start = end


def get_openai_embedding(chunk):
    """
    Calls OpenAI's text-embedding-ada-002 model
    and returns the 1536-dimensional vector.
    """
    response = oa.embeddings.create(model="text-embedding-ada-002", input=chunk)
    # The actual embedding vector is in response["data"][0]["embedding"]
    return response.data[0].embedding


def store_embeddings_in_pinecone(embeddings, user_id, doc_id):
    """
    Demonstrates how to store embeddings in Pinecone for robust
    vector similarity search.
    """
    index = pc.Index(PINECONE_INDEX)
    # print(embeddings)
    vectors_to_upsert = []
    for i, data in enumerate(embeddings):
        vector_id = f"{user_id}-{doc_id}-chunk-{i}"
        vectors_to_upsert.append(
            {
                "id": vector_id,
                "values": data["vector"],
                "metadata": {
                    "user_id": user_id,
                    "doc_id": doc_id,
                    "chunk": data["chunk"],
                    "timestamp": data["timestamp"],
                },
            }
        )

    # Upsert to Pinecone
    index.upsert(vectors=vectors_to_upsert)
    response_body = f"Upserted {len(vectors_to_upsert)} vectors to Pinecone index '{PINECONE_INDEX}'."
    print(response_body)
    return (response_body, 200, CORS_HEADERS)


def create_embeddings(doc_id):
    doc_ref = db.collection("documents").document(doc_id)
    doc = doc_ref.get()

    if doc.exists:
        doc_data = doc.to_dict()
    else:
        raise Exception("No such document")

    text = "\n".join(doc_data["content"])
    user_id = doc_data["user_id"]

    # print(text)
    # print(f"^^^^ {doc_id} ^^^^")

    chunk_embeddings = list()
    timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
    for c in chunk_text(text):
        e = get_openai_embedding(c)
        chunk_embeddings.append({"chunk": c, "vector": e, "timestamp": timestamp})

    return chunk_embeddings, user_id


# Entry point for Google Cloud Function
@api_key_required
def main(request):
    if request.method == "OPTIONS":
        # For preflight requests
        return ("", 204, CORS_HEADERS)

    if request.method == "POST":
        doc_id = request.form.get("doc_id")

    embeddings, user_id = create_embeddings(doc_id)
    return store_embeddings_in_pinecone(embeddings, user_id, doc_id)
