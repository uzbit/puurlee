from openai import OpenAI

from pinecone import Pinecone, ServerlessSpec
from google.cloud import firestore

# import firebase_admin

from utils.Utilities import OPENAI_API_KEY, PINECONE_API_KEY
from utils.Utilities import api_key_required, CORS_HEADERS

PINECONE_INDEX = "puurlee-test"

# # Initialize the Firebase Admin SDK
# firebase_admin.initialize_app(options={"storageBucket": "puurlee.appspot.com"})

# Initialize Firestore
db = firestore.Client()

oa = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    # environment="us-west1-gcp"  # Example environment
)

# ========================== CHUNKING FUNCTION ==========================


def chunk_text(text, max_chars=500):
    """
    Simple character-based chunking.
    For large docs or production usage, consider better chunking
    by tokens or paragraphs.
    """
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        yield text[start:end]
        start = end


# ========================== OPENAI EMBEDDINGS ==========================


def get_openai_embedding(chunk):
    """
    Calls OpenAI's text-embedding-ada-002 model
    and returns the 1536-dimensional vector.
    """
    response = oa.embeddings.create(model="text-embedding-ada-002", input=chunk)
    # The actual embedding vector is in response["data"][0]["embedding"]
    return response.data[0].embedding


# ========================== PINECONE STORAGE ==========================


def store_embeddings_in_pinecone(user_id, chunk_embeddings):
    """
    Demonstrates how to store embeddings in Pinecone for robust
    vector similarity search.
    """
    index = pc.Index(PINECONE_INDEX)

    vectors_to_upsert = []
    for i, data in enumerate(chunk_embeddings):
        vector_id = f"{user_id}-chunk-{i}"
        vectors_to_upsert.append(
            {
                "id": vector_id,
                "values": data["vector"],
                "metadata": {
                    "user_id": user_id,
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
    try:
        doc_ref = db.collection("documents").document(doc_id)
        doc = doc_ref.get()

        if doc.exists:
            doc_data = doc.to_dict()
        else:
            print("No such document")
            return False
    except Exception as e:
        print(f"Error getting document: {e}")
        return False

    text = "\n".join(doc_data["content"])
    print(text)
    print(f"^^^^ {doc_id} ^^^^")

    chunk_embeddings = list()
    for c in chunk_text(text):
        e = get_openai_embedding(c)
        chunk_embeddings.append(
            {"chunk": c, "vector": e, "timestamp": firestore.SERVER_TIMESTAMP}
        )

    return chunk_embeddings


# Entry point for Google Cloud Function
def main(request):
    if request.method == "OPTIONS":
        # For preflight requests
        return ("", 204, CORS_HEADERS)

    if request.method == "POST":
        user_id = request.form.get("user_id")
        doc_id = request.form.get("doc_id")

    embeddings = create_embeddings(doc_id)
    store_embeddings_in_pinecone(user_id, embeddings)
