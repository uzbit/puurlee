import datetime
from pathlib import Path
import configparser
from functools import wraps
from flask import jsonify
from google.cloud import firestore

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",  # Or restrict to specific domain
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "3600",
}

config = configparser.ConfigParser()
config.read(Path(__file__).parent.parent / "options.ini")
PUURLEE_API_KEY = config["Puurlee"]["api_key"]
PROJECT_ID = config["Puurlee"]["project_id"]
OPENAI_API_KEY = config["OpenAI"]["api_key"]
PINECONE_API_KEY = config["Pinecone"]["api_key"]


firestore_db = firestore.Client()


def insert_into_firestore(data):
    # Insert the structured data into Firestore
    return firestore_db.collection("documents").add(data)


def update_document_firestore(doc_id, data):
    doc_ref = firestore_db.collection("documents").document(doc_id)

    try:
        doc_ref.update(data)
        print(f"Document {doc_id} updated successfully!")
    except Exception as e:
        print(f"Error updating document {doc_id}: {e}")


# def encrypt_text(text):
#     # 1. Prepare KMS client
#     client = kms.KeyManagementServiceClient()
#     crypto_key_name = client.crypto_key_path(
#         PROJECT_ID, LOCATION, KEY_RING_ID, CRYPTO_KEY_ID
#     )

#     # 2. Encrypt plaintext
#     encrypt_response = client.encrypt(
#         request={
#             "name": crypto_key_name,
#             "plaintext": plaintext_str.encode("utf-8"),
#         }
#     )
#     ciphertext_bytes = encrypt_response.ciphertext

#     # Convert to base64 to store in Firestore
#     ciphertext_b64 = base64.b64encode(ciphertext_bytes).decode("utf-8")


def structure_data(text, storage_url, user_id, doc_type):
    timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
    structured_data = {
        "timestamp": timestamp,
        "content": text,
        "user_id": user_id,
        "data_type": doc_type,
        "storage_url": storage_url,
    }
    return structured_data


def get_user_docs_by_type(user_id, data_type):
    docs_ref = (
        firestore_db.collection("documents")
        .where("user_id", "==", user_id)
        .where("data_type", "==", data_type)
    )

    results = docs_ref.stream()

    # Should only be one conversation
    for doc in results:
        return doc


def embed_text(oa, text):
    """Get embedding vector for a text using OpenAI Embeddings."""
    response = oa.embeddings.create(model="text-embedding-ada-002", input=text)
    return response.data[0].embedding


def api_key_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        api_key = request.form.get("api_key")  # Extract API key from the request
        if api_key != PUURLEE_API_KEY:
            return (
                jsonify({"error": "Invalid API key"}),
                403,
                CORS_HEADERS,
            )  # Forbidden status
        return f(request, *args, **kwargs)  # Call the original function

    return decorated_function
