import datetime
from openai import OpenAI
from pinecone import Pinecone
from google.cloud import firestore

from utils.Utilities import OPENAI_API_KEY, PINECONE_API_KEY, CORS_HEADERS
from utils.Utilities import api_key_required, embed_text, decrypt_text

# To call service:
# curl -X POST \
#   -F "api_key=key" \
#   -F "doc_id=Akyc7QWwIbVk8rxrKaaT"
# http://localhost:8080
#   https://embeddings-286240844421.us-central1.run.app

PINECONE_INDEX = "puurlee-test"

# Initialize Firestore
db = firestore.Client()

oa = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)


def chunk_lines(lines, num_lines=10):
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

    chunk_sizes = divide_number(len(lines), num_lines)
    start = 0
    for c in chunk_sizes:
        end = min(start + c, len(lines))
        yield lines[start:end]
        start = end


def store_embeddings_in_pinecone(embeddings, user_id, doc_id):
    """
    Demonstrates how to store embeddings in Pinecone for robust
    vector similarity search.
    """
    index = pc.Index(PINECONE_INDEX)
    # print(embeddings)
    vectors_to_upsert = []
    for i, data in enumerate(embeddings):
        vector_id = f"{user_id}-{doc_id}"
        vectors_to_upsert.append(
            {
                "id": vector_id,
                "values": data["vector"],
                "metadata": {
                    "user_id": user_id,
                    "doc_id": doc_id,
                    "content": data["text"],
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

    user_id = doc_data["user_id"]
    doc_text = decrypt_text(doc_data["content"])
    embedding = embed_text(oa, doc_text)
    timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
    return [
        {"text": doc_data["content"], "vector": embedding, "timestamp": timestamp}
    ], user_id


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
