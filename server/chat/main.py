import datetime
from openai import OpenAI
from pinecone import Pinecone

from utils.Utilities import OPENAI_API_KEY, PINECONE_API_KEY
from utils.Utilities import api_key_required, embed_text, CORS_HEADERS

# To call service:
# curl -X POST \
#   -F "api_key=key" \
#   -F "doc_id=Akyc7QWwIbVk8rxrKaaT"
# http://localhost:8080
#   https://embeddings-286240844421.us-central1.run.app

PINECONE_INDEX = "puurlee-test"

oa = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "puurlee-test"  # the index where you stored user data
index = pc.Index(index_name)


def retrieve_relevant_chunks(user_id, query, top_k=3):
    """
    1. Create query embedding
    2. Query pinecone
    3. Return the top_k chunks
    """
    query_embedding = embed_text(oa, query)
    # Pinecone expects a single vector as a list, top_k results
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"user_id": {"$eq": user_id}},
    )

    # each match has .metadata["chunk"] if you stored your chunk text under "chunk"
    chunks = []
    for match in result["matches"]:
        chunk_text = match["metadata"].get("chunk", "")
        chunks.append(chunk_text)
    return chunks


def answer_health_question(user_id, query):
    """
    1. Retrieve relevant chunks from Pinecone
    2. Construct a chat prompt
    3. Call OpenAI to generate an answer
    """
    # 1. Retrieve relevant data from Pinecone
    relevant_chunks = retrieve_relevant_chunks(user_id, query, top_k=3)

    # 2. Construct context for the LLM
    #    We combine the relevant chunks into a single string
    context = "\n\n".join(relevant_chunks)

    # 3. Use a system message or a more advanced prompt. For example:
    system_prompt = (
        "You are a helpful health assistant with knowledge based on user-specific data.\n"
        "You are not a doctor, so provide disclaimers if uncertain.\n"
        "Use the following data to answer the user's question:\n\n"
        f"{context}\n\n"
        "If the information is insufficient or unclear, say so."
    )

    # 4. Call OpenAI ChatCompletion
    response = oa.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.7,
        max_tokens=300,
    )

    # 5. Extract the assistant’s answer
    answer = response.choices[0].message.content
    print(answer)
    return (answer, 200, CORS_HEADERS)


# Entry point for Google Cloud Function
@api_key_required
def main(request):
    if request.method == "OPTIONS":
        # For preflight requests
        return ("", 204, CORS_HEADERS)

    if request.method == "POST":
        doc_id = request.form.get("doc_id")
